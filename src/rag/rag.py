import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from .ingest import ChromaIngestor
from .data_tool import get_gold_data_summary

load_dotenv()

class RAGOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_db = ChromaIngestor()
        self.gold_summary = get_gold_data_summary()
        self.model = "gpt-4o-mini" 

    def ask(self, user_query: str):
        """Main entry point for the RAG pipeline."""
        
        # Retrieve Unstructured Context (Policies)
        search_results = self.vector_db.collection.query(
            query_texts=[user_query],
            n_results=3
        )
        policy_context = "\n".join(search_results['documents'][0])

        # Build the System Prompt
        # give the LLM BOTH the Policy context and the Data summary
        system_prompt = f"""
        You are an AI Data Assistant for a Nordic financial firm. 
        You have access to two main knowledge sources:
        
        1. POLICY DOCUMENTS (Unstructured):
        {policy_context}
        
        2. CUSTOMER DATA SUMMARY (Structured):
        {self.gold_summary}
        
        INSTRUCTIONS:
        - If the user asks about a policy, cite the documents.
        - If the user asks about customer metrics or statistics, use the data summary.
        - If the user asks for a 'table' or 'summary', format your response clearly using Markdown.
        - Be concise and professional.
        """

        # Get Completion from ChatGPT
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1 
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"