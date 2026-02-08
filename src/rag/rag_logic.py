import os
import json
import pandas as pd
from pathlib import Path
from mistralai import Mistral
from dotenv import load_dotenv
from .ingest import ChromaIngestor

from .tools import (
    get_gold_data_summary,
    execute_data_analysis,
    get_csv_tool_definition,
    generate_customer_visualization,
    get_viz_tool_definition
)

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")

class RAGOrchestrator:
    def __init__(self):
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "mistral-small-latest"

        self.vector_db = ChromaIngestor(db_path=DB_PATH)
        self.gold_summary = get_gold_data_summary()
        self.tools = [
            get_csv_tool_definition(),
            get_viz_tool_definition()
        ]
         
    def ask(self, user_query: str) -> dict:
        """Main entry point: Orchestrates the background context and agent loop."""
        try:
            # 1. Get background context (Policy documents)
            context, source_df = self._get_background_context(user_query)
            
            # 2. Prepare conversation state
            messages = self._initialize_messages(user_query, context)
            collected_plots = []

            # 3. Enter Agentic Loop
            for _ in range(3):
                response = self.client.chat.complete(
                    model=self.model,
                    messages=messages,
                    tools=self.tools
                )
                
                msg = response.choices[0].message
                messages.append(msg)

                if not msg.tool_calls:
                    break
                
                # 4. Process tool calls and update conversation
                turn_plots = self._process_tool_calls(msg.tool_calls, messages)
                collected_plots.extend(turn_plots)

            return {
                "answer": messages[-1].content,
                "source_data": source_df,
                "metadata": {
                    "method": "modular_agentic_rag",
                    "plots": collected_plots,
                    "steps": len(messages)
                }
            }

        except Exception as e:
            return self._handle_error(e)

    def _get_background_context(self, query: str):
        """Retrieves and formats policy data from the vector database."""
        results = self.vector_db.collection.query(query_texts=[query], n_results=3)
        context = "\n".join(results['documents'][0])
        source_df = pd.DataFrame([
            {"Source": m['source'], "Snippet": d[:75] + "..."} 
            for m, d in zip(results['metadatas'][0], results['documents'][0])
        ])
        return context, source_df

    def _initialize_messages(self, query: str, context: str, specific_data: str = "No records fetched yet.") -> list:
        #Constructs the initial system and user messages.
        system_content = f"""
        You are an AI Data Assistant for a Nordic financial firm. 
        You have access to two main knowledge sources:
        
        1. POLICY DOCUMENTS (Unstructured):
        {context}
        
        2. CUSTOMER DATA SUMMARY (Structured):
        {self.gold_summary}
        
        3. RELEVANT DATA RECORDS (Actual Evidence):
        {specific_data}
        
        INSTRUCTIONS:
        - If the user asks about a policy, cite the documents.
        - If the user asks about customer metrics or statistics, use the data summary.
        - If the user asks for a 'table' or 'summary', format your response clearly using Markdown.
        - Use Section 3 (RELEVANT DATA RECORDS) to answer specific questions about customers.
        - Cross-reference these records with Section 1 (POLICY) to see if the customer violates any rules.
        - Be concise and professional.
        """
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]

    def _process_tool_calls(self, tool_calls, messages: list) -> list:
        #Iterates through tool calls, executes them, and updates message history
        plots = []
        data_evidence = ""
        for call in tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            
            if name == "execute_data_analysis":
                result = execute_data_analysis(**args)
                data_evidence += f"\n--- Data from {args['table_name']} ---\n{result}"
            elif name == "generate_customer_visualization":
                fig = generate_customer_visualization(**args)
                plots.append(fig)
                result = f"Generated {args['plot_type']} plot for customer {args['customer_id']}."
            
            messages.append({
                "role": "tool", "name": name, 
                "content": str(result), "tool_call_id": call.id
            })
        return plots

    def _handle_error(self, e: Exception) -> dict:
        # Error handling
        return {
            "answer": f"Agent error: {str(e)}",
            "source_data": pd.DataFrame(),
            "metadata": {"status": "error"}
        }