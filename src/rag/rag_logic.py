import os
from pathlib import Path
import pandas as pd
from openai import OpenAI
from google import genai
from mistralai import Mistral
from google.genai import types
from dotenv import load_dotenv
from .ingest import ChromaIngestor

from .data_tool import get_gold_data_summary

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")

class RAGOrchestrator:
    def __init__(self):
        #self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        #self.model = "gpt-4o-mini" 
        #self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        #self.model = "gemini-2.0-flash-lite"
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "mistral-small-latest"
        self.vector_db = ChromaIngestor(db_path=DB_PATH)
        self.gold_summary = get_gold_data_summary()

    def ask(self, user_query: str):
        """Main entry point for the RAG pipeline."""
        
        # Retrieve Unstructured Context (Policies)
        search_results = self.vector_db.collection.query(
            query_texts=[user_query],
            n_results=3
        )
        # Extract content and sources for the UI
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        policy_context = "\n".join(documents)
        
        # Create a simple DataFrame of sources for the Streamlit UI
        source_df = pd.DataFrame([
            {"Source": m['source'], "Content Snippet": d[:50] + "..."} 
            for m, d in zip(metadatas, documents)
        ]) 

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
            # Use OpenAI's LLM 
            # response = self.client.chat.completions.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": user_query}
            #     ],
            #     temperature=0.1 
            # )
            
            # # Return a dictionary that matches your Streamlit 'real_rag_query' logic
            # return {
            #     "answer": response.choices[0].message.content,
            #     "source_data": source_df,
            #     "metadata": {"Model": self.model, "Sources Found": len(documents)}
            # }
            # Use Gemini
            # response = self.client.models.generate_content(
            #     model=self.model,
            #     contents=user_query,
            #     config=types.GenerateContentConfig(
            #         system_instruction=system_prompt, # Move your system_prompt here
            #         temperature=0.1
            #     )
            # )
            
            # return {
            #     "answer": response.text,
            #     "source_data": source_df,
            #     "metadata": {"Model": self.model, "Sources Found": len(documents)}
            # }
            # Use Mistral
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1 
            )
            
            return {
                "answer": response.choices[0].message.content,
                "source_data": source_df,
                "metadata": {"Model": self.model, "Sources Found": len(documents)}
            }
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "source_data": pd.DataFrame(), "metadata": {}}