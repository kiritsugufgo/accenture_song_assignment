# Song Data & AI Take-Home Assignment

## Project Overview

The solution is divided into three core components:
* **Data Engineering (ETL):** Processing and cleaning `customers.csv` and `transactions.csv` using Pandas to create a reliable foundation for analytics.
* **Feature Engineering:** Deriving customer-level behavioral metrics and identifying patterns 
* **AI Services (RAG):** An LLM-powered assistant utilizing **ChromaDB** for vector embeddings to provide grounded answers based on internal policy documents.

## Technical Stack

* **Language:** Python 3.11
* **Data Processing:** Pandas
* **Vector Database:** ChromaDB
* **LLM Provider:** Mistral AI (via API)
* **Visualization:** Matplotlib, Seaborn
* **User Interface:** Streamlit

---

## Getting Started

### 1. Environment Setup
Create a virtual environment and install the necessary dependencies to ensure a clean workspace.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

### 2. Configuration
The project requires a Mistral AI API key to power the RAG component. 
Create a .env file in the root directory and add your credentials:


MISTRAL_API_KEY=your_api_key_here

### 3. Running the Pipeline
The core ETL and data processing logic is handled through main source file. Run this to process the raw data and prepare the vector store. 

python src/main.py

### 4. Launch the UI
A Streamlit-based interfact is provided to interact with the RAG pipeline. This allows for both live LLM queries and mock testing

streamlit run src/app/streamlit_app.py

---

### Part 1 - Data Pipeline & ETL
