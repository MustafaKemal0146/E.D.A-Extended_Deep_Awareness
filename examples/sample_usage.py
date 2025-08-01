"""
Sample usage examples for E.D.A MCP Tool
"""
import asyncio
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_ingestion import DataIngestionEngine
from core.preprocessing import PreprocessingPipeline
from core.analysis import DeepAnalysisEngine
from core.visualization import VisualizationHub
from core.insights import InsightGenerator


async def create_sample_data():
    """Create sample dataset for demonstration"""
    np.random.seed(42)
    
    # Generate sample sales data
    n_samples = 1000
    
    data = {
        'date': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
        'sales': np.random.normal(1000, 200, n_samples) + np.sin(np.arange(n_samples) * 2 * np.pi / 365) * 100,
        'marketing_spend': np.random.normal(500, 100, n_samples),
        'temperature': np.random.normal(20, 10, n_samples),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], n_samples),
        'customer_satisfaction': np.random.uniform(1, 5, n_samples)
    }
    
    # Add some correlations
    data['sales'] = data['sales'] + data['marketing_spend'] * 0.5 + np.random.normal(0, 50, n_samples)
    
    # Add some missing values
    missing_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    for idx in missing_indices:
        data['customer_satisfaction'][idx] = np.nan
    
    df = pd.DataFrame(data)
    df.to_csv('sample_sales_data.csv', index=False)
    return df


async def basic_analysis_example():
    """Example of basic EDA workflow"""
    print("=== E.D.A Basic Analysis Example ===\n")
    
    # Create sample data
    df = await create_sample_data()
    print(f"Created sample dataset with {df.shape[0]} rows and {df.shape[1]} columns\n")
    
    # Initialize components
    data_engine = DataIngestionEngine()
    preprocessor = PreprocessingPipeline()
    analyzer = DeepAnalysisEngine()
    visualizer = VisualizationHub()
    insight_generator = InsightGenerator()
    
    # Load data
    print("1. Loading data...")
    loaded_data = data_engine.load_data('sample_sales_data.csv')
    data_info = data_engine.get_data_info(loaded_data)
    print(f"   Data loaded: {data_info['shape'][0]} rows, {data_info['shape'][1]} columns")
    print(f"   Missing values: {sum(data_info['missing_values'].values())}\n")
    
    # Preprocess data
    print("2. Preprocessing data...")
    clean_data = preprocessor.clean_data(loaded_data)
    processed_data = preprocessor.handle_missing_values(clean_data)
    encoded_data = preprocessor.encode_categorical(processed_data)
    
    transformations = preprocessor.get_transformation_summary()
    print("   Transformations applied:")
    for transformation in transformations:
        print(f"   • {transformation}")
    print()
    
    # Statistical analysis
    print("3. Performing statistical analysis...")
    statistical_results = analyzer.statistical_analysis(encoded_data)
    
    if 'correlations' in statistical_results:
        strong_corrs = statistical_results['correlations'].get('strong_correlations', [])
        if strong_corrs:
            print(f"   Found {len(strong_corrs)} strong correlations")
            strongest = strong_corrs[0]
            print(f"   Strongest: {strongest['variable1']} ↔ {strongest['variable2']} (r={strongest['correlation']:.3f})")
    print()
    
    # Clustering analysis
    print("4. Performing clustering analysis...")
    clustering_results = analyzer.clustering_analysis(encoded_data)
    
    if 'kmeans' in clustering_results:
        n_clusters = clustering_results['kmeans']['n_clusters']
        print(f"   K-means identified {n_clusters} clusters")
    
    if 'dbscan' in clustering_results:
        noise_points = clustering_results['dbscan']['n_noise_points']
        print(f"   DBSCAN found {noise_points} outlier points")
    print()
    
    # Feature importance analysis
    print("5. Analyzing feature importance...")
    fi_results = analyzer.feature_importance_analysis(encoded_data, 'sales')
    
    if 'top_features' in fi_results:
        top_features = fi_results['top_features'][:3]
        print(f"   Top 3 predictive features: {', '.join(top_features)}")
        
        performance = fi_results.get('performance', {})
        if 'r2_score' in performance:
            print(f"   Model R² score: {performance['r2_score']:.3f}")
    print()
    
    # Create visualizations
    print("6. Creating visualizations...")
    
    # Correlation heatmap
    corr_plot = visualizer.create_correlation_heatmap(encoded_data)
    if 'error' not in corr_plot:
        print("   ✓ Correlation heatmap created")
    
    # Distribution plots
    dist_plots = visualizer.create_distribution_plots(encoded_data)
    if 'error' not in dist_plots:
        print("   ✓ Distribution plots created")
    
    # Box plots
    box_plots = visualizer.create_box_plots(encoded_data, 'region')
    if 'error' not in box_plots:
        print("   ✓ Box plots created")
    
    # Time series plot
    ts_plot = visualizer.create_time_series_plot(loaded_data, 'date', 'sales')
    if 'error' not in ts_plot:
        print("   ✓ Time series plot created")
    
    # Cluster visualization
    if 'kmeans' in clustering_results:
        cluster_labels = clustering_results['kmeans']['labels']
        cluster_plot = visualizer.create_cluster_visualization(encoded_data, cluster_labels)
        if 'error' not in cluster_plot:
            print("   ✓ Cluster visualization created")
    
    # Feature importance plot
    if 'feature_importance' in fi_results:
        fi_plot = visualizer.create_feature_importance_plot(fi_results['feature_importance'])
        if 'error' not in fi_plot:
            print("   ✓ Feature importance plot created")
    print()
    
    # Generate insights
    print("7. Generating insights...")
    analysis_results = {
        'statistical': statistical_results,
        'clustering': clustering_results,
        'feature_importance': fi_results
    }
    
    insights = insight_generator.generate_comprehensive_insights(
        encoded_data, analysis_results, "sales analysis"
    )
    
    print("   Executive Summary:")
    for insight in insights.get('executive_summary', []):
        print(f"   • {insight}")
    print()
    
    print("   Top Recommendations:")
    for rec in insights.get('recommendations', [])[:3]:
        print(f"   • {rec['recommendation']} ({rec['priority']} priority)")
    print()
    
    # Generate report
    print("8. Generating comprehensive report...")
    report = insight_generator.generate_natural_language_report(insights)
    
    # Save report
    with open('eda_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("   ✓ Report saved as 'eda_analysis_report.md'")
    print()
    
    # Q&A example
    print("9. Q&A Examples:")
    questions = [
        "How many rows are in the dataset?",
        "What are the strongest correlations?",
        "How many clusters were found?",
        "Are there any outliers?"
    ]
    
    for question in questions:
        answer = insight_generator.ask_question(question, encoded_data, analysis_results)
        print(f"   Q: {question}")
        print(f"   A: {answer}\n")
    
    print("=== Analysis Complete! ===")
    print("Check the generated files:")
    print("• sample_sales_data.csv - Sample dataset")
    print("• eda_analysis_report.md - Comprehensive analysis report")


async def mcp_server_example():
    """Example of using the MCP server"""
    print("=== MCP Server Usage Example ===\n")
    
    print("To use the EDA tool as an MCP server:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the server: python src/mcp_server.py")
    print("3. Connect from your LLM client\n")
    
    print("Available MCP tools:")
    tools = [
        "load_data - Load data from various sources",
        "preprocess_data - Clean and preprocess data",
        "analyze_data - Perform comprehensive analysis",
        "create_visualizations - Generate interactive plots",
        "ask_question - Ask natural language questions",
        "generate_report - Create detailed reports"
    ]
    
    for tool in tools:
        print(f"• {tool}")
    print()
    
    print("Example MCP tool call:")
    example_call = {
        "name": "analyze_data",
        "parameters": {
            "analysis_depth": "deep",
            "target_column": "sales",
            "business_context": "retail sales analysis"
        }
    }
    print(f"{example_call}")


if __name__ == "__main__":
    print("E.D.A - Extended Deep Awareness Tool Examples\n")
    
    # Run basic analysis example
    asyncio.run(basic_analysis_example())
    
    print("\n" + "="*50 + "\n")
    
    # Show MCP server example
    asyncio.run(mcp_server_example())