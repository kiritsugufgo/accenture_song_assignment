import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
import matplotlib.pyplot as plt

def render_result_card(
    question: str,
    answer: str,
    source_data: Optional[pd.DataFrame] = None,
    metadata: Optional[Dict[str, Any]] = None,
    plots: Optional[List[plt.Figure]] = None,
    card_index: int = 0
):
    """
    Render a result card showing question, answer, and source data.
    
    Args:
        question: The user's question
        answer: The RAG-generated answer
        source_data: Optional DataFrame showing data sources used
        metadata: Optional dict with additional metadata
        plots: Optional list of matplotlib figures for visual analysis
        card_index: Index for unique identification
    """
    with st.container():
        # Card styling
        st.markdown(
            """
            <style>
            .result-card {
                padding: 1.5rem;
                border-radius: 0.5rem;
                background-color: #f8f9fa;
                margin-bottom: 1rem;
            }
            .question-text {
                color: #1f77b4;
                font-weight: 600;
                font-size: 1.1rem;
            }
            .answer-text {
                margin-top: 1rem;
                line-height: 1.6;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Question section
        st.markdown(f'<div class="question-text">❓ Question:</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="padding-left: 1.5rem; margin-top: 0.5rem;">{question}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Answer section
        st.markdown(f'<div class="question-text">💡 Answer:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-text" style="padding-left: 1.5rem;">{answer}</div>', unsafe_allow_html=True)
        
        # Source data section (if provided)
        if source_data is not None and not source_data.empty:
            st.markdown("---")
            st.markdown(f'<div class="question-text">📊 Data Sources Used:</div>', unsafe_allow_html=True)
            st.markdown('<div style="padding-left: 1.5rem; margin-top: 0.5rem;">', unsafe_allow_html=True)
            
            # Display the dataframe
            st.dataframe(
                source_data,
                use_container_width=True,
                hide_index=False
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
     
        if plots:
            st.markdown("---")
            st.markdown(f'<div class="question-text">📈 Visual Analysis:</div>', unsafe_allow_html=True)
            for i, fig in enumerate(plots):
                # Temporarily resize figure for display without mutating stored figure state
                orig_size = fig.get_size_inches().copy()
                fig.set_size_inches(orig_size[0] * 0.5, orig_size[1] * 0.5)
                st.pyplot(fig, clear_figure=False)
                fig.set_size_inches(orig_size[0], orig_size[1])
                 
        # Metadata section (if provided)
        if metadata:
            with st.expander("ℹ️ Additional Information"):
                for key, value in metadata.items():
                    st.write(f"**{key}:** {value}")