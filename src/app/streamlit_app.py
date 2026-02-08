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
    page_title="Yuto Kvist, Home Assignment",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'mock_test_idx' not in st.session_state:
    st.session_state.mock_test_idx = -1

@st.cache_resource
def get_rag_engine():
    return RAGOrchestrator()

rag_engine = get_rag_engine()

def real_rag_query(question: str) -> Dict:
    # This now returns the full dict: {answer, source_data, metadata}
    return rag_engine.ask(question)
   
 # Sidebar with mock test button
MOCK_TEST_QUESTIONS = [
    "Could you provide a detailed profile for customer ID 1971?",
    "Identify the top 5 customers by total spending and summarize their key traits.",
    "Customer 2368 is interesting, I would like to visualize how it compares with the rest?",
    "Show me the most expensive transactions."
]

# Title and description
st.title("RAG UI for Nordic Financial Data Analysis")
st.markdown("Ask questions about your customer data, transactions and policies.")

# User input section (fixed at top)
with st.container():
    user_input = st.text_area(
        "Your Question:",
        height=100,
        placeholder="e.g., What are the top spending customers? Show me fraud patterns.",
        key="user_input_box"
    )
    
    # Button Row
    col1, col2, col3, col4 = st.columns([1, 1, 1.5, 3])
    with col1:
        send_button = st.button("🚀 Send", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    with col3:
        mock_test_button = st.button("🧪 Run Mock Test", use_container_width=True)

    # Logic: Handle Clear
    if clear_button:
        st.session_state.messages = []
        st.session_state.mock_test_idx = -1
        st.rerun()

    # Logic: Handle Start Mock Test
    if mock_test_button:
        st.session_state.messages = []
        st.session_state.mock_test_idx = 0
        st.rerun()

    # Logic: Handle Manual Query
    if send_button and user_input.strip():
        with st.spinner("Analyzing data..."):
            try:
                rag_response = real_rag_query(user_input)
                st.session_state.messages.append({
                    'question': user_input,
                    'answer': rag_response['answer'],
                    'source_data': rag_response.get('source_data'),
                    'metadata': rag_response.get('metadata'),
                    'plots': rag_response.get('metadata', {}).get('plots', [])
                })
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()

    # Logic: Automated Mock Test Execution
    # This block ensures the spinner stays right here under the buttons
    if 0 <= st.session_state.mock_test_idx < len(MOCK_TEST_QUESTIONS):
        current_q = MOCK_TEST_QUESTIONS[st.session_state.mock_test_idx]
        
        with st.spinner(f"Running Mock Query {st.session_state.mock_test_idx + 1}/{len(MOCK_TEST_QUESTIONS)}..."):
            try:
                response = real_rag_query(current_q)
                st.session_state.messages.append({
                    'question': current_q,
                    'answer': response['answer'],
                    'source_data': response.get('source_data'),
                    'metadata': response.get('metadata'),
                    'plots': response.get('metadata', {}).get('plots', [])
                })
                st.session_state.mock_test_idx += 1
                st.rerun()
            except Exception as e:
                st.error(f"Mock test failed at query {st.session_state.mock_test_idx}: {e}")
                st.session_state.mock_test_idx = -1 # Stop on error
    
    elif st.session_state.mock_test_idx >= len(MOCK_TEST_QUESTIONS):
        st.success("✅ Mock test sequence completed successfully!")
        st.session_state.mock_test_idx = -1

# --- Conversation Display ---
st.markdown("---")

if not st.session_state.messages:
    st.info("👋 Welcome! Ask a question or run the mock test to get started.")
else:
    st.subheader(f"💬 Conversation ({len(st.session_state.messages)} queries)")
    
    # Display messages in reverse order (newest first)
    for idx, message in enumerate(reversed(st.session_state.messages)):
        message_number = len(st.session_state.messages) - idx
        
        with st.expander(f"Query #{message_number}: {message['question'][:60]}...", expanded=(idx == 0)):
            render_result_card(
                question=message['question'],
                answer=message['answer'],
                source_data=message.get('source_data'),
                metadata=message.get('metadata'),
                plots=message.get('plots'),
                card_index=message_number
            )