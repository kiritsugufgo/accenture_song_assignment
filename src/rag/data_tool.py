import pandas as pd

def get_gold_data_summary():
    """
    Returns a string representation of the Gold Data schema and stats.
    This is passed to the LLM's system prompt so it knows what it can 'talk' about.
    """
    # Load your gold data
    cust_df = pd.read_csv("data/processed_gold/gold_customers.csv")
    
    summary = f"""
    GOLD_CUSTOMERS TABLE:
    - Columns: {list(cust_df.columns)}
    - Total Customers: {len(cust_df)}
    - Metrics Available: Avg transaction value, Churn risk flag, Total spend.
    
    GOLD_TRANSACTIONS TABLE:
    - Transaction count: {len(pd.read_csv('data/processed_gold/gold_transactions.csv'))}
    - Key Fields: timestamp, amount, customer_id, category.
    """
    return summary