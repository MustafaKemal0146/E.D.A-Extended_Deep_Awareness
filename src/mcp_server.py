"""
MCP Server Implementation for E.D.A Tool
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import pandas as pd

from core.data_ingestion import DataIngestionEngine
from core.preprocessing import PreprocessingPipeline
from core.analysis import DeepAnalysisEngine
from core.visualization import VisualizationHub
from core.insights import InsightGenerator


class EDAMCPServer:
    """MCP Server for Extended Deep Awareness analysis"""
    
    def __init__(self):
        self.server = Server("eda-extended-deep-awareness")
        self.data_engine = DataIngestionEngine()
        self.preprocessor = PreprocessingPipeline()
        self.analyzer = DeepAnalysisEngine()
        self.visualizer = VisualizationHub()
        self.insight_generator = InsightGenerator()
        
        # Current session data
        self.current_data = None
        self.analysis_results = {}
        
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="load_data",
                    description="Load data from various sources (CSV, JSON, SQL, S3, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Data source path or connection string"
                            },
                            "source_type": {
                                "type": "string",
                                "enum": ["auto", "csv", "json", "parquet", "sql", "s3"],
                                "default": "auto",
                                "description": "Type of data source"
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional options for data loading"
                            }
                        },
                        "required": ["source"]
                    }
                ),
                Tool(
                    name="analyze_data",
                    description="Perform comprehensive EDA analysis on loaded data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_depth": {
                                "type": "string",
                                "enum": ["basic", "intermediate", "deep"],
                                "default": "intermediate",
                                "description": "Depth of analysis to perform"
                            },
                            "target_column": {
                                "type": "string",
                                "description": "Target column for supervised analysis (optional)"
                            },
                            "business_context": {
                                "type": "string",
                                "description": "Business context for targeted insights"
                            }
                        }
                    }
                ),
                Tool(
                    name="create_visualizations",
                    description="Generate interactive visualizations from the data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plot_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["correlation", "distribution", "scatter_matrix", "box_plots", "time_series"]
                                },
                                "description": "Types of plots to generate"
                            },
                            "categorical_column": {
                                "type": "string",
                                "description": "Categorical column for grouping (optional)"
                            },
                            "date_column": {
                                "type": "string",
                                "description": "Date column for time series analysis (optional)"
                            },
                            "value_column": {
                                "type": "string",
                                "description": "Value column for time series analysis (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="ask_question",
                    description="Ask natural language questions about the data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Natural language question about the data"
                            }
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="generate_report",
                    description="Generate comprehensive analysis report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "html", "json"],
                                "default": "markdown",
                                "description": "Report format"
                            },
                            "include_visualizations": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include visualizations in report"
                            }
                        }
                    }
                ),
                Tool(
                    name="preprocess_data",
                    description="Clean and preprocess the loaded data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "remove_duplicates": {
                                "type": "boolean",
                                "default": True,
                                "description": "Remove duplicate rows"
                            },
                            "handle_missing": {
                                "type": "string",
                                "enum": ["auto", "mean", "median", "mode", "knn"],
                                "default": "auto",
                                "description": "Strategy for handling missing values"
                            },
                            "handle_outliers": {
                                "type": "string",
                                "enum": ["none", "iqr", "zscore", "isolation_forest"],
                                "default": "iqr",
                                "description": "Method for handling outliers"
                            },
                            "encode_categorical": {
                                "type": "string",
                                "enum": ["auto", "onehot", "label"],
                                "default": "auto",
                                "description": "Method for encoding categorical variables"
                            },
                            "scale_features": {
                                "type": "string",
                                "enum": ["none", "standard", "minmax"],
                                "default": "none",
                                "description": "Feature scaling method"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "load_data":
                    return await self._load_data(arguments)
                elif name == "analyze_data":
                    return await self._analyze_data(arguments)
                elif name == "create_visualizations":
                    return await self._create_visualizations(arguments)
                elif name == "ask_question":
                    return await self._ask_question(arguments)
                elif name == "generate_report":
                    return await self._generate_report(arguments)
                elif name == "preprocess_data":
                    return await self._preprocess_data(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]
    
    async def _load_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Load data from specified source"""
        source = arguments["source"]
        source_type = arguments.get("source_type", "auto")
        options = arguments.get("options", {})
        
        try:
            self.current_data = self.data_engine.load_data(source, source_type, **options)
            data_info = self.data_engine.get_data_info(self.current_data)
            
            # Convert dtypes to string for JSON serialization
            dtypes_str = {col: str(dtype) for col, dtype in data_info['dtypes'].items()}
            
            response = f"""Data loaded successfully!

**Dataset Information:**
- Shape: {data_info['shape'][0]:,} rows × {data_info['shape'][1]} columns
- Memory usage: {data_info['memory_usage'] / 1024 / 1024:.1f} MB
- Missing values: {sum(data_info['missing_values'].values()):,}
- Duplicate rows: {data_info['duplicate_rows']:,}

**Column Types:**
{json.dumps(dtypes_str, indent=2)}

Data is ready for analysis!"""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error loading data: {str(e)}")]
    
    async def _preprocess_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Preprocess the loaded data"""
        if self.current_data is None:
            return [TextContent(type="text", text="No data loaded. Please load data first.")]
        
        try:
            # Apply preprocessing steps
            processed_data = self.current_data.copy()
            
            # Clean data
            if arguments.get("remove_duplicates", True) or arguments.get("handle_outliers", "iqr") != "none":
                processed_data = self.preprocessor.clean_data(
                    processed_data,
                    remove_duplicates=arguments.get("remove_duplicates", True),
                    handle_outliers=arguments.get("handle_outliers", "iqr") if arguments.get("handle_outliers") != "none" else None
                )
            
            # Handle missing values
            if arguments.get("handle_missing", "auto") != "none":
                processed_data = self.preprocessor.handle_missing_values(
                    processed_data,
                    strategy=arguments.get("handle_missing", "auto")
                )
            
            # Encode categorical variables
            if arguments.get("encode_categorical", "auto") != "none":
                processed_data = self.preprocessor.encode_categorical(
                    processed_data,
                    method=arguments.get("encode_categorical", "auto")
                )
            
            # Scale features
            if arguments.get("scale_features", "none") != "none":
                processed_data = self.preprocessor.scale_features(
                    processed_data,
                    method=arguments.get("scale_features")
                )
            
            # Update current data
            original_shape = self.current_data.shape
            self.current_data = processed_data
            new_shape = processed_data.shape
            
            # Get transformation summary
            transformations = self.preprocessor.get_transformation_summary()
            
            response = f"""Data preprocessing completed!

**Changes:**
- Original shape: {original_shape[0]:,} rows × {original_shape[1]} columns
- New shape: {new_shape[0]:,} rows × {new_shape[1]} columns

**Transformations applied:**
"""
            for transformation in transformations:
                response += f"• {transformation}\n"
            
            response += "\nData is now ready for analysis!"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error preprocessing data: {str(e)}")]
    
    async def _analyze_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Perform comprehensive data analysis"""
        if self.current_data is None:
            return [TextContent(type="text", text="No data loaded. Please load data first.")]
        
        try:
            analysis_depth = arguments.get("analysis_depth", "intermediate")
            target_column = arguments.get("target_column")
            business_context = arguments.get("business_context")
            
            # Perform different analyses based on depth
            if analysis_depth in ["basic", "intermediate", "deep"]:
                # Statistical analysis
                self.analysis_results["statistical"] = self.analyzer.statistical_analysis(self.current_data)
                
                # Clustering analysis
                self.analysis_results["clustering"] = self.analyzer.clustering_analysis(self.current_data)
            
            if analysis_depth in ["intermediate", "deep"] and target_column:
                # Feature importance analysis
                self.analysis_results["feature_importance"] = self.analyzer.feature_importance_analysis(
                    self.current_data, target_column
                )
            
            if analysis_depth == "deep":
                # Time series analysis (if applicable)
                date_columns = self.current_data.select_dtypes(include=['datetime64']).columns
                numerical_columns = self.current_data.select_dtypes(include=['number']).columns
                
                if len(date_columns) > 0 and len(numerical_columns) > 0:
                    self.analysis_results["time_series"] = self.analyzer.time_series_analysis(
                        self.current_data, date_columns[0], numerical_columns[0]
                    )
            
            # Generate insights
            insights = self.insight_generator.generate_comprehensive_insights(
                self.current_data, self.analysis_results, business_context
            )
            
            # Create summary response
            response = f"""Analysis completed! ({analysis_depth} level)

**Executive Summary:**
"""
            for insight in insights.get("executive_summary", []):
                response += f"• {insight}\n"
            
            response += f"""
**Key Statistical Findings:**
"""
            for insight in insights.get("statistical_insights", [])[:3]:
                response += f"• {insight}\n"
            
            response += f"""
**Pattern Insights:**
"""
            for insight in insights.get("pattern_insights", [])[:3]:
                response += f"• {insight}\n"
            
            response += f"""
**Top Recommendations:**
"""
            for rec in insights.get("recommendations", [])[:3]:
                response += f"• {rec['recommendation']} ({rec['priority']} priority)\n"
            
            response += "\nUse 'generate_report' to get the full detailed analysis!"
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error analyzing data: {str(e)}")]
    
    async def _create_visualizations(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Create visualizations"""
        if self.current_data is None:
            return [TextContent(type="text", text="No data loaded. Please load data first.")]
        
        try:
            plot_types = arguments.get("plot_types", ["correlation", "distribution"])
            categorical_column = arguments.get("categorical_column")
            date_column = arguments.get("date_column")
            value_column = arguments.get("value_column")
            
            created_plots = []
            
            for plot_type in plot_types:
                if plot_type == "correlation":
                    plot_data = self.visualizer.create_correlation_heatmap(self.current_data)
                    if "error" not in plot_data:
                        created_plots.append("Correlation heatmap")
                
                elif plot_type == "distribution":
                    plot_data = self.visualizer.create_distribution_plots(self.current_data)
                    if "error" not in plot_data:
                        created_plots.append("Distribution plots")
                
                elif plot_type == "scatter_matrix":
                    plot_data = self.visualizer.create_scatter_matrix(self.current_data)
                    if "error" not in plot_data:
                        created_plots.append("Scatter plot matrix")
                
                elif plot_type == "box_plots":
                    plot_data = self.visualizer.create_box_plots(self.current_data, categorical_column)
                    if "error" not in plot_data:
                        created_plots.append("Box plots")
                
                elif plot_type == "time_series" and date_column and value_column:
                    plot_data = self.visualizer.create_time_series_plot(
                        self.current_data, date_column, value_column
                    )
                    if "error" not in plot_data:
                        created_plots.append("Time series plot")
            
            # Add clustering visualization if clustering analysis was performed
            if "clustering" in self.analysis_results:
                kmeans_labels = self.analysis_results["clustering"].get("kmeans", {}).get("labels", [])
                if kmeans_labels:
                    plot_data = self.visualizer.create_cluster_visualization(
                        self.current_data, kmeans_labels
                    )
                    if "error" not in plot_data:
                        created_plots.append("Cluster visualization")
            
            # Add feature importance plot if available
            if "feature_importance" in self.analysis_results:
                feature_importance = self.analysis_results["feature_importance"].get("feature_importance", [])
                if feature_importance:
                    plot_data = self.visualizer.create_feature_importance_plot(feature_importance)
                    if "error" not in plot_data:
                        created_plots.append("Feature importance plot")
            
            response = f"""Visualizations created successfully!

**Generated plots:**
"""
            for plot in created_plots:
                response += f"• {plot}\n"
            
            response += f"""
Total plots created: {len(created_plots)}

Use 'generate_report' with include_visualizations=true to get the plots in your report!"""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating visualizations: {str(e)}")]
    
    async def _ask_question(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Answer natural language questions about the data"""
        if self.current_data is None:
            return [TextContent(type="text", text="No data loaded. Please load data first.")]
        
        question = arguments["question"]
        
        try:
            answer = self.insight_generator.ask_question(
                question, self.current_data, self.analysis_results
            )
            
            return [TextContent(type="text", text=f"**Question:** {question}\n\n**Answer:** {answer}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error answering question: {str(e)}")]
    
    async def _generate_report(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Generate comprehensive analysis report"""
        if self.current_data is None:
            return [TextContent(type="text", text="No data loaded. Please load data first.")]
        
        try:
            format_type = arguments.get("format", "markdown")
            include_visualizations = arguments.get("include_visualizations", True)
            
            # Get insights if not already generated
            if not hasattr(self.insight_generator, 'insights') or not self.insight_generator.insights:
                insights = self.insight_generator.generate_comprehensive_insights(
                    self.current_data, self.analysis_results
                )
            else:
                insights = self.insight_generator.get_insights_summary()
            
            if format_type == "markdown":
                report = self.insight_generator.generate_natural_language_report(insights)
                
                if include_visualizations:
                    report += "\n\n## Visualizations\n"
                    plots = self.visualizer.get_all_plots()
                    for plot_name, plot_data in plots.items():
                        report += f"\n### {plot_name.replace('_', ' ').title()}\n"
                        for insight in plot_data.get('insights', []):
                            report += f"• {insight}\n"
                
                return [TextContent(type="text", text=report)]
            
            elif format_type == "json":
                report_data = {
                    "insights": insights,
                    "analysis_results": self.analysis_results,
                    "data_info": self.data_engine.get_data_info(self.current_data)
                }
                
                if include_visualizations:
                    report_data["visualizations"] = self.visualizer.export_plots("html")
                
                return [TextContent(type="text", text=json.dumps(report_data, indent=2, default=str))]
            
            elif format_type == "html":
                markdown_report = self.insight_generator.generate_natural_language_report(insights)
                # Simple markdown to HTML conversion
                html_report = markdown_report.replace("## ", "<h2>").replace("\n", "<br>\n")
                html_report = f"<html><body>{html_report}</body></html>"
                
                return [TextContent(type="text", text=html_report)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error generating report: {str(e)}")]
    
    async def run(self, transport_type: str = "stdio"):
        """Run the MCP server"""
        if transport_type == "stdio":
            from mcp.server.stdio import stdio_server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main():
    """Main entry point"""
    server = EDAMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())