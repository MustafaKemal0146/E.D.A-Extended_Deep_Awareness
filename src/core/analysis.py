"""
Deep Analysis Engine - Statistical, ML, and NLP analysis
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import shap
from typing import Dict, List, Any, Optional, Tuple


class DeepAnalysisEngine:
    """Perform comprehensive data analysis"""
    
    def __init__(self):
        self.analysis_results = {}
        self.models = {}
    
    def statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive statistical analysis
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary containing statistical analysis results
        """
        results = {}
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        # Descriptive statistics
        results['descriptive_stats'] = df[numerical_cols].describe().to_dict()
        
        # Distribution analysis
        results['distribution_tests'] = {}
        for col in numerical_cols:
            if df[col].nunique() > 1:  # Skip constant columns
                # Shapiro-Wilk test for normality
                stat, p_value = stats.shapiro(df[col].dropna().sample(min(5000, len(df[col].dropna()))))
                results['distribution_tests'][col] = {
                    'shapiro_wilk_stat': stat,
                    'shapiro_wilk_p_value': p_value,
                    'is_normal': p_value > 0.05,
                    'skewness': df[col].skew(),
                    'kurtosis': df[col].kurtosis()
                }
        
        # Correlation analysis
        if len(numerical_cols) > 1:
            correlation_matrix = df[numerical_cols].corr()
            results['correlations'] = {
                'correlation_matrix': correlation_matrix.to_dict(),
                'strong_correlations': self._find_strong_correlations(correlation_matrix)
            }
        
        # Hypothesis testing for categorical vs numerical
        results['hypothesis_tests'] = self._perform_hypothesis_tests(df)
        
        self.analysis_results['statistical'] = results
        return results
    
    def clustering_analysis(self, df: pd.DataFrame, n_clusters: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform clustering analysis
        
        Args:
            df: Input dataframe
            n_clusters: Number of clusters (auto-determine if None)
            
        Returns:
            Dictionary containing clustering results
        """
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return {'error': 'Need at least 2 numerical columns for clustering'}
        
        X = df[numerical_cols].fillna(df[numerical_cols].mean())
        results = {}
        
        # K-Means clustering
        if n_clusters is None:
            # Use elbow method to find optimal clusters
            inertias = []
            K_range = range(2, min(11, len(X)))
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(X)
                inertias.append(kmeans.inertia_)
            
            # Simple elbow detection
            n_clusters = self._find_elbow(K_range, inertias)
        
        # Fit K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(X)
        
        # Fit DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(X)
        
        results = {
            'kmeans': {
                'n_clusters': n_clusters,
                'labels': kmeans_labels.tolist(),
                'centroids': kmeans.cluster_centers_.tolist(),
                'inertia': kmeans.inertia_,
                'cluster_sizes': pd.Series(kmeans_labels).value_counts().to_dict()
            },
            'dbscan': {
                'labels': dbscan_labels.tolist(),
                'n_clusters': len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0),
                'n_noise_points': list(dbscan_labels).count(-1),
                'cluster_sizes': pd.Series(dbscan_labels[dbscan_labels != -1]).value_counts().to_dict()
            }
        }
        
        self.analysis_results['clustering'] = results
        return results
    
    def feature_importance_analysis(self, df: pd.DataFrame, target_column: str, 
                                  task_type: str = 'auto') -> Dict[str, Any]:
        """
        Analyze feature importance using Random Forest and SHAP
        
        Args:
            df: Input dataframe
            target_column: Name of target column
            task_type: 'classification', 'regression', or 'auto'
            
        Returns:
            Dictionary containing feature importance results
        """
        if target_column not in df.columns:
            return {'error': f'Target column {target_column} not found'}
        
        # Prepare features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Handle categorical variables
        X_encoded = pd.get_dummies(X, drop_first=True)
        
        # Determine task type
        if task_type == 'auto':
            if y.dtype == 'object' or y.nunique() < 10:
                task_type = 'classification'
            else:
                task_type = 'regression'
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, test_size=0.2, random_state=42
        )
        
        # Train model
        if task_type == 'classification':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Performance metrics
            performance = {
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'accuracy': model.score(X_test, y_test)
            }
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Performance metrics
            performance = {
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2_score': r2_score(y_test, y_pred)
            }
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_encoded.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # SHAP analysis (on a sample for performance)
        try:
            sample_size = min(100, len(X_test))
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_test.iloc[:sample_size], check_additivity=False)
            
            if task_type == 'classification' and len(np.array(shap_values).shape) == 3:
                # Multi-class classification - use first class for simplicity
                shap_values = shap_values[0]
            
            shap_importance = pd.DataFrame({
                'feature': X_encoded.columns,
                'shap_importance': np.abs(shap_values).mean(0)
            }).sort_values('shap_importance', ascending=False)
        except Exception as e:
            # Fallback to feature importance only if SHAP fails
            shap_importance = pd.DataFrame({
                'feature': X_encoded.columns,
                'shap_importance': model.feature_importances_
            }).sort_values('shap_importance', ascending=False)
        
        results = {
            'task_type': task_type,
            'performance': performance,
            'feature_importance': feature_importance.to_dict('records'),
            'shap_importance': shap_importance.to_dict('records'),
            'top_features': feature_importance.head(10)['feature'].tolist()
        }
        
        self.models[target_column] = model
        self.analysis_results['feature_importance'] = results
        return results
    
    def time_series_analysis(self, df: pd.DataFrame, date_column: str, 
                           value_column: str) -> Dict[str, Any]:
        """
        Perform time series analysis
        
        Args:
            df: Input dataframe
            date_column: Name of date column
            value_column: Name of value column
            
        Returns:
            Dictionary containing time series analysis results
        """
        if date_column not in df.columns or value_column not in df.columns:
            return {'error': 'Date or value column not found'}
        
        # Prepare time series data
        ts_df = df[[date_column, value_column]].copy()
        ts_df[date_column] = pd.to_datetime(ts_df[date_column])
        ts_df = ts_df.sort_values(date_column).set_index(date_column)
        ts_df = ts_df.dropna()
        
        if len(ts_df) < 10:
            return {'error': 'Not enough data points for time series analysis'}
        
        results = {}
        
        # Basic statistics
        results['basic_stats'] = {
            'start_date': ts_df.index.min().isoformat(),
            'end_date': ts_df.index.max().isoformat(),
            'data_points': len(ts_df),
            'mean': ts_df[value_column].mean(),
            'std': ts_df[value_column].std(),
            'trend': 'increasing' if ts_df[value_column].iloc[-1] > ts_df[value_column].iloc[0] else 'decreasing'
        }
        
        # Seasonality detection (simple approach)
        if len(ts_df) >= 24:  # Need enough data for seasonality
            # Check for weekly seasonality (if daily data)
            ts_df['day_of_week'] = ts_df.index.dayofweek
            weekly_pattern = ts_df.groupby('day_of_week')[value_column].mean()
            weekly_variation = weekly_pattern.std() / weekly_pattern.mean()
            
            # Check for monthly seasonality
            ts_df['month'] = ts_df.index.month
            monthly_pattern = ts_df.groupby('month')[value_column].mean()
            monthly_variation = monthly_pattern.std() / monthly_pattern.mean()
            
            results['seasonality'] = {
                'weekly_variation_coefficient': weekly_variation,
                'monthly_variation_coefficient': monthly_variation,
                'has_weekly_pattern': weekly_variation > 0.1,
                'has_monthly_pattern': monthly_variation > 0.1,
                'weekly_pattern': weekly_pattern.to_dict(),
                'monthly_pattern': monthly_pattern.to_dict()
            }
        
        # Stationarity test (Augmented Dickey-Fuller)
        try:
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(ts_df[value_column].dropna())
            results['stationarity'] = {
                'adf_statistic': adf_result[0],
                'p_value': adf_result[1],
                'is_stationary': adf_result[1] < 0.05,
                'critical_values': adf_result[4]
            }
        except ImportError:
            results['stationarity'] = {'error': 'statsmodels not available'}
        
        self.analysis_results['time_series'] = results
        return results
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """Find pairs of variables with strong correlations"""
        strong_corrs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corrs.append({
                        'variable1': corr_matrix.columns[i],
                        'variable2': corr_matrix.columns[j],
                        'correlation': corr_value,
                        'strength': 'very strong' if abs(corr_value) >= 0.9 else 'strong'
                    })
        
        return sorted(strong_corrs, key=lambda x: abs(x['correlation']), reverse=True)
    
    def _perform_hypothesis_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform hypothesis tests between categorical and numerical variables"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        tests = {}
        
        for cat_col in categorical_cols:
            for num_col in numerical_cols:
                groups = [group[num_col].dropna() for name, group in df.groupby(cat_col)]
                groups = [g for g in groups if len(g) > 1]  # Remove empty groups
                
                if len(groups) >= 2:
                    try:
                        if len(groups) == 2:
                            # T-test for two groups
                            stat, p_value = stats.ttest_ind(groups[0], groups[1])
                            test_name = 't-test'
                        else:
                            # ANOVA for multiple groups
                            stat, p_value = stats.f_oneway(*groups)
                            test_name = 'ANOVA'
                        
                        tests[f'{cat_col}_vs_{num_col}'] = {
                            'test': test_name,
                            'statistic': stat,
                            'p_value': p_value,
                            'significant': p_value < 0.05,
                            'groups_count': len(groups)
                        }
                    except Exception as e:
                        tests[f'{cat_col}_vs_{num_col}'] = {'error': str(e)}
        
        return tests
    
    def _find_elbow(self, k_range: range, inertias: List[float]) -> int:
        """Find elbow point for optimal number of clusters"""
        if len(inertias) < 3:
            return k_range[0]
        
        # Simple elbow detection using second derivative
        diffs = np.diff(inertias)
        diffs2 = np.diff(diffs)
        
        if len(diffs2) > 0:
            elbow_idx = np.argmax(diffs2) + 2  # +2 because of double diff
            return k_range[min(elbow_idx, len(k_range) - 1)]
        
        return k_range[len(k_range) // 2]  # Default to middle
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all analysis results"""
        return self.analysis_results.copy()