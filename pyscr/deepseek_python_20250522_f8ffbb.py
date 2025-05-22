import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import Union, Optional
from . import OUTPUT_PATH, setup_logger

def save_to_parquet(
    df: pd.DataFrame, 
    filename: str, 
    partition_cols: Optional[list] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """Save DataFrame to Parquet format."""
    if logger is None:
        logger = setup_logger()
    
    output_path = Path(OUTPUT_PATH) / filename
    try:
        table = pa.Table.from_pandas(df)
        pq.write_table(
            table, 
            output_path, 
            partition_cols=partition_cols,
            compression='snappy'
        )
        logger.info(f"Data saved to Parquet file: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save Parquet file: {e}")
        raise

def describe_extended(df: pd.DataFrame) -> pd.DataFrame:
    """Extended describe function with additional statistics."""
    stats = df.describe(include='all').T
    stats['nulls'] = df.isnull().sum()
    stats['zeros'] = (df == 0).sum()
    stats['uniques'] = df.nunique()
    stats['dtype'] = df.dtypes
    return stats

def filter_by_quantile(
    df: pd.DataFrame, 
    column: str, 
    lower_quantile: float = 0.05, 
    upper_quantile: float = 0.95
) -> pd.DataFrame:
    """Filter DataFrame by quantile range of a specific column."""
    lower_bound = df[column].quantile(lower_quantile)
    upper_bound = df[column].quantile(upper_quantile)
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

def merge_with_indicator(
    left: pd.DataFrame, 
    right: pd.DataFrame, 
    **kwargs
) -> pd.DataFrame:
    """Merge DataFrames with an indicator column showing source."""
    if 'indicator' not in kwargs:
        kwargs['indicator'] = '_merge'
    return pd.merge(left, right, **kwargs)