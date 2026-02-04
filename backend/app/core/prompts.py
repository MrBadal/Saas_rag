"""
Optimized Prompts for SQL Generation
Research-backed prompt engineering for better accuracy
"""

# Few-shot examples for PostgreSQL
POSTGRESQL_EXAMPLES = """
EXAMPLES:

User: "Show me all users"
Query: SELECT * FROM users LIMIT 100;

User: "Get the latest 10 orders"
Query: SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;

User: "How many customers do we have?"
Query: SELECT COUNT(*) as total_customers FROM customers;

User: "Find orders from last month"
Query: SELECT * FROM orders WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND created_at < DATE_TRUNC('month', CURRENT_DATE);

User: "Show top 5 products by price"
Query: SELECT * FROM products ORDER BY price DESC LIMIT 5;

User: "Get customers who made purchases"
Query: SELECT DISTINCT c.* FROM customers c INNER JOIN orders o ON c.id = o.customer_id;
"""

# Few-shot examples for MongoDB
MONGODB_EXAMPLES = """
EXAMPLES:

User: "Show me all users"
Query: {"collection": "users", "filter": {}, "limit": 100}

User: "Get the latest 10 orders"
Query: {"collection": "orders", "filter": {}, "sort": {"created_at": -1}, "limit": 10}

User: "How many customers do we have?"
Query: {"collection": "customers", "operation": "count"}

User: "Find orders from last month"
Query: {"collection": "orders", "filter": {"created_at": {"$gte": "DATE_LAST_MONTH_START", "$lt": "DATE_CURRENT_MONTH_START"}}}

User: "Show top 5 products by price"
Query: {"collection": "products", "filter": {}, "sort": {"price": -1}, "limit": 5}

User: "Get customers who made purchases"
Query: {"collection": "orders", "filter": {}, "distinct": "customer_id"}
"""

# Base prompt template
QUERY_GENERATION_TEMPLATE = """You are an expert database assistant specializing in {db_type}.

Generate a {db_type} query based on the user's request.

{examples}

DATABASE SCHEMA:
{schema}

CRITICAL RULES:
1. Generate ONLY SELECT statements (read-only queries)
2. Use exact table and column names from the schema
3. Add LIMIT 100 if no limit is specified by the user
4. For PostgreSQL:
   - Use proper SQL syntax
   - Use ILIKE for case-insensitive text searches
   - Use JSON operators (->, ->>) for JSON columns
   - Use DATE_TRUNC for date aggregations
5. For MongoDB:
   - Return valid JSON format only
   - Use proper MongoDB operators ($gte, $lte, $in, etc.)
   - Include collection name in the query
6. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER statements
7. Ensure all referenced columns exist in the schema
8. Use proper JOIN syntax for related tables

TABLE RELATIONSHIPS:
{relationships}

USER REQUEST: {user_query}

Return ONLY the query without any explanation or markdown formatting."""

# RAG QA Prompt
RAG_QA_TEMPLATE = """You are a helpful database assistant. Answer the user's question based on the database schema and context provided.

CONTEXT:
{context}

SCHEMA INFORMATION:
{schema}

USER QUESTION: {question}

Instructions:
- Provide clear, concise answers
- Reference specific tables and columns when relevant
- If suggesting a query, mention it's a suggestion only
- Be helpful and professional
- If you don't have enough information, say so

Answer:"""

# Query validation prompt
QUERY_VALIDATION_TEMPLATE = """Validate and fix this {db_type} query if needed.

Original Query:
{query}

Schema Context:
{schema}

Rules:
1. Fix any syntax errors
2. Ensure all table/column names exist in schema
3. Add LIMIT if missing
4. Convert to proper {db_type} dialect
5. Ensure it's a read-only SELECT statement

If the query is valid, return it as-is.
If it needs fixes, return the corrected query.

Return ONLY the corrected query, no explanation:"""

# System prompts for different providers
OPENAI_SYSTEM_PROMPT = """You are an expert database assistant specializing in SQL and NoSQL queries.
Your task is to generate accurate, read-only database queries based on user requests.
Always follow the schema provided and generate only SELECT statements.
Be precise with table names, column names, and query syntax."""

GEMINI_SYSTEM_PROMPT = """You are a database query expert. Generate accurate queries based on user requests and schema information.
Only generate SELECT statements. Use exact table and column names from the schema.
Return only the query without explanations."""

def get_query_generation_prompt(db_type: str, schema: str, user_query: str, relationships: str = "") -> str:
    """Generate optimized prompt for query generation"""
    examples = POSTGRESQL_EXAMPLES if db_type == "postgresql" else MONGODB_EXAMPLES
    
    return QUERY_GENERATION_TEMPLATE.format(
        db_type=db_type,
        examples=examples,
        schema=schema,
        relationships=relationships if relationships else "No explicit relationships defined.",
        user_query=user_query
    )

def get_rag_qa_prompt(context: str, schema: str, question: str) -> str:
    """Generate RAG QA prompt"""
    return RAG_QA_TEMPLATE.format(
        context=context,
        schema=schema,
        question=question
    )

def get_validation_prompt(db_type: str, query: str, schema: str) -> str:
    """Generate query validation prompt"""
    return QUERY_VALIDATION_TEMPLATE.format(
        db_type=db_type,
        query=query,
        schema=schema
    )
