import pandas as pd

CUST_DF = pd.read_csv("data/processed_gold/gold_customers.csv")
TRANS_DF = pd.read_csv("data/processed_gold/gold_transactions.csv")

def get_gold_data_summary():
    """Returns a string representation of the schema for LLM context."""
    summary = f"""
    TABLE SCHEMAS:
    - GOLD_CUSTOMERS: {list(CUST_DF.columns)}
    - GOLD_TRANSACTIONS: {list(TRANS_DF.columns)}
    """
    return summary

def execute_data_analysis(query_type: str, table_name: str, column: str, value: str = None, operator: str = "==", n: int = 5):
    df = CUST_DF if table_name == "customers" else TRANS_DF
    
    if column not in df.columns:
        return f"Error: Column '{column}' not found in {table_name}."

    try:
        # --- Handle Ranking Queries (e.g., "Top 5 Spenders") ---
        if query_type == "top_n":
            result = df.nlargest(n, column)
            return result.to_string(index=False)

        # --- Handle Filter Queries (e.g., "Customer ID 1971") ---
        if query_type == "filter":
            # 1. Type Conversion Logic
            target_dtype = df[column].dtype
            
            if target_dtype == 'bool':
                converted_value = value.lower() == 'true'
            elif target_dtype in ['int64', 'int32']:
                converted_value = int(value)
            elif target_dtype in ['float64', 'float32']:
                converted_value = float(value)
            else:
                converted_value = str(value)

            # 2. Apply Operators
            if operator == "==":
                result = df[df[column] == converted_value]
            elif operator == ">":
                result = df[df[column] > converted_value]
            elif operator == "<":
                result = df[df[column] < converted_value]
            elif operator == "contains":
                result = df[df[column].astype(str).str.contains(str(value), case=False)]
            
            if result.empty:
                return f"No records found in {table_name} where {column} {operator} {value}."
                
            return result.head(10).to_string(index=False)

    except Exception as e:
        return f"Analysis Error: {str(e)}"

def get_csv_tool_definition():
    return {
        "type": "function",
        "function": {
            "name": "execute_data_analysis",
            "description": ("Essential for behavioral analysis and specific customer lookups in the Nordic finance datasets. "
                            "Query the Nordic finance gold datasets (customers and transactions)."),
            "parameters": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string", 
                        "enum": ["filter", "top_n"],
                        "description": "Use 'filter' for specific lookups (e.g., ID=123) or 'top_n' for rankings (e.g., top spenders)."
                    },
                    "table_name": {
                        "type": "string", 
                        "enum": ["customers", "transactions"],
                        "description": "Which table to query."
                    },
                    "column": {
                        "type": "string",
                        "description": (
                            "For 'customers' use: customer_id, country, signup_date, email, total_spend_eur, "
                            "avg_transaction_value, transaction_frequency, last_tx_date, recency_days, high_ticket_user, cross_border_count. "
                            "For 'transactions' use: transaction_id, customer_id, amount, currency, timestamp, category, amount_eur."
                        )
                    },
                    "operator": {
                        "type": "string", 
                        "enum": ["==", "contains", ">", "<"],
                        "description": "Comparison operator. Use 'contains' for partial text matches."
                    },
                    "value": {
                        "type": "string", 
                        "description": "The value to filter by. For booleans (high_ticket_user), use 'True' or 'False'."
                    },
                    "n": {
                        "type": "integer", 
                        "default": 5, 
                        "description": "Number of rows to return (for top_n queries)."
                    }
                },
                "required": ["query_type", "table_name", "column"]
            }
        }
    }
