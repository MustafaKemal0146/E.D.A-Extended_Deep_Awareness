"""
Command Line Interface for E.D.A Tool
"""
import argparse
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.data_ingestion import DataIngestionEngine
from core.preprocessing import PreprocessingPipeline
from core.analysis import DeepAnalysisEngine
from core.visualization import VisualizationHub
from core.insights import InsightGenerator


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="E.D.A - Extended Deep Awareness Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py analyze data.csv --depth deep --target sales
  python cli.py analyze data.csv --output report.md --visualizations
  python cli.py server  # Start MCP server
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze dataset')
    analyze_parser.add_argument('data_source', help='Path to data file or connection string')
    analyze_parser.add_argument('--depth', choices=['basic', 'intermediate', 'deep'], 
                               default='intermediate', help='Analysis depth')
    analyze_parser.add_argument('--target', help='Target column for supervised analysis')
    analyze_parser.add_argument('--output', help='Output file for report')
    analyze_parser.add_argument('--format', choices=['markdown', 'html', 'json'], 
                               default='markdown', help='Report format')
    analyze_parser.add_argument('--visualizations', action='store_true', 
                               help='Include visualizations in report')
    analyze_parser.add_argument('--context', help='Business context for insights')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start MCP server')
    server_parser.add_argument('--port', type=int, default=8000, help='Server port')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show dataset information')
    info_parser.add_argument('data_source', help='Path to data file')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        asyncio.run(analyze_command(args))
    elif args.command == 'server':
        asyncio.run(server_command(args))
    elif args.command == 'info':
        asyncio.run(info_command(args))
    else:
        parser.print_help()


async def analyze_command(args):
    """Execute analyze command"""
    print(f"🔍 Analyzing {args.data_source}...")
    
    try:
        # Initialize components
        data_engine = DataIngestionEngine()
        preprocessor = PreprocessingPipeline()
        analyzer = DeepAnalysisEngine()
        visualizer = VisualizationHub()
        insight_generator = InsightGenerator()
        
        # Load data
        print("📊 Loading data...")
        df = data_engine.load_data(args.data_source)
        print(f"   Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
        
        # Preprocess
        print("🧹 Preprocessing data...")
        clean_data = preprocessor.clean_data(df)
        processed_data = preprocessor.handle_missing_values(clean_data)
        final_data = preprocessor.encode_categorical(processed_data)
        
        transformations = preprocessor.get_transformation_summary()
        for t in transformations:
            print(f"   • {t}")
        
        # Analyze
        print(f"🔬 Performing {args.depth} analysis...")
        analysis_results = {}
        
        # Statistical analysis
        analysis_results['statistical'] = analyzer.statistical_analysis(final_data)
        print("   ✓ Statistical analysis complete")
        
        # Clustering
        analysis_results['clustering'] = analyzer.clustering_analysis(final_data)
        print("   ✓ Clustering analysis complete")
        
        # Feature importance (if target specified)
        if args.target and args.target in final_data.columns:
            analysis_results['feature_importance'] = analyzer.feature_importance_analysis(
                final_data, args.target
            )
            print("   ✓ Feature importance analysis complete")
        
        # Time series (if deep analysis)
        if args.depth == 'deep':
            date_cols = df.select_dtypes(include=['datetime64']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            
            if len(date_cols) > 0 and len(num_cols) > 0:
                analysis_results['time_series'] = analyzer.time_series_analysis(
                    df, date_cols[0], num_cols[0]
                )
                print("   ✓ Time series analysis complete")
        
        # Generate visualizations
        if args.visualizations:
            print("📈 Creating visualizations...")
            visualizer.create_correlation_heatmap(final_data)
            visualizer.create_distribution_plots(final_data)
            visualizer.create_box_plots(final_data)
            
            if 'clustering' in analysis_results:
                labels = analysis_results['clustering'].get('kmeans', {}).get('labels', [])
                if labels:
                    visualizer.create_cluster_visualization(final_data, labels)
            
            if 'feature_importance' in analysis_results:
                fi_data = analysis_results['feature_importance'].get('feature_importance', [])
                if fi_data:
                    visualizer.create_feature_importance_plot(fi_data)
            
            print("   ✓ Visualizations created")
        
        # Generate insights
        print("💡 Generating insights...")
        insights = insight_generator.generate_comprehensive_insights(
            final_data, analysis_results, args.context
        )
        
        # Create report
        report = insight_generator.generate_natural_language_report(insights)
        
        # Output report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved to {args.output}")
        else:
            print("\n" + "="*50)
            print("ANALYSIS REPORT")
            print("="*50)
            print(report)
        
        # Show executive summary
        print("\n🎯 Executive Summary:")
        for insight in insights.get('executive_summary', []):
            print(f"   • {insight}")
        
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


async def server_command(args):
    """Execute server command"""
    print(f"🚀 Starting MCP server on port {args.port}...")
    
    try:
        from mcp_server import EDAMCPServer
        server = EDAMCPServer()
        await server.run()
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        sys.exit(1)


async def info_command(args):
    """Execute info command"""
    print(f"ℹ️  Dataset Information: {args.data_source}")
    
    try:
        data_engine = DataIngestionEngine()
        df = data_engine.load_data(args.data_source)
        data_info = data_engine.get_data_info(df)
        
        print(f"\n📊 Basic Information:")
        print(f"   Shape: {data_info['shape'][0]:,} rows × {data_info['shape'][1]} columns")
        print(f"   Memory: {data_info['memory_usage'] / 1024 / 1024:.1f} MB")
        print(f"   Missing values: {sum(data_info['missing_values'].values()):,}")
        print(f"   Duplicates: {data_info['duplicate_rows']:,}")
        
        print(f"\n📋 Column Information:")
        for col, dtype in data_info['dtypes'].items():
            missing = data_info['missing_values'][col]
            print(f"   {col:<20} {str(dtype):<15} ({missing} missing)")
        
        print(f"\n🔍 Sample Data:")
        print(df.head().to_string())
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()