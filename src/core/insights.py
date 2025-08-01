"""
Insight Generator - LLM-powered insights and recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json


class InsightGenerator:
    """Generate actionable insights from analysis results"""
    
    def __init__(self):
        self.insights = {}
        self.recommendations = {}
    
    def generate_comprehensive_insights(self, df: pd.DataFrame, 
                                      analysis_results: Dict[str, Any],
                                      business_context: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights from all analysis results
        
        Args:
            df: Original dataframe
            analysis_results: Results from various analyses
            business_context: Optional business context for targeted insights
            
        Returns:
            Dictionary containing comprehensive insights
        """
        insights = {
            'data_overview': self._generate_data_overview_insights(df),
            'statistical_insights': self._generate_statistical_insights(analysis_results.get('statistical', {})),
            'pattern_insights': self._generate_pattern_insights(analysis_results),
            'quality_insights': self._generate_data_quality_insights(df),
            'recommendations': self._generate_recommendations(df, analysis_results, business_context)
        }
        
        # Generate executive summary
        insights['executive_summary'] = self._generate_executive_summary(insights)
        
        self.insights = insights
        return insights
    
    def _generate_data_overview_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insights about the dataset overview"""
        insights = []
        
        # Basic dataset info
        insights.append(f"Dataset contains {df.shape[0]:,} rows and {df.shape[1]} columns")
        
        # Column types breakdown
        numerical_cols = len(df.select_dtypes(include=[np.number]).columns)
        categorical_cols = len(df.select_dtypes(include=['object', 'category']).columns)
        datetime_cols = len(df.select_dtypes(include=['datetime64']).columns)
        
        insights.append(f"Column types: {numerical_cols} numerical, {categorical_cols} categorical, {datetime_cols} datetime")
        
        # Memory usage
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        insights.append(f"Dataset memory usage: {memory_mb:.1f} MB")
        
        # Missing data overview
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 0:
            insights.append(f"Missing data: {missing_pct:.1f}% of all values")
        else:
            insights.append("No missing values detected")
        
        return insights
    
    def _generate_statistical_insights(self, statistical_results: Dict[str, Any]) -> List[str]:
        """Generate insights from statistical analysis"""
        insights = []
        
        if not statistical_results:
            return ["No statistical analysis results available"]
        
        # Distribution insights
        if 'distribution_tests' in statistical_results:
            normal_cols = []
            skewed_cols = []
            
            for col, test_result in statistical_results['distribution_tests'].items():
                if test_result.get('is_normal', False):
                    normal_cols.append(col)
                elif abs(test_result.get('skewness', 0)) > 1:
                    skewed_cols.append((col, test_result.get('skewness', 0)))
            
            if normal_cols:
                insights.append(f"Normally distributed variables: {', '.join(normal_cols[:3])}")
            
            if skewed_cols:
                most_skewed = max(skewed_cols, key=lambda x: abs(x[1]))
                insights.append(f"Most skewed variable: {most_skewed[0]} (skewness: {most_skewed[1]:.2f})")
        
        # Correlation insights
        if 'correlations' in statistical_results:
            strong_corrs = statistical_results['correlations'].get('strong_correlations', [])
            if strong_corrs:
                strongest = strong_corrs[0]
                insights.append(f"Strongest correlation: {strongest['variable1']} ↔ {strongest['variable2']} (r={strongest['correlation']:.3f})")
                
                if len(strong_corrs) > 1:
                    insights.append(f"Found {len(strong_corrs)} strong correlations (|r| > 0.7)")
        
        # Hypothesis test insights
        if 'hypothesis_tests' in statistical_results:
            significant_tests = [
                test for test, result in statistical_results['hypothesis_tests'].items()
                if result.get('significant', False)
            ]
            
            if significant_tests:
                insights.append(f"Significant relationships found: {len(significant_tests)} variable pairs")
        
        return insights
    
    def _generate_pattern_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate insights about patterns in the data"""
        insights = []
        
        # Clustering insights
        if 'clustering' in analysis_results:
            clustering_results = analysis_results['clustering']
            
            if 'kmeans' in clustering_results:
                n_clusters = clustering_results['kmeans']['n_clusters']
                insights.append(f"K-means identified {n_clusters} distinct clusters in the data")
                
                # Cluster size distribution
                cluster_sizes = clustering_results['kmeans']['cluster_sizes']
                largest_cluster = max(cluster_sizes.values())
                smallest_cluster = min(cluster_sizes.values())
                
                if largest_cluster / smallest_cluster > 3:
                    insights.append("Clusters are imbalanced - some groups are much larger than others")
            
            if 'dbscan' in clustering_results:
                dbscan_results = clustering_results['dbscan']
                noise_points = dbscan_results.get('n_noise_points', 0)
                if noise_points > 0:
                    insights.append(f"DBSCAN identified {noise_points} outlier/noise points")
        
        # Feature importance insights
        if 'feature_importance' in analysis_results:
            fi_results = analysis_results['feature_importance']
            top_features = fi_results.get('top_features', [])
            
            if top_features:
                insights.append(f"Most predictive feature: {top_features[0]}")
                
                if len(top_features) >= 3:
                    insights.append(f"Top 3 predictive features: {', '.join(top_features[:3])}")
        
        # Time series insights
        if 'time_series' in analysis_results:
            ts_results = analysis_results['time_series']
            
            if 'basic_stats' in ts_results:
                trend = ts_results['basic_stats'].get('trend', 'unknown')
                insights.append(f"Time series shows {trend} trend")
            
            if 'seasonality' in ts_results:
                seasonality = ts_results['seasonality']
                if seasonality.get('has_weekly_pattern', False):
                    insights.append("Weekly seasonal pattern detected")
                if seasonality.get('has_monthly_pattern', False):
                    insights.append("Monthly seasonal pattern detected")
        
        return insights
    
    def _generate_data_quality_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insights about data quality"""
        insights = []
        
        # Missing data patterns
        missing_by_col = df.isnull().sum()
        high_missing_cols = missing_by_col[missing_by_col > len(df) * 0.1].index.tolist()
        
        if high_missing_cols:
            insights.append(f"Columns with >10% missing data: {', '.join(high_missing_cols[:3])}")
        
        # Duplicate analysis
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            insights.append(f"Duplicate rows: {duplicates} ({dup_pct:.1f}%)")
        
        # Constant columns
        constant_cols = []
        for col in df.columns:
            if df[col].nunique() <= 1:
                constant_cols.append(col)
        
        if constant_cols:
            insights.append(f"Constant columns (no variation): {', '.join(constant_cols)}")
        
        # High cardinality categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        high_cardinality_cols = []
        
        for col in categorical_cols:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.5:  # More than 50% unique values
                high_cardinality_cols.append(col)
        
        if high_cardinality_cols:
            insights.append(f"High cardinality categorical columns: {', '.join(high_cardinality_cols)}")
        
        return insights
    
    def _generate_recommendations(self, df: pd.DataFrame, analysis_results: Dict[str, Any],
                                business_context: str = None) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        missing_by_col = df.isnull().sum()
        high_missing_cols = missing_by_col[missing_by_col > len(df) * 0.1]
        
        if len(high_missing_cols) > 0:
            recommendations.append({
                'category': 'Data Quality',
                'priority': 'High',
                'recommendation': f"Address missing data in columns: {', '.join(high_missing_cols.index[:3])}",
                'action': 'Consider imputation strategies or investigate data collection process'
            })
        
        # Feature engineering recommendations
        if 'correlations' in analysis_results.get('statistical', {}):
            strong_corrs = analysis_results['statistical']['correlations'].get('strong_correlations', [])
            if len(strong_corrs) > 2:
                recommendations.append({
                    'category': 'Feature Engineering',
                    'priority': 'Medium',
                    'recommendation': 'Consider dimensionality reduction due to high correlations',
                    'action': 'Apply PCA or remove redundant features to reduce multicollinearity'
                })
        
        # Modeling recommendations
        if 'feature_importance' in analysis_results:
            fi_results = analysis_results['feature_importance']
            task_type = fi_results.get('task_type', 'unknown')
            
            if task_type == 'classification':
                performance = fi_results.get('performance', {})
                accuracy = performance.get('accuracy', 0)
                
                if accuracy < 0.8:
                    recommendations.append({
                        'category': 'Model Performance',
                        'priority': 'High',
                        'recommendation': f'Model accuracy is {accuracy:.2%} - consider feature engineering',
                        'action': 'Try feature selection, polynomial features, or ensemble methods'
                    })
        
        # Clustering recommendations
        if 'clustering' in analysis_results:
            clustering_results = analysis_results['clustering']
            
            if 'dbscan' in clustering_results:
                noise_points = clustering_results['dbscan'].get('n_noise_points', 0)
                if noise_points > len(df) * 0.05:  # More than 5% noise
                    recommendations.append({
                        'category': 'Outlier Analysis',
                        'priority': 'Medium',
                        'recommendation': f'{noise_points} outliers detected ({noise_points/len(df)*100:.1f}%)',
                        'action': 'Investigate outliers - they may represent important edge cases or data errors'
                    })
        
        # Business context recommendations
        if business_context:
            if 'sales' in business_context.lower():
                recommendations.append({
                    'category': 'Business Intelligence',
                    'priority': 'High',
                    'recommendation': 'Focus on seasonal patterns and customer segmentation',
                    'action': 'Analyze sales trends by time periods and customer demographics'
                })
            elif 'customer' in business_context.lower():
                recommendations.append({
                    'category': 'Business Intelligence',
                    'priority': 'High',
                    'recommendation': 'Implement customer lifetime value analysis',
                    'action': 'Segment customers based on behavior and predict churn risk'
                })
        
        return recommendations
    
    def _generate_executive_summary(self, insights: Dict[str, Any]) -> List[str]:
        """Generate executive summary of key findings"""
        summary = []
        
        # Data overview
        data_overview = insights.get('data_overview', [])
        if data_overview:
            summary.append(data_overview[0])  # Dataset size info
        
        # Key statistical finding
        statistical_insights = insights.get('statistical_insights', [])
        if statistical_insights:
            summary.append(statistical_insights[0])  # Most important statistical insight
        
        # Key pattern finding
        pattern_insights = insights.get('pattern_insights', [])
        if pattern_insights:
            summary.append(pattern_insights[0])  # Most important pattern
        
        # Top recommendation
        recommendations = insights.get('recommendations', [])
        high_priority_recs = [r for r in recommendations if r.get('priority') == 'High']
        if high_priority_recs:
            summary.append(f"Priority action: {high_priority_recs[0]['recommendation']}")
        
        return summary
    
    def generate_natural_language_report(self, insights: Dict[str, Any]) -> str:
        """Generate a natural language report from insights"""
        report_sections = []
        
        # Executive Summary
        report_sections.append("## Executive Summary")
        exec_summary = insights.get('executive_summary', [])
        for item in exec_summary:
            report_sections.append(f"• {item}")
        
        # Data Overview
        report_sections.append("\n## Data Overview")
        data_overview = insights.get('data_overview', [])
        for item in data_overview:
            report_sections.append(f"• {item}")
        
        # Key Findings
        report_sections.append("\n## Key Statistical Findings")
        statistical_insights = insights.get('statistical_insights', [])
        for item in statistical_insights:
            report_sections.append(f"• {item}")
        
        # Patterns and Trends
        report_sections.append("\n## Patterns and Trends")
        pattern_insights = insights.get('pattern_insights', [])
        for item in pattern_insights:
            report_sections.append(f"• {item}")
        
        # Data Quality Assessment
        report_sections.append("\n## Data Quality Assessment")
        quality_insights = insights.get('quality_insights', [])
        for item in quality_insights:
            report_sections.append(f"• {item}")
        
        # Recommendations
        report_sections.append("\n## Recommendations")
        recommendations = insights.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report_sections.append(f"{i}. **{rec['category']}** ({rec['priority']} Priority)")
            report_sections.append(f"   {rec['recommendation']}")
            report_sections.append(f"   *Action:* {rec['action']}")
        
        return "\n".join(report_sections)
    
    def ask_question(self, question: str, df: pd.DataFrame, 
                    analysis_results: Dict[str, Any]) -> str:
        """
        Answer natural language questions about the data
        
        Args:
            question: Natural language question
            df: Original dataframe
            analysis_results: Analysis results
            
        Returns:
            Natural language answer
        """
        question_lower = question.lower()
        
        # Simple pattern matching for common questions
        if 'how many' in question_lower and ('row' in question_lower or 'record' in question_lower):
            return f"The dataset contains {df.shape[0]:,} rows/records."
        
        elif 'how many' in question_lower and 'column' in question_lower:
            return f"The dataset has {df.shape[1]} columns."
        
        elif 'missing' in question_lower or 'null' in question_lower:
            missing_total = df.isnull().sum().sum()
            missing_pct = (missing_total / (df.shape[0] * df.shape[1])) * 100
            return f"There are {missing_total:,} missing values ({missing_pct:.1f}% of all data)."
        
        elif 'correlation' in question_lower:
            if 'statistical' in analysis_results and 'correlations' in analysis_results['statistical']:
                strong_corrs = analysis_results['statistical']['correlations'].get('strong_correlations', [])
                if strong_corrs:
                    strongest = strong_corrs[0]
                    return f"The strongest correlation is between {strongest['variable1']} and {strongest['variable2']} (r={strongest['correlation']:.3f})."
                else:
                    return "No strong correlations (|r| > 0.7) were found in the data."
            else:
                return "Correlation analysis has not been performed yet."
        
        elif 'cluster' in question_lower:
            if 'clustering' in analysis_results:
                kmeans_results = analysis_results['clustering'].get('kmeans', {})
                n_clusters = kmeans_results.get('n_clusters', 0)
                return f"K-means clustering identified {n_clusters} distinct groups in the data."
            else:
                return "Clustering analysis has not been performed yet."
        
        elif 'outlier' in question_lower:
            if 'clustering' in analysis_results and 'dbscan' in analysis_results['clustering']:
                noise_points = analysis_results['clustering']['dbscan'].get('n_noise_points', 0)
                return f"DBSCAN identified {noise_points} outlier points ({noise_points/len(df)*100:.1f}% of data)."
            else:
                return "Outlier analysis has not been performed yet."
        
        else:
            return "I can answer questions about data size, missing values, correlations, clusters, and outliers. Please rephrase your question or run the appropriate analysis first."
    
    def get_insights_summary(self) -> Dict[str, Any]:
        """Get summary of all generated insights"""
        return self.insights.copy()