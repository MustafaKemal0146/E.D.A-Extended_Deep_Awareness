"""
Visualization Hub - Interactive charts and plots
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Union
import base64
import io


class VisualizationHub:
    """Generate interactive and static visualizations"""
    
    def __init__(self):
        self.plots = {}
        self.plot_configs = {
            'theme': 'plotly_white',
            'color_palette': px.colors.qualitative.Set3
        }
    
    def create_correlation_heatmap(self, df: pd.DataFrame, title: str = "Correlation Matrix") -> Dict[str, Any]:
        """Create interactive correlation heatmap"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'error': 'Need at least 2 numerical columns for correlation heatmap'}
        
        corr_matrix = df[numerical_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            template=self.plot_configs['theme'],
            width=600,
            height=600
        )
        
        plot_data = {
            'type': 'correlation_heatmap',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': self._generate_correlation_insights(corr_matrix)
        }
        
        self.plots['correlation_heatmap'] = plot_data
        return plot_data
    
    def create_distribution_plots(self, df: pd.DataFrame, max_cols: int = 6) -> Dict[str, Any]:
        """Create distribution plots for numerical columns"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns[:max_cols]
        
        if len(numerical_cols) == 0:
            return {'error': 'No numerical columns found'}
        
        n_cols = min(3, len(numerical_cols))
        n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, 
            cols=n_cols,
            subplot_titles=numerical_cols,
            vertical_spacing=0.08
        )
        
        for i, col in enumerate(numerical_cols):
            row = i // n_cols + 1
            col_pos = i % n_cols + 1
            
            # Histogram
            fig.add_trace(
                go.Histogram(
                    x=df[col].dropna(),
                    name=col,
                    showlegend=False,
                    opacity=0.7
                ),
                row=row, col=col_pos
            )
        
        fig.update_layout(
            title="Distribution of Numerical Variables",
            template=self.plot_configs['theme'],
            height=300 * n_rows,
            showlegend=False
        )
        
        plot_data = {
            'type': 'distribution_plots',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': self._generate_distribution_insights(df[numerical_cols])
        }
        
        self.plots['distribution_plots'] = plot_data
        return plot_data
    
    def create_scatter_matrix(self, df: pd.DataFrame, max_cols: int = 5) -> Dict[str, Any]:
        """Create interactive scatter plot matrix"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns[:max_cols]
        
        if len(numerical_cols) < 2:
            return {'error': 'Need at least 2 numerical columns for scatter matrix'}
        
        fig = px.scatter_matrix(
            df[numerical_cols],
            title="Scatter Plot Matrix",
            template=self.plot_configs['theme']
        )
        
        fig.update_traces(diagonal_visible=False)
        fig.update_layout(height=600)
        
        plot_data = {
            'type': 'scatter_matrix',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': ['Scatter matrix shows pairwise relationships between numerical variables']
        }
        
        self.plots['scatter_matrix'] = plot_data
        return plot_data
    
    def create_box_plots(self, df: pd.DataFrame, categorical_col: str = None, 
                        max_numerical_cols: int = 4) -> Dict[str, Any]:
        """Create box plots for numerical variables, optionally grouped by categorical"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns[:max_numerical_cols]
        
        if len(numerical_cols) == 0:
            return {'error': 'No numerical columns found'}
        
        if categorical_col and categorical_col not in df.columns:
            categorical_col = None
        
        n_cols = min(2, len(numerical_cols))
        n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=numerical_cols,
            vertical_spacing=0.1
        )
        
        for i, col in enumerate(numerical_cols):
            row = i // n_cols + 1
            col_pos = i % n_cols + 1
            
            if categorical_col:
                for j, category in enumerate(df[categorical_col].unique()[:8]):  # Limit categories
                    data = df[df[categorical_col] == category][col].dropna()
                    fig.add_trace(
                        go.Box(
                            y=data,
                            name=f"{category}",
                            showlegend=(i == 0)  # Only show legend for first subplot
                        ),
                        row=row, col=col_pos
                    )
            else:
                fig.add_trace(
                    go.Box(
                        y=df[col].dropna(),
                        name=col,
                        showlegend=False
                    ),
                    row=row, col=col_pos
                )
        
        title = f"Box Plots by {categorical_col}" if categorical_col else "Box Plots"
        fig.update_layout(
            title=title,
            template=self.plot_configs['theme'],
            height=300 * n_rows
        )
        
        plot_data = {
            'type': 'box_plots',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': self._generate_boxplot_insights(df, numerical_cols, categorical_col)
        }
        
        self.plots['box_plots'] = plot_data
        return plot_data
    
    def create_cluster_visualization(self, df: pd.DataFrame, cluster_labels: List[int], 
                                   method: str = 'pca') -> Dict[str, Any]:
        """Create cluster visualization using PCA or t-SNE"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'error': 'Need at least 2 numerical columns for cluster visualization'}
        
        X = df[numerical_cols].fillna(df[numerical_cols].mean())
        
        if method == 'pca':
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2)
            X_reduced = reducer.fit_transform(X)
            explained_var = reducer.explained_variance_ratio_.sum()
            method_info = f"PCA (explains {explained_var:.1%} variance)"
        else:
            # Fallback to first two columns if t-SNE not available
            X_reduced = X.iloc[:, :2].values
            method_info = "First two numerical columns"
        
        fig = px.scatter(
            x=X_reduced[:, 0],
            y=X_reduced[:, 1],
            color=[str(label) for label in cluster_labels],
            title=f"Cluster Visualization - {method_info}",
            labels={'x': 'Component 1', 'y': 'Component 2', 'color': 'Cluster'},
            template=self.plot_configs['theme']
        )
        
        plot_data = {
            'type': 'cluster_visualization',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': [
                f"Visualization shows {len(set(cluster_labels))} distinct clusters",
                f"Dimensionality reduction method: {method_info}"
            ]
        }
        
        self.plots['cluster_visualization'] = plot_data
        return plot_data
    
    def create_time_series_plot(self, df: pd.DataFrame, date_column: str, 
                               value_column: str, title: str = None) -> Dict[str, Any]:
        """Create interactive time series plot"""
        if date_column not in df.columns or value_column not in df.columns:
            return {'error': 'Date or value column not found'}
        
        # Prepare data
        ts_df = df[[date_column, value_column]].copy()
        ts_df[date_column] = pd.to_datetime(ts_df[date_column])
        ts_df = ts_df.sort_values(date_column).dropna()
        
        if len(ts_df) == 0:
            return {'error': 'No valid data points for time series'}
        
        fig = px.line(
            ts_df,
            x=date_column,
            y=value_column,
            title=title or f"Time Series: {value_column}",
            template=self.plot_configs['theme']
        )
        
        # Add trend line
        fig.add_scatter(
            x=ts_df[date_column],
            y=ts_df[value_column].rolling(window=min(30, len(ts_df)//4)).mean(),
            mode='lines',
            name='Trend',
            line=dict(dash='dash', color='red')
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=value_column,
            hovermode='x unified'
        )
        
        plot_data = {
            'type': 'time_series',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': self._generate_timeseries_insights(ts_df, value_column)
        }
        
        self.plots['time_series'] = plot_data
        return plot_data
    
    def create_feature_importance_plot(self, feature_importance: List[Dict], 
                                     top_n: int = 15) -> Dict[str, Any]:
        """Create feature importance visualization"""
        if not feature_importance:
            return {'error': 'No feature importance data provided'}
        
        # Take top N features
        top_features = feature_importance[:top_n]
        
        fig = px.bar(
            x=[item['importance'] for item in top_features],
            y=[item['feature'] for item in top_features],
            orientation='h',
            title=f"Top {len(top_features)} Feature Importance",
            labels={'x': 'Importance', 'y': 'Features'},
            template=self.plot_configs['theme']
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=max(400, len(top_features) * 25)
        )
        
        plot_data = {
            'type': 'feature_importance',
            'figure': fig,
            'html': fig.to_html(include_plotlyjs='cdn'),
            'insights': [
                f"Top feature: {top_features[0]['feature']} (importance: {top_features[0]['importance']:.3f})",
                f"Showing {len(top_features)} most important features"
            ]
        }
        
        self.plots['feature_importance'] = plot_data
        return plot_data
    
    def _generate_correlation_insights(self, corr_matrix: pd.DataFrame) -> List[str]:
        """Generate insights from correlation matrix"""
        insights = []
        
        # Find strongest correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if not np.isnan(corr_val):
                    correlations.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_val
                    ))
        
        if correlations:
            correlations.sort(key=lambda x: abs(x[2]), reverse=True)
            strongest = correlations[0]
            insights.append(f"Strongest correlation: {strongest[0]} vs {strongest[1]} (r={strongest[2]:.3f})")
            
            strong_corrs = [c for c in correlations if abs(c[2]) > 0.7]
            if strong_corrs:
                insights.append(f"Found {len(strong_corrs)} strong correlations (|r| > 0.7)")
        
        return insights
    
    def _generate_distribution_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insights from distribution analysis"""
        insights = []
        
        for col in df.columns:
            skewness = df[col].skew()
            if abs(skewness) > 1:
                skew_type = "right-skewed" if skewness > 0 else "left-skewed"
                insights.append(f"{col} is {skew_type} (skewness: {skewness:.2f})")
        
        return insights
    
    def _generate_boxplot_insights(self, df: pd.DataFrame, numerical_cols: List[str], 
                                  categorical_col: str = None) -> List[str]:
        """Generate insights from box plots"""
        insights = []
        
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)][col]
            
            if len(outliers) > 0:
                outlier_pct = len(outliers) / len(df) * 100
                insights.append(f"{col} has {len(outliers)} outliers ({outlier_pct:.1f}% of data)")
        
        return insights
    
    def _generate_timeseries_insights(self, df: pd.DataFrame, value_column: str) -> List[str]:
        """Generate insights from time series analysis"""
        insights = []
        
        # Trend analysis
        first_val = df[value_column].iloc[0]
        last_val = df[value_column].iloc[-1]
        change_pct = ((last_val - first_val) / first_val) * 100
        
        trend = "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable"
        insights.append(f"Overall trend: {trend} ({change_pct:+.1f}% change)")
        
        # Volatility
        volatility = df[value_column].std() / df[value_column].mean()
        vol_level = "high" if volatility > 0.3 else "moderate" if volatility > 0.1 else "low"
        insights.append(f"Volatility: {vol_level} (CV: {volatility:.2f})")
        
        return insights
    
    def export_plots(self, format: str = 'html') -> Dict[str, str]:
        """Export all plots in specified format"""
        exports = {}
        
        for plot_name, plot_data in self.plots.items():
            if format == 'html':
                exports[plot_name] = plot_data['html']
            elif format == 'png':
                # Convert to PNG (requires kaleido)
                try:
                    img_bytes = plot_data['figure'].to_image(format="png")
                    img_b64 = base64.b64encode(img_bytes).decode()
                    exports[plot_name] = img_b64
                except Exception as e:
                    exports[plot_name] = f"Error exporting to PNG: {str(e)}"
        
        return exports
    
    def get_all_plots(self) -> Dict[str, Any]:
        """Get all generated plots"""
        return self.plots.copy()