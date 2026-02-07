from etl.run_etl import run_etl_pipeline

def main():
    # 1. Run the ETL pipeline to get cleaned DataFrames
    customers_df, transactions_df = run_etl_pipeline()


if __name__ == "__main__":
    main()
