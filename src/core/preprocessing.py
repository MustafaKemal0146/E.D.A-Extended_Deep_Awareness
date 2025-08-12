"""
Preprocessing Pipeline - Data cleaning and transformation
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Any, Optional


class PreprocessingPipeline:
    """Advanced data preprocessing and transformation"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.transformations_applied = []
    
    def clean_data(self, df: pd.DataFrame, remove_duplicates: bool = True, 
                   handle_outliers: str = 'iqr') -> pd.DataFrame:
        """
        Clean the dataset
        
        Args:
            df: Input dataframe
            remove_duplicates: Whether to remove duplicate rows
            handle_outliers: Method to handle outliers ('iqr', 'zscore', 'isolation_forest')
        """
        df_clean = df.copy()
        
        # Remove duplicates
        if remove_duplicates:
            initial_shape = df_clean.shape[0]
            df_clean = df_clean.drop_duplicates()
            removed = initial_shape - df_clean.shape[0]
            if removed > 0:
                self.transformations_applied.append(f"Removed {removed} duplicate rows")
        
        # Handle outliers
        if handle_outliers and not df_clean.empty:
            df_clean = self._handle_outliers(df_clean, method=handle_outliers)
        
        return df_clean
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """
        Handle missing values using various strategies
        
        Args:
            df: Input dataframe
            strategy: Imputation strategy ('mean', 'median', 'mode', 'knn', 'auto')
        """
        df_imputed = df.copy()
        
        for column in df_imputed.columns:
            if df_imputed[column].isnull().sum() > 0:
                if strategy == 'auto':
                    # Choose strategy based on data type and distribution
                    if df_imputed[column].dtype in ['object', 'category']:
                        # Mode for categorical
                        df_imputed[column].fillna(df_imputed[column].mode()[0], inplace=True)
                    elif df_imputed[column].dtype in ['int64', 'float64']:
                        # Median for numerical (more robust to outliers)
                        df_imputed[column].fillna(df_imputed[column].median(), inplace=True)
                elif strategy == 'knn':
                    # KNN imputation for numerical columns
                    numerical_cols = df_imputed.select_dtypes(include=[np.number]).columns
                    if column in numerical_cols:
                        imputer = KNNImputer(n_neighbors=5)
                        df_imputed[numerical_cols] = imputer.fit_transform(df_imputed[numerical_cols])
                        self.imputers[column] = imputer
                else:
                    # Standard strategies
                    if strategy == 'mean' and df_imputed[column].dtype in ['int64', 'float64']:
                        df_imputed[column].fillna(df_imputed[column].mean(), inplace=True)
                    elif strategy == 'median' and df_imputed[column].dtype in ['int64', 'float64']:
                        df_imputed[column].fillna(df_imputed[column].median(), inplace=True)
                    elif strategy == 'mode':
                        df_imputed[column].fillna(df_imputed[column].mode()[0], inplace=True)
        
        missing_handled = df.isnull().sum().sum() - df_imputed.isnull().sum().sum()
        if missing_handled > 0:
            self.transformations_applied.append(f"Handled {missing_handled} missing values using {strategy}")
        
        return df_imputed
    
    def encode_categorical(self, df: pd.DataFrame, method: str = 'auto') -> pd.DataFrame:
        """
        Encode categorical variables
        
        Args:
            df: Input dataframe
            method: Encoding method ('onehot', 'label', 'auto')
        """
        df_encoded = df.copy()
        categorical_cols = df_encoded.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            unique_values = df_encoded[col].nunique()
            
            if method == 'auto':
                # Use one-hot for low cardinality, label encoding for high cardinality
                if unique_values <= 10:
                    # One-hot encoding
                    dummies = pd.get_dummies(df_encoded[col], prefix=col)
                    df_encoded = pd.concat([df_encoded.drop(col, axis=1), dummies], axis=1)
                else:
                    # Label encoding
                    encoder = LabelEncoder()
                    df_encoded[col] = encoder.fit_transform(df_encoded[col].astype(str))
                    self.encoders[col] = encoder
            elif method == 'onehot':
                dummies = pd.get_dummies(df_encoded[col], prefix=col)
                df_encoded = pd.concat([df_encoded.drop(col, axis=1), dummies], axis=1)
            elif method == 'label':
                encoder = LabelEncoder()
                df_encoded[col] = encoder.fit_transform(df_encoded[col].astype(str))
                self.encoders[col] = encoder
        
        if len(categorical_cols) > 0:
            self.transformations_applied.append(f"Encoded {len(categorical_cols)} categorical columns using {method}")
        
        return df_encoded
    
    def scale_features(self, df: pd.DataFrame, method: str = 'standard', 
                      columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Scale numerical features
        
        Args:
            df: Input dataframe
            method: Scaling method ('standard', 'minmax', 'robust')
            columns: Specific columns to scale (if None, scale all numerical)
        """
        df_scaled = df.copy()
        
        if columns is None:
            columns = df_scaled.select_dtypes(include=[np.number]).columns.tolist()
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unsupported scaling method: {method}")
        
        if columns:
            df_scaled[columns] = scaler.fit_transform(df_scaled[columns])
            self.scalers[method] = scaler
            self.transformations_applied.append(f"Applied {method} scaling to {len(columns)} columns")
        
        return df_scaled
    
    def _handle_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Handle outliers using various methods"""
        df_clean = df.copy()
        numerical_cols = df_clean.select_dtypes(include=[np.number]).columns
        
        if method == 'iqr':
            for col in numerical_cols:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_mask = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
                outliers_count = outliers_mask.sum()
                
                if outliers_count > 0:
                    # Cap outliers instead of removing
                    df_clean.loc[df_clean[col] < lower_bound, col] = lower_bound
                    df_clean.loc[df_clean[col] > upper_bound, col] = upper_bound
                    self.transformations_applied.append(f"Capped {outliers_count} outliers in {col}")
        
        elif method == 'zscore':
            for col in numerical_cols:
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                outliers_mask = z_scores > 3
                outliers_count = outliers_mask.sum()
                
                if outliers_count > 0:
                    # Replace with median
                    median_val = df_clean[col].median()
                    df_clean.loc[outliers_mask, col] = median_val
                    self.transformations_applied.append(f"Replaced {outliers_count} outliers in {col} with median")
        
        elif method == 'isolation_forest':
            if len(numerical_cols) > 0:
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers_mask = iso_forest.fit_predict(df_clean[numerical_cols]) == -1
                outliers_count = outliers_mask.sum()
                
                if outliers_count > 0:
                    # Remove outlier rows
                    df_clean = df_clean[~outliers_mask]
                    self.transformations_applied.append(f"Removed {outliers_count} outlier rows using Isolation Forest")
        
        return df_clean
    
    def apply_pca(self, df: pd.DataFrame, n_components: float = 0.95) -> pd.DataFrame:
        """
        Apply PCA for dimensionality reduction
        
        Args:
            df: Input dataframe
            n_components: Number of components or variance ratio to retain
        """
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return df
        
        pca = PCA(n_components=n_components)
        pca_features = pca.fit_transform(df[numerical_cols])
        
        # Create new dataframe with PCA components
        pca_columns = [f'PC{i+1}' for i in range(pca_features.shape[1])]
        df_pca = pd.DataFrame(pca_features, columns=pca_columns, index=df.index)
        
        # Add non-numerical columns back
        non_numerical_cols = df.select_dtypes(exclude=[np.number]).columns
        if len(non_numerical_cols) > 0:
            df_pca = pd.concat([df_pca, df[non_numerical_cols]], axis=1)
        
        explained_variance = pca.explained_variance_ratio_.sum()
        self.transformations_applied.append(
            f"Applied PCA: {len(pca_columns)} components explaining {explained_variance:.2%} variance"
        )
        
        return df_pca
    
    def get_transformation_summary(self) -> List[str]:
        """Get summary of all transformations applied"""
        return self.transformations_applied.copy