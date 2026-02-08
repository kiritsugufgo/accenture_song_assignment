# Song Data & AI Take-Home Assignment

## Technical Stack

* **Language:** Python 3.11
* **Data Processing:** Pandas
* **Vector Database:** ChromaDB
* **LLM Provider:** Mistral AI (via API)
* **Visualization:** Matplotlib, Seaborn
* **User Interface:** Streamlit

---

## How to run this project

### Environment Setup
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
```
If the application starts successfully, you will see the interface shown below. In this dashboard, you can interact with the RAG system to ask questions regarding internal policy documents or view insights related to customers and transactions.
<img width="1890" height="939" alt="image" src="https://github.com/user-attachments/assets/37fbd3ea-6e31-4c65-a5f2-d158edee03b8" />

---

## Key assumptions and trade-offs

### Part 1 – Data Pipeline & ETL
After spending some time exploring the raw data, I made a few specific calls to ensure the final dataset was clean enough for the RAG and analytics components.

### Customers
For the customer data, I kept things lean. I implemented basic type-checking to ensure everything is in the right format. If a new CSV is uploaded with broken schemas, the pipeline is set to throw an error early so we don't process "garbage" data further down the line.

### Transactions
This is where most of the cleanup happened. Here’s the logic behind my choices:
* **Missing Customer IDs:** I decided to remove any rows where the `customer_id` was missing. Since we can’t reliably link these transactions back to a specific person, keeping them would likely skew our customer-level insights.
* **The Currency "Puzzle":** I noticed about 25,000 rows had missing currency values. Looking at the distribution, I saw other Scandinavian currencies represented, but **DKK** was missing entirely. I made the assumption that these missing values were meant to be DKK and imputed them accordingly. I also made sure to normalize everything (like turning `eur` into `EUR`) so the grouping works correctly later.
* **Handling Categories:** Right now, the data mainly sits in `food` and `electronics`. I standardized these to lowercase. For any missing or weird category values, I labeled them as `unknown` rather than guessing. In a real consulting scenario, I'd rather have an "Unknown" bucket than misclassify a customer's spending habits.
* **Timestamps:** I ensured all dates are valid and parsed correctly so we can trust any time-based reporting.
* **Handling Categories:** I noticed the data primarily falls into `food` and `electronics`, so I standardized those to lowercase to keep things neat. For any missing or blank values, I chose to label them as `unknown` rather than trying to force them into a category. My reasoning here is that in a real-world project, these transactions could easily belong to categories we haven't defined yet (like "Utilities" or "Transport") and I'd rather be transparent about the gaps in the data than guess and get it wrong.
  
The plots below show some of the "behind the scenes" looks at the data that helped me reach these conclusions.
<img width="999" height="527" alt="image" src="https://github.com/user-attachments/assets/d788027d-7298-4c51-a35b-fa3f8416b30f" />
<img width="790" height="396" alt="image" src="https://github.com/user-attachments/assets/07f4084e-4646-404b-8488-0cba15f598e2" />

The ETL pipeline in this project was built with a clear focus: making sure the transaction data comes out clean and that the customer profiles have the correct data types.
