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


### Part 2 – Feature Engineering + Simple Logic
For this section, I chose to focus on **Feature Engineering** rather than building a rule-based classifier or a lightweight model. 

After spending a good amount of time in the data exploration phase, I had a clear picture of which metrics would actually be useful. I decided to attach these features directly to each customer profile. This way, the RAG system doesn't just have access to raw text; it can easily "grab" summarized behavioral data like; spending habits or frequency, to give much more informed and context-aware answers.

I chose this path to keep the solution clean and effective without overcomplicating things just for the sake of it. It’s about giving the AI the best possible "cheat sheet" to understand the customer.

| Feature Name | Logic Description | Business Rationale |
| :--- | :--- | :--- |
| **is_currency_imputed** | Indicates if the original currency was missing and estimated. | **Financial Accuracy:** **Data Integrity:** Allows users to filter for raw data vs. estimated values when high precision is required. |
| **total_spend_eur** | Aggregate transaction volume normalized to EUR using fixed exchange rates. | **Revenue Impact:** Identifies high-value accounts and drives customer tiering. |
| **avg_transaction_value** | The mean EUR value per purchase. | **Behavioral Analysis:** Distinguishes between frequent low-cost buyers and occasional high-ticket shoppers. |
| **recency_days** | Days elapsed since the user's last transaction (relative to the dataset's max date). | **Retention:** Primary indicator for churn risk or "sleeping" accounts. |
| **transaction_frequency** | Total lifetime transaction count for the customer. | **Engagement:** Measures platform stickiness and long-term user loyalty. |
| **high_ticket_user** | Boolean flag for any single transaction exceeding €500. | **Compliance:** Automatically triggers the "manual review" workflow required by our product policy. |
| **frequent_transactor** | Boolean flag for users in the top 10% by transaction volume. | **Risk Management:** Highlights outlier behavior that may warrant a closer look for fraud prevention. |
| **cross_border_count** | Count of transactions where the currency does not match the user's home country. | **Fraud Detection:** Key metric for flagging high-risk international activity patterns. |
| **preferred_category** | The most frequent category assigned to the user (excluding "uncategorized"). | **Customer Support:** Enables LLM-driven support agents to prioritize the correct policy sections (e.g., Electronics) instantly. |


### Part 3&4 - LLM Pipeline and output 

**Architectural Approach: Agentic RAG**
For this component, I moved beyond a standard RAG pipeline to build an **Agentic RAG**. My primary goal was to bridge the gap between our unstructured documents (FAQs, fraud guidelines, and product policies) and our structured customer data.

While standard RAG is great for simple Q&A, it struggles when a question requires looking at a document *and* calculating numbers from a dataset simultaneously. By using an agentic framework, the system can "decide" which tool to use based on the user's intent.


#### 1. The Toolset: Bridging Structured and Unstructured Data
To make the RAG truly agentic, I provided it with specific capabilities it can call upon depending on the prompt:
* **Knowledge Retrieval:** For answering "What is our policy on...?"
* **CSV Analysis Tool:** To query the structured Silver-layer features we engineered (like `cross_border_count` or `high_ticket_user`).
* **Visualization Tool:** To transform raw numbers into tables or plots that make business decisions easier to visualize.

#### 2. Reasoning in Action
The real value of this setup is its ability to synthesize information. If an end-user asks whether a specific customer should be flagged for fraud, the agent doesn't just guess. It follows a logical path:
1.  **Retrieve:** It pulls the "Fraud Prevention" guidelines to identify high-risk triggers.
2.  **Query:** It uses the CSV tool to check if the customer’s `frequent_transactor` flag or `total_spend_eur` matches those triggers.
3.  **Conclude:** It provides a data-backed recommendation based on company policy.

---


## Reflections and Future Roadmap

#### Key Assumptions & Trade-offs

* **Latency vs. Capability:** The biggest trade-off I encountered was the "Agent Tax." By moving from a simple retrieval system to an Agentic RAG, response times increased. The LLM now has to perform multiple "reasoning loops" to decide which tool to use before actually answering.
* **Accuracy vs. Complexity:** While the agent can now perform complex tasks like data visualization and CSV querying, the "surface area" for errors is larger. More tools mean more opportunities for the LLM to get confused or return a "cannot answer" response if the tool output doesn't perfectly match its expectations.



#### What I would improve with more time

If I were to take this from a prototype to a production-grade system, these would be my next steps:

* **Advanced Prompt Engineering & Few-Shot Prompting:** Currently, the agent relies on general instructions. I would implement "Few-Shot" examples in the system prompt—essentially giving the agent a library of "Correct" reasoning paths to follow. This would significantly reduce the "I cannot answer that" occurrences.
* **Robust ETL & Orchestration:** I would move the local processing script into a proper orchestration tool (like Airflow or Databricksr). This would allow for automated data quality checks, schema enforcement and secure handling before it ever hits the vector store.
* **Fine-tuned Embedding Models:** I would move beyond the default Mistral embeddings to a model fine-tuned on financial/fraud-specific terminology to improve the retrieval accuracy of our "Product Policy" chunks.
