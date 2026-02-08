import logging
from etl.run_etl import run_etl_pipeline
from feature_engineering.add_features import run_feature_engineering
from rag.ingest import ChromaIngestor

logger = logging.getLogger(__name__)

def run_setup():
    """Run this once to prepare the system for the Streamlit app."""
    try:
        logger.info("--- Data Refresh Started ---")

        # 1. ETL & Feature Engineering
        customers_df, transactions_df = run_etl_pipeline()
        gold_customers_df = run_feature_engineering(customers_df, transactions_df)
        
        # 2. Update Vector Store
        logger.info("Updating Vector Database...")
        ingestor = ChromaIngestor()
        ingestor.ingest_directory("data/raw/documents")

        logger.info("--- Setup Successfully Completed ---")

    except Exception as e:
        logger.error(f"Setup failed: {e}")

if __name__ == "__main__":
    run_setup()