import streamlit as st
from typing import List, Dict
import sys
from pathlib import Path
import pandas as pd

current_file_path = Path(__file__).resolve() # .../src/app/main_app.py
project_root = current_file_path.parent.parent # .../src/
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from rag.rag_logic import RAGOrchestrator
from app.components.result_card import render_result_card

# Page config
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def get_rag_engine():
    return RAGOrchestrator()

rag_engine = get_rag_engine()

# Mock RAG function for demonstration
def mock_rag_query(question: str) -> Dict:
    """
    Mock RAG function that returns structured response.
    Replace this with your actual RAG implementation.
    """
    # Mock answer
    answer = f"""
    Based on the analysis of customer data and transactions, here's what I found regarding your question:
    
    {question}
    
    The data shows interesting patterns in customer behavior. We observed that customers 
    with higher transaction frequencies tend to have better engagement rates. The fraud 
    detection guidelines suggest monitoring transactions above certain thresholds.
    
    Key insights:
    - Average transaction value: $245.67
    - Most active customer segment: Premium tier
    - Fraud risk: Low (2.3% of transactions flagged)
    """
    
    # Mock source data table
    source_data = pd.DataFrame({
        'Source': ['customers.csv', 'transactions.csv', 'fraud_guidelines.txt'],
        'Type': ['CSV', 'CSV', 'Document'],
        'Records Used': [150, 1250, 'N/A'],
        'Relevance Score': [0.92, 0.88, 0.75],
        'Last Updated': ['2024-01-15', '2024-01-20', '2024-01-10']
    })
    
    # Mock metadata
    metadata = {
        'Processing Time': '1.2s',
        'Confidence Score': '0.87',
        'Model': 'RAG-v1',
        'Total Sources': 3
    }
    
    return {
        'answer': answer,
        'source_data': source_data,
        'metadata': metadata
    }
    
def real_rag_query(question: str) -> Dict:
    # This now returns the full dict: {answer, source_data, metadata}
    return rag_engine.ask(question)
    
# Title and description
st.title("🤖 RAG Assistant")
st.markdown("Ask questions about your customer data, transactions, and policies.")

# User input section (fixed at top)
with st.container():
    user_input = st.text_area(
        "Your Question:",
        height=100,
        placeholder="e.g., What are the top spending customers? Show me fraud patterns.",
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("🚀 Send", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)

# Handle clear button
if clear_button:
    st.session_state.messages = []
    st.rerun()

# Handle send button
if send_button and user_input.strip():
    # Call mock RAG function (replace with your actual RAG)
    rag_response = real_rag_query(user_input)
    
    # Add to conversation history
    st.session_state.messages.append({
        'question': user_input,
        'answer': rag_response['answer'],
        'source_data': rag_response['source_data'],
        'metadata': rag_response['metadata']
    })
    
    st.rerun()

# Display conversation history
st.markdown("---")

if len(st.session_state.messages) == 0:
    st.info("👋 Welcome! Ask a question to get started.")
else:
    st.subheader(f"💬 Conversation ({len(st.session_state.messages)} queries)")
    
    # Display messages in reverse order (newest first)
    for idx, message in enumerate(reversed(st.session_state.messages)):
        message_number = len(st.session_state.messages) - idx
        
        with st.expander(f"Query #{message_number}", expanded=(idx == 0)):
            render_result_card(
                question=message['question'],
                answer=message['answer'],
                source_data=message.get('source_data'),
                metadata=message.get('metadata'),
                card_index=message_number
            )

# Sidebar with mock test button
with st.sidebar:
    st.header("Settings")
    
    if st.button("🧪 Load Mock Test", use_container_width=True):
        # Add a mock conversation
        mock_questions = [
            "What is the average transaction amount for premium customers?",
            "Show me the fraud detection patterns from last month",
            "Which customers have the highest lifetime value?"
        ]
        
        st.session_state.messages = []
        for q in mock_questions:
            rag_response = mock_rag_query(q)
            st.session_state.messages.append({
                'question': q,
                'answer': rag_response['answer'],
                'source_data': rag_response['source_data'],
                'metadata': rag_response['metadata']
            })
        
        st.rerun()
    
    if st.session_state.messages:
        st.metric("Total Queries", len(st.session_state.messages))
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This RAG assistant helps you query customer data and policies.")