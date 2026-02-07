import logging
from etl.extract import extract_customers, extract_transactions
from etl.transform import transform_customers, transform_transactions
from etl.load import save_dataframe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_etl_pipeline():
    """
    Main entry point for the ETL process.
    Coordinates extraction, transformation, and loading.
    """
    try:
        logger.info("Starting ETL Pipeline...")

        # --- STEP 1: EXTRACT ---
        logger.info("Extracting raw data...")
        raw_customers = extract_customers()
        raw_transactions = extract_transactions()

        # --- STEP 2: TRANSFORM ---
        logger.info("Transforming Customer data...")
        cleaned_customers = transform_customers(raw_customers)

        logger.info("Transforming Transaction data...")
        cleaned_transactions = transform_transactions(raw_transactions)

        # --- STEP 3: LOAD ---
        logger.info("Saving processed data to storage...")
        customer_path = save_dataframe(cleaned_customers, "processed_customers.csv")
        transaction_path = save_dataframe(cleaned_transactions, "processed_transactions.csv")

        logger.info(f"ETL Pipeline completed successfully.")
        
        # Return the DataFrames so they can be used immediately by 
        # Feature Engineering or RAG modules without re-reading files.
        return cleaned_customers, cleaned_transactions

    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_etl_pipeline()
    