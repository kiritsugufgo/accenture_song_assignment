import pandas as pd
from pathlib import Path
import logging
from etl.load import save_dataframe, load_processed_data

logger = logging.getLogger(__name__)

# Nordic currency map 
# Euro Conversion in 2020
NORDIC_CURRENCY_MAP = {'FI': 'EUR', 'SE': 'SEK', 'NO': 'NOK', 'DK': 'DKK'}
EXCHANGE_RATES = {'EUR': 1.0, 'SEK': 0.097, 'NOK': 0.093, 'DKK': 0.134}

def _calculate_base_metrics(df, snapshot_date):
    # helper for core aggregations
    return df.groupby('customer_id').agg(
        total_spend_eur=('amount_eur', 'sum'),
        avg_transaction_value=('amount_eur', 'mean'),
        transaction_frequency=('transaction_id', 'count'),
        last_tx_date=('timestamp', 'max')
    ).assign(
        recency_days=lambda x: (snapshot_date - x['last_tx_date']).dt.days
    ).reset_index()

def run_feature_engineering(customers_df: pd.DataFrame, transactions_df: pd.DataFrame):
    # Main pipeline step for Gold Layer creation.
    logger.info("Loading Silver data for feature engineering...") 
    
    # Date handling
    transactions = transactions_df.copy()
    transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])
    snapshot_date = transactions['timestamp'].max()
    
    # Convert to EUR using exchange rates (vectorized for performance)
    rates = transactions['currency'].map(EXCHANGE_RATES).fillna(1.0)
    transactions['amount_eur'] = transactions['amount'] * rates
    # Feature Calculation
    logger.info("Calculating behavioral features and policy flags...")
    gold_features = _calculate_base_metrics(transactions, snapshot_date)

    # Policy Flag: high_ticket_user (> 500 EUR per product_policy.txt)
    high_ticket_ids = transactions[transactions['amount_eur'] > 500]['customer_id'].unique()
    gold_features['high_ticket_user'] = gold_features['customer_id'].isin(high_ticket_ids)

    # Fraud Flag: cross_border_count (mismatched currency per fraud_guidelines.txt)
    temp = transactions.merge(customers_df[['customer_id', 'country']], on='customer_id')
    temp['is_mismatch'] = temp.apply(lambda x: x['currency'] != NORDIC_CURRENCY_MAP.get(x['country']), axis=1)
    cb_counts = temp.groupby('customer_id')['is_mismatch'].sum().reset_index(name='cross_border_count')
    gold_features = gold_features.merge(cb_counts, on='customer_id', how='left')

    # Final Merge & Cleanup
    final_gold = customers_df.merge(gold_features, on='customer_id', how='left')

    # Reuse your save function to write to the gold directory
    save_dataframe(final_gold, "gold_customers.csv", base_path="data/processed_gold")
    save_dataframe(transactions, "gold_transactions.csv", base_path="data/processed_gold")
    logger.info(f"Feature engineering complete. Gold data saved.")
    
    return final_gold