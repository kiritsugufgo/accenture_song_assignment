import logging
from etl.run_etl import run_etl_pipeline
from feature_engineering.add_features import run_feature_engineering

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("--- Pipeline Started ---")

        # 1. Run the ETL pipeline to get cleaned DataFrames 
        customers_df, transactions_df = run_etl_pipeline()

        # Step 2: Feature Engineering (Accepts DFs directly)
        gold_customers_df = run_feature_engineering(customers_df, transactions_df)

        # Step 3: RAG (We will eventually pass gold_customers_df here)
        # run_rag_pipeline(gold_customers_df)

        logger.info("--- Pipeline Successfully Completed ---")

    except Exception as e:
        logger.error(f"Pipeline crashed: {e}")

if __name__ == "__main__":
    main()