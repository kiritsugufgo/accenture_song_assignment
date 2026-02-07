'''
Extract module that handles reading raw data files and validating their schemas.
Added schema validation in case more data are added in the future.
'''
from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path("data/raw/csv")

# Should this be stored in yaml or json instead?
# For now, hardcoding the expected columns in the code for simplicity.
EXPECTED_CUSTOMER_COLUMNS = {
    "customer_id",
    "country",
    "signup_date",
    "email",
}

EXPECTED_TRANSACTION_COLUMNS = {
    "transaction_id",
    "customer_id",
    "amount",
    "currency",
    "timestamp",
    "category",
}


def _validate_schema(
    df: pd.DataFrame, expected_columns: set, dataset_name: str
) -> None:
    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: {missing_columns}"
        )


def extract_customers() -> pd.DataFrame:
    customers_df = pd.read_csv(RAW_DATA_PATH / "customers.csv")
    _validate_schema(customers_df, EXPECTED_CUSTOMER_COLUMNS, "customers")
    return customers_df


def extract_transactions() -> pd.DataFrame:
    transactions_df = pd.read_csv(RAW_DATA_PATH / "transactions.csv")
    _validate_schema(transactions_df, EXPECTED_TRANSACTION_COLUMNS, "transactions")
    return transactions_df