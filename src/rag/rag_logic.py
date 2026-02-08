import os
import json
import pandas as pd
from pathlib import Path
from openai import OpenAI
from google import genai
from mistralai import Mistral
from google.genai import types
from dotenv import load_dotenv
from .ingest import ChromaIngestor

from .data_tool import (
    get_gold_data_summary, 
    execute_data_analysis, 
    get_csv_tool_definition
)

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
        self.tools = [get_csv_tool_definition()]
    
    def ask(self, user_query: str) -> dict:
        """
        Main entry point. Decides whether to use analytical tools 
        or vector-based policy retrieval.
        """
        try:
            # 1. Route the query: Does the LLM need a tool?
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": user_query}],
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message

            # 2. Branch A: Structured Data Analysis (Tool Calling)
            if message.tool_calls:
                return self._handle_tool_execution(user_query, message)

            # 3. Branch B: Unstructured Policy Retrieval (Standard RAG)
            return self._handle_vector_search(user_query)

        except Exception as e:
            return {
                "answer": f"I encountered an error processing your request: {str(e)}",
                "source_data": pd.DataFrame(),
                "metadata": {"status": "error"}
            }

    def _handle_tool_execution(self, query: str, message) -> dict:
        """Executes Python logic for data analysis and returns the LLM interpretation."""
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        
        # Execute the Pandas logic
        analysis_result = execute_data_analysis(**args)
        
        # Final pass to summarize results for the user
        final_response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "user", "content": query},
                message,
                {
                    "role": "tool", 
                    "name": tool_call.function.name, 
                    "content": analysis_result, 
                    "tool_call_id": tool_call.id
                }
            ]
        )
        
        return {
            "answer": final_response.choices[0].message.content,
            "source_data": pd.DataFrame({"Operation": [args.get("query_type")], "Scope": [args.get("table_name")]}),
            "metadata": {"method": "structured_tool_analysis", "tool": tool_call.function.name}
        }

    def _handle_vector_search(self, query: str) -> dict:
        """Performs vector search on policy docs and generates an answer."""
        search_results = self.vector_db.collection.query(query_texts=[query], n_results=3)
        
        docs = search_results['documents'][0]
        metas = search_results['metadatas'][0]
        
        context = "\n".join(docs)
        source_df = pd.DataFrame([
            {"Source": m['source'], "Snippet": d[:75] + "..."} 
            for m, d in zip(metas, docs)
        ])

        system_prompt = f"""
        You are a Nordic Finance Assistant. 
        Use the following context to answer the user:
        
        POLICY CONTEXT:
        {context}
        
        DATA SCHEMA INFO:
        {self.gold_summary}
        
        If the answer isn't in the context, say you don't know.
        """

        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )

        return {
            "answer": response.choices[0].message.content,
            "source_data": source_df,
            "metadata": {"method": "vector_rag", "sources_found": len(docs)}
        }
