import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional

# Load the gold data for visualization context
CUST_DF = pd.read_csv("data/processed_gold/gold_customers.csv")

def generate_customer_visualization(customer_id: int, plot_type: str) -> plt.Figure:
    """
    Generates a distribution plot for a specific metric and highlights a customer's position.
    """
    # 1. Fetch customer data
    customer_row = CUST_DF[CUST_DF['customer_id'] == customer_id]
    if customer_row.empty:
        raise ValueError(f"Customer ID {customer_id} not found.")

    # 2. Configuration for the 4 specific plots requested
    config = {
        "avg_transaction": {
            "col": "avg_transaction_value",
            "title": "Distribution of Average Transaction Value",
            "label": "Avg Transaction Value (EUR)"
        },
        "frequency": {
            "col": "transaction_frequency",
            "title": "Distribution of Transaction Frequency",
            "label": "Number of Transactions"
        },
        "recency": {
            "col": "recency_days",
            "title": "Distribution of Recency (Days Since Last Transaction)",
            "label": "Recency (days)"
        },
        "cross_border": {
            "col": "cross_border_count",
            "title": "Distribution of Cross-Border Transaction Count",
            "label": "Cross-Border Transaction Count"
        }
    }

    plt_cfg = config.get(plot_type)
    if not plt_cfg:
        raise ValueError(f"Unsupported plot type: {plot_type}")

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(CUST_DF[plt_cfg['col']], bins=30, kde=True, ax=ax, color="#1f77b4")
    
    # Add vertical line for the specific customer
    customer_value = customer_row[plt_cfg['col']].iloc[0]
    ax.axvline(
        customer_value, 
        color='red', 
        linestyle='--', 
        linewidth=2, 
        label=f'Customer {customer_id} ({customer_value:.2f})'
    )

    ax.set_title(plt_cfg['title'])
    ax.set_xlabel(plt_cfg['label'])
    ax.set_ylabel("Count of Customers")
    ax.legend()
    
    return fig

def get_viz_tool_definition():
    """Returns the tool definition for the Mistral/OpenAI API."""
    return {
        "type": "function",
        "function": {
            "name": "generate_customer_visualization",
            "description": "Visualizes a customer's position relative to the whole database for specific metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "The unique ID of the customer."},
                    "plot_type": {
                        "type": "string",
                        "enum": ["avg_transaction", "frequency", "recency", "cross_border"],
                        "description": "The metric to visualize on the X-axis."
                    }
                },
                "required": ["customer_id", "plot_type"]
            }
        }
    }