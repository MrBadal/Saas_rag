"""
Auto-Visualization Service
Generates chart recommendations based on query results
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    TABLE = "table"
    NONE = "none"

@dataclass
class ChartRecommendation:
    chart_type: ChartType
    title: str
    description: str
    x_column: Optional[str]
    y_column: Optional[str]
    data_mapping: Dict[str, Any]
    confidence: float

class Visualizer:
    """
    Analyzes query results and recommends appropriate visualizations
    
    Supports:
    - Line charts (time series)
    - Bar charts (categorical comparisons)
    - Pie charts (proportions)
    - Scatter plots (correlations)
    - Data tables (raw data)
    """
    
    def __init__(self):
        self.min_rows_for_chart = 2
        self.max_rows_for_pie = 10
    
    def recommend_visualization(self, results: List[Dict], 
                               query: str = "") -> ChartRecommendation:
        """
        Analyze results and recommend best visualization
        
        Args:
            results: Query results
            query: Original query text (for context)
            
        Returns:
            ChartRecommendation with type and configuration
        """
        if not results or len(results) < self.min_rows_for_chart:
            return ChartRecommendation(
                chart_type=ChartType.TABLE,
                title="Query Results",
                description="Results displayed as table",
                x_column=None,
                y_column=None,
                data_mapping={},
                confidence=1.0
            )
        
        # Analyze result structure
        columns = list(results[0].keys())
        column_types = self._analyze_column_types(results, columns)
        
        # Determine chart type
        chart_type = self._determine_chart_type(results, columns, column_types, query)
        
        # Map data to chart
        data_mapping = self._map_data_to_chart(results, columns, column_types, chart_type)
        
        return ChartRecommendation(
            chart_type=chart_type,
            title=self._generate_title(query, chart_type),
            description=self._generate_description(chart_type, columns),
            x_column=data_mapping.get("x_column"),
            y_column=data_mapping.get("y_column"),
            data_mapping=data_mapping,
            confidence=0.85
        )
    
    def generate_plotly_config(self, recommendation: ChartRecommendation, 
                               results: List[Dict]) -> Dict[str, Any]:
        """
        Generate Plotly configuration for the recommended chart
        
        Returns:
            Plotly figure configuration as dict
        """
        chart_type = recommendation.chart_type
        
        if chart_type == ChartType.LINE:
            return self._generate_line_chart(results, recommendation)
        elif chart_type == ChartType.BAR:
            return self._generate_bar_chart(results, recommendation)
        elif chart_type == ChartType.PIE:
            return self._generate_pie_chart(results, recommendation)
        elif chart_type == ChartType.SCATTER:
            return self._generate_scatter_chart(results, recommendation)
        else:
            return self._generate_table(results, recommendation)
    
    def _analyze_column_types(self, results: List[Dict], 
                             columns: List[str]) -> Dict[str, str]:
        """Analyze data types of columns"""
        types = {}
        
        for col in columns:
            values = [row.get(col) for row in results if row.get(col) is not None]
            
            if not values:
                types[col] = "unknown"
                continue
            
            # Check if date/time
            if any(self._is_datetime(str(v)) for v in values[:5]):
                types[col] = "datetime"
            # Check if numeric
            elif all(self._is_numeric(v) for v in values[:10]):
                types[col] = "numeric"
            # Check if categorical (few unique values)
            elif len(set(str(v) for v in values)) <= min(len(values) * 0.5, 20):
                types[col] = "categorical"
            else:
                types[col] = "text"
        
        return types
    
    def _determine_chart_type(self, results: List[Dict], columns: List[str],
                             column_types: Dict[str, str], query: str) -> ChartType:
        """Determine best chart type based on data"""
        
        # Time series detection
        date_cols = [c for c, t in column_types.items() if t == "datetime"]
        numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
        categorical_cols = [c for c, t in column_types.items() if t == "categorical"]
        
        # Line chart: Time series with numeric values
        if date_cols and numeric_cols:
            return ChartType.LINE
        
        # Pie chart: Single categorical with numeric (few categories)
        if (len(categorical_cols) == 1 and len(numeric_cols) == 1 and 
            len(results) <= self.max_rows_for_pie):
            return ChartType.PIE
        
        # Bar chart: Categorical comparison
        if categorical_cols and numeric_cols:
            return ChartType.BAR
        
        # Scatter: Two numeric columns
        if len(numeric_cols) >= 2:
            return ChartType.SCATTER
        
        # Default to table
        return ChartType.TABLE
    
    def _map_data_to_chart(self, results: List[Dict], columns: List[str],
                          column_types: Dict[str, str], 
                          chart_type: ChartType) -> Dict[str, Any]:
        """Map data columns to chart axes"""
        
        date_cols = [c for c, t in column_types.items() if t == "datetime"]
        numeric_cols = [c for c, t in column_types.items() if t == "numeric"]
        categorical_cols = [c for c, t in column_types.items() if t == "categorical"]
        
        mapping = {}
        
        if chart_type == ChartType.LINE:
            mapping["x_column"] = date_cols[0] if date_cols else columns[0]
            mapping["y_column"] = numeric_cols[0] if numeric_cols else columns[1]
        
        elif chart_type == ChartType.BAR:
            mapping["x_column"] = categorical_cols[0] if categorical_cols else columns[0]
            mapping["y_column"] = numeric_cols[0] if numeric_cols else columns[1]
        
        elif chart_type == ChartType.PIE:
            mapping["label_column"] = categorical_cols[0] if categorical_cols else columns[0]
            mapping["value_column"] = numeric_cols[0] if numeric_cols else columns[1]
        
        elif chart_type == ChartType.SCATTER:
            mapping["x_column"] = numeric_cols[0]
            mapping["y_column"] = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        return mapping
    
    def _generate_line_chart(self, results: List[Dict], 
                            rec: ChartRecommendation) -> Dict[str, Any]:
        """Generate Plotly line chart config"""
        x_col = rec.x_column or list(results[0].keys())[0]
        y_col = rec.y_column or list(results[0].keys())[1]
        
        return {
            "data": [{
                "x": [row.get(x_col) for row in results],
                "y": [row.get(y_col) for row in results],
                "type": "scatter",
                "mode": "lines+markers",
                "name": y_col
            }],
            "layout": {
                "title": rec.title,
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col}
            }
        }
    
    def _generate_bar_chart(self, results: List[Dict], 
                           rec: ChartRecommendation) -> Dict[str, Any]:
        """Generate Plotly bar chart config"""
        x_col = rec.x_column or list(results[0].keys())[0]
        y_col = rec.y_column or list(results[0].keys())[1]
        
        return {
            "data": [{
                "x": [row.get(x_col) for row in results],
                "y": [row.get(y_col) for row in results],
                "type": "bar",
                "name": y_col
            }],
            "layout": {
                "title": rec.title,
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col}
            }
        }
    
    def _generate_pie_chart(self, results: List[Dict], 
                           rec: ChartRecommendation) -> Dict[str, Any]:
        """Generate Plotly pie chart config"""
        mapping = rec.data_mapping
        label_col = mapping.get("label_column", list(results[0].keys())[0])
        value_col = mapping.get("value_column", list(results[0].keys())[1])
        
        return {
            "data": [{
                "labels": [row.get(label_col) for row in results],
                "values": [row.get(value_col) for row in results],
                "type": "pie",
                "hole": 0.3
            }],
            "layout": {
                "title": rec.title
            }
        }
    
    def _generate_scatter_chart(self, results: List[Dict], 
                               rec: ChartRecommendation) -> Dict[str, Any]:
        """Generate Plotly scatter chart config"""
        x_col = rec.x_column or list(results[0].keys())[0]
        y_col = rec.y_column or list(results[0].keys())[1]
        
        return {
            "data": [{
                "x": [row.get(x_col) for row in results],
                "y": [row.get(y_col) for row in results],
                "type": "scatter",
                "mode": "markers",
                "name": f"{y_col} vs {x_col}"
            }],
            "layout": {
                "title": rec.title,
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col}
            }
        }
    
    def _generate_table(self, results: List[Dict], 
                       rec: ChartRecommendation) -> Dict[str, Any]:
        """Generate data table config"""
        columns = list(results[0].keys()) if results else []
        
        return {
            "data": [{
                "type": "table",
                "header": {
                    "values": columns,
                    "fill": {"color": "#f8f9fa"},
                    "align": "left"
                },
                "cells": {
                    "values": [[row.get(col) for row in results] for col in columns],
                    "align": "left"
                }
            }],
            "layout": {
                "title": rec.title
            }
        }
    
    def _is_datetime(self, value: str) -> bool:
        """Check if string looks like datetime"""
        import re
        patterns = [
            r'^\d{4}-\d{2}-\d{2}',  # ISO date
            r'^\d{2}/\d{2}/\d{4}',   # US date
            r'^\d{2}-\d{2}-\d{4}',   # EU date
        ]
        return any(re.match(p, value) for p in patterns)
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric"""
        if isinstance(value, (int, float)):
            return True
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _generate_title(self, query: str, chart_type: ChartType) -> str:
        """Generate chart title from query"""
        if not query:
            return f"{chart_type.value.title()} Chart"
        
        # Clean up query for title
        title = query.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title
    
    def _generate_description(self, chart_type: ChartType, columns: List[str]) -> str:
        """Generate chart description"""
        descriptions = {
            ChartType.LINE: f"Time series showing trends over time",
            ChartType.BAR: f"Comparison across categories",
            ChartType.PIE: f"Distribution of values",
            ChartType.SCATTER: f"Correlation between variables",
            ChartType.TABLE: f"Detailed results table"
        }
        return descriptions.get(chart_type, "Data visualization")

# Convenience function
def create_visualizer() -> Visualizer:
    """Factory function to create visualizer"""
    return Visualizer()
