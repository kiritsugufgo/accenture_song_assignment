'''
This module cleans the data. 

Data cleaning is mostly focused on the transactions dataset. 

Transactions data is cleaned by:
1. Remove duplicates from transactions
2. Drop transactions with missing customer_id (since we can't link them to customers)
3. Data type conversions (dates, proper numeric types)
4. Standardize currency codes to uppercase
5. Filter invalid data: Remove transactions with negative or zero amounts
6. Handle missing currency and category:
7. Sort transactions by customer_id and timestamp for logical grouping and easier analysis later on.

Now handling the missing currency and category field is tricky. 
During this etl pipeline, I'm going to impute missing currency as DKK and leave unkonwn categories as 'uncategorized'.
The reasonning will be written in another document

customers_df and transactions_df are going to be merged at the end of the transformation
'''

import pandas as pd
import logging

logger = logging.getLogger(__name__)

#Standardizes categories and marks imputed/unknown values.
def _handle_category_cleaning(transactions_df: pd.DataFrame) -> pd.DataFrame:
    # Funciton replaces missing values and 'unknown' to 'uncategorized'
    # Addds a flag to mark imputed/unknown categories for future analysis.
    df = transactions_df.copy()
    
    df['is_category_imputed'] = df['category'].isna() | (df['category'].str.strip().str.lower() == 'unknown')
    
    df['category'] = df['category'].fillna('uncategorized').str.strip().str.lower()
    df.loc[df['category'] == 'unknown', 'category'] = 'uncategorized'
    
    return df

def _handle_currency_imputation(transactions_df: pd.DataFrame) -> pd.DataFrame:
    # impute missing currencies, by adding DKK to it. Reasoning can be found in the document   
    df = transactions_df.copy()
    
    df['is_currency_imputed'] = df['currency'].isna()
    
    df['currency'] = (
        df['currency']
        .fillna('DKK')
        .str.strip()
        .str.upper()
    )
    
    return df


#Customers data is relatively clean, mainly needs type conversions.
def transform_customers(customers_df: pd.DataFrame) -> pd.DataFrame:
    
    df = customers_df.copy()
    
    df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
    df['customer_id'] = df['customer_id'].astype('Int64')
    df['country'] = df['country'].str.upper()
    df = df.dropna(subset=['customer_id'])
    
    return df

def transform_transactions(transactions_df: pd.DataFrame) -> pd.DataFrame:
    
    df = transactions_df.copy()
    initial_rows = len(df)
    
    # 1. Remove exact duplicates
    df = df.drop_duplicates()
    if len(df) < initial_rows:
        logger.info(f"Removed {initial_rows - len(df)} duplicate transactions")
    
    # 2. Drop transactions with missing customer_id
    missing_customer_id = df['customer_id'].isna().sum()
    df = df.dropna(subset=['customer_id'])
    if missing_customer_id > 0:
        logger.warning(f"Dropped {missing_customer_id} transactions with missing customer_id")
    
    # 3. Data type conversions
    df['customer_id'] = df['customer_id'].astype('Int64')
    df['transaction_id'] = df['transaction_id'].astype('Int64')
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    invalid_timestamp = df['timestamp'].isna().sum()
    invalid_amount = df['amount'].isna().sum()
    df = df.dropna(subset=['timestamp', 'amount'])
    if invalid_timestamp > 0 or invalid_amount > 0:
        logger.warning(
            f"Dropped {invalid_timestamp} transactions with invalid timestamp, "
            f"{invalid_amount} with invalid amount"
        )
        
    # 4. Standardize currency codes to uppercase
    df['currency'] = df['currency'].str.upper()
    
    # 5. Filter invalid data: Remove transactions with negative or zero amounts
    invalid_amounts = (df['amount'] <= 0).sum()
    df = df[df['amount'] > 0]
    if invalid_amounts > 0:
        logger.warning(f"Removed {invalid_amounts} transactions with non-positive amounts")

    # 6 handle missing category and currency
    logger.info("Handling missing currency and category fields...")
    
    df = _handle_category_cleaning(df)
    df = _handle_currency_imputation(df)

    # 7. Sort and Group logically
    # This groups by customer_id (ascending) and then by timestamp (oldest to newest)
    logger.info("Sorting transactions by customer_id and timestamp...")
    df = df.sort_values(by=['customer_id', 'timestamp'], ascending=[True, True])
    
    # reset index
    df = df.reset_index(drop=True)
    
    
    return df
 
