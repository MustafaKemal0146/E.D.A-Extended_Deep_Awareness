"""
Data Ingestion Engine - Multi-source data loading
"""
import pandas as pd
import json
from pathlib import Path
from typing import Union, Dict, Any
import boto3
from sqlalchemy import create_engine


class DataIngestionEngine:
    """Handle data ingestion from multiple sources"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'parquet', 'sql']
    
    def load_data(self, source: Union[str, Path], source_type: str = 'auto', **kwargs) -> pd.DataFrame:
        """
        Load data from various sources
        
        Args:
            source: Data source path/connection string
            source_type: Type of source (auto-detect if 'auto')
            **kwargs: Additional parameters for specific loaders
        """
        if source_type == 'auto':
            source_type = self._detect_source_type(source)
        
        loaders = {
            'csv': self._load_csv,
            'json': self._load_json,
            'parquet': self._load_parquet,
            'sql': self._load_sql,
            's3': self._load_s3
        }
        
        if source_type not in loaders:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        return loaders[source_type](source, **kwargs)
    
    def _detect_source_type(self, source: str) -> str:
        """Auto-detect source type from path/string"""
        source_str = str(source).lower()
        
        if source_str.startswith('s3://'):
            return 's3'
        elif source_str.startswith(('postgresql://', 'mysql://', 'sqlite://')):
            return 'sql'
        elif source_str.endswith('.csv'):
            return 'csv'
        elif source_str.endswith('.json'):
            return 'json'
        elif source_str.endswith('.parquet'):
            return 'parquet'
        else:
            return 'csv'  # Default fallback
    
    def _load_csv(self, path: str, **kwargs) -> pd.DataFrame:
        """Load CSV file"""
        return pd.read_csv(path, **kwargs)
    
    def _load_json(self, path: str, **kwargs) -> pd.DataFrame:
        """Load JSON file"""
        return pd.read_json(path, **kwargs)
    
    def _load_parquet(self, path: str, **kwargs) -> pd.DataFrame:
        """Load Parquet file"""
        return pd.read_parquet(path, **kwargs)
    
    def _load_sql(self, connection_string: str, query: str = None, table: str = None, **kwargs) -> pd.DataFrame:
        """Load data from SQL database"""
        engine = create_engine(connection_string)
        
        if query:
            return pd.read_sql_query(query, engine, **kwargs)
        elif table:
            return pd.read_sql_table(table, engine, **kwargs)
        else:
            raise ValueError("Either 'query' or 'table' parameter must be provided")
    
    def _load_s3(self, s3_path: str, **kwargs) -> pd.DataFrame:
        """Load data from S3"""
        # Parse S3 path
        parts = s3_path.replace('s3://', '').split('/')
        bucket = parts[0]
        key = '/'.join(parts[1:])
        
        s3_client = boto3.client('s3')
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        
        # Determine file type and load accordingly
        if key.endswith('.csv'):
            return pd.read_csv(obj['Body'], **kwargs)
        elif key.endswith('.json'):
            return pd.read_json(obj['Body'], **kwargs)
        elif key.endswith('.parquet'):
            return pd.read_parquet(obj['Body'], **kwargs)
        else:
            raise ValueError(f"Unsupported S3 file format: {key}")
    
    def get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the dataset"""
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum()
        }