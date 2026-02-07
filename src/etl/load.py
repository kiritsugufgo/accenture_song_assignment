import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

def save_dataframe(df: pd.DataFrame, filename: str, base_path: str = "data/processed_silver") -> str:
    """
    Saves a dataframe to the specified path. 
    Using CSV for accessibility, but would use Parquet in a production environment 
    for better schema preservation and compression.
    """
    out_dir = Path(base_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = out_dir / filename
    
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully saved: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to save {filename}: {e}")
        raise

def load_processed_data(filename: str, base_path: str = "data/processed_silver") -> pd.DataFrame:
    #Helper to read data for the Feature Engineering phase.
    file_path = Path(base_path) / filename
    return pd.read_csv(file_path)