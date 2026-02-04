"""
LangGraph Self-Correcting SQL Agent
Generator-Critic pattern for robust query generation
"""

from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.prompts import get_query_generation_prompt, get_validation_prompt
from app.utils.query_cleaner import clean_query
from app.services.query_validator import QueryValidator
import json
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State maintained across agent workflow"""
    user_query: str
    schema: Dict[str, Any]
    db_type: str
    iteration: int
    generated_query: str
    validation_result: Optional[Dict]
    execution_error: Optional[str]
    final_query: Optional[str]
    thinking_steps: List[str]
    is_valid: bool

class SQLAgent:
    """
    Self-correcting SQL agent using LangGraph
    
    Workflow:
    1. Generator: Create initial query
    2. Validator: Check syntax and safety
    3. Critic: Evaluate and suggest fixes
    4. Retry: If errors found, go back to Generator with feedback
    5. Complete: Return final validated query
    """
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        self.llm_config = llm_config or {}
        self.provider = self.llm_config.get('provider', 'openai')
        self.api_key = self.llm_config.get('api_key')
        self.model = self.llm_config.get('model')
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        self.query_validator = QueryValidator()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("SQLAgent initialized with LangGraph workflow")
    
    def _initialize_llm(self):
        """Initialize LLM for agent"""
        if self.provider == 'google':
            return ChatGoogleGenerativeAI(
                model=self.model or "gemini-1.5-flash",
                google_api_key=self.api_key,
                temperature=0,
                convert_system_message_to_human=True
            )
        else:
            return ChatOpenAI(
                model=self.model or "gpt-3.5-turbo",
                temperature=0,
                openai_api_key=self.api_key
            )
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Define workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("generator", self._generator_node)
        workflow.add_node("validator", self._validator_node)
        workflow.add_node("critic", self._critic_node)
        
        # Define edges
        workflow.set_entry_point("generator")
        workflow.add_edge("generator", "validator")
        
        # Conditional edge from validator
        workflow.add_conditional_edges(
            "validator",
            self._should_retry,
            {
                "retry": "critic",
                "complete": END
            }
        )
        
        # Critic always goes back to generator for retry
        workflow.add_edge("critic", "generator")
        
        return workflow.compile()
    
    def _generator_node(self, state: AgentState) -> AgentState:
        """Generate or regenerate query"""
        iteration = state["iteration"]
        user_query = state["user_query"]
        schema = state["schema"]
        db_type = state["db_type"]
        
        logger.info(f"Generator iteration {iteration + 1}")
        
        # Build prompt
        if iteration == 0:
            # First attempt
            prompt = get_query_generation_prompt(
                db_type=db_type,
                schema=json.dumps(schema, indent=2),
                user_query=user_query,
                relationships=self._extract_relationships(schema)
            )
        else:
            # Retry with feedback
            error_feedback = state.get("execution_error") or ""
            validation_feedback = ""
            if state.get("validation_result"):
                validation_feedback = "\n".join(state["validation_result"].get("errors", []))
            
            prompt = f"""Fix the following {db_type} query based on the errors:

Original Request: {user_query}

Previous Query Attempt:
{state.get('generated_query', '')}

Errors Found:
{error_feedback}
{validation_feedback}

Schema:
{json.dumps(schema, indent=2)}

Rules:
- Fix all syntax errors
- Use exact table and column names from schema
- Generate only SELECT statements
- Add LIMIT 100 if missing
- Return only the corrected query, no explanation

Corrected Query:"""
        
        # Generate query
        try:
            response = self.llm.invoke(prompt)
            raw_query = response.content if hasattr(response, 'content') else str(response)
            
            # Clean query
            cleaned_query, _ = clean_query(raw_query, db_type)
            
            # Update state
            state["generated_query"] = cleaned_query
            state["iteration"] = iteration + 1
            state["thinking_steps"].append(f"Iteration {iteration + 1}: Generated query")
            
        except Exception as e:
            logger.error(f"Generator failed: {e}")
            state["execution_error"] = str(e)
        
        return state
    
    def _validator_node(self, state: AgentState) -> AgentState:
        """Validate generated query"""
        query = state.get("generated_query", "")
        db_type = state["db_type"]
        
        logger.info(f"Validating query: {query[:100]}...")
        
        if not query:
            state["validation_result"] = {
                "is_valid": False,
                "errors": ["Empty query generated"]
            }
            state["is_valid"] = False
            return state
        
        # Validate based on db_type
        if db_type == "postgresql":
            result = self.query_validator.validate(query, db_type)
            state["validation_result"] = {
                "is_valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings
            }
            state["is_valid"] = result.is_valid
            
            if result.is_valid:
                state["final_query"] = result.normalized_query
                state["thinking_steps"].append("Validation passed")
            else:
                state["thinking_steps"].append(f"Validation failed: {', '.join(result.errors)}")
        
        elif db_type == "mongodb":
            # Validate JSON
            try:
                json.loads(query)
                state["validation_result"] = {"is_valid": True, "errors": []}
                state["is_valid"] = True
                state["final_query"] = query
                state["thinking_steps"].append("Validation passed")
            except json.JSONDecodeError as e:
                state["validation_result"] = {
                    "is_valid": False,
                    "errors": [f"Invalid JSON: {str(e)}"]
                }
                state["is_valid"] = False
                state["thinking_steps"].append(f"Validation failed: Invalid JSON")
        
        return state
    
    def _critic_node(self, state: AgentState) -> AgentState:
        """Critique and provide feedback for retry"""
        errors = state.get("validation_result", {}).get("errors", [])
        
        logger.info(f"Critic analyzing {len(errors)} errors")
        
        # Build error feedback
        error_feedback = "\n".join(errors)
        state["execution_error"] = error_feedback
        state["thinking_steps"].append(f"Critique: {error_feedback}")
        
        return state
    
    def _should_retry(self, state: AgentState) -> str:
        """Decide whether to retry or complete"""
        is_valid = state.get("is_valid", False)
        iteration = state["iteration"]
        max_iterations = 3
        
        if is_valid:
            logger.info("Query valid, completing workflow")
            return "complete"
        elif iteration >= max_iterations:
            logger.warning(f"Max iterations ({max_iterations}) reached")
            return "complete"
        else:
            logger.info(f"Retrying, iteration {iteration}")
            return "retry"
    
    def generate_query(self, user_query: str, schema: Dict[str, Any], 
                       db_type: str) -> Dict[str, Any]:
        """
        Generate query using agent workflow
        
        Returns:
            Dict with query, success status, and thinking steps
        """
        # Initialize state
        initial_state: AgentState = {
            "user_query": user_query,
            "schema": schema,
            "db_type": db_type,
            "iteration": 0,
            "generated_query": "",
            "validation_result": None,
            "execution_error": None,
            "final_query": None,
            "thinking_steps": [],
            "is_valid": False
        }
        
        try:
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "query": final_state.get("final_query") or final_state.get("generated_query", ""),
                "success": final_state.get("is_valid", False),
                "iterations": final_state.get("iteration", 0),
                "thinking_steps": final_state.get("thinking_steps", []),
                "errors": final_state.get("validation_result", {}).get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Agent workflow failed: {e}")
            return {
                "query": "",
                "success": False,
                "iterations": 0,
                "thinking_steps": ["Workflow failed"],
                "errors": [str(e)]
            }
    
    def _extract_relationships(self, schema: Dict[str, Any]) -> str:
        """Extract foreign key relationships"""
        relationships = []
        
        for table_name, columns in schema.items():
            if isinstance(columns, list):
                for col in columns:
                    if col.get('foreign_key'):
                        fk = col['foreign_key']
                        rel = f"{table_name}.{col['name']} → {fk.get('referred_table')}.{fk.get('referred_columns', ['id'])[0]}"
                        relationships.append(rel)
        
        return "\n".join(relationships) if relationships else "No explicit relationships defined."

# Convenience function
def create_sql_agent(llm_config: Dict[str, Any] = None) -> SQLAgent:
    """Factory function to create SQL agent"""
    return SQLAgent(llm_config)
