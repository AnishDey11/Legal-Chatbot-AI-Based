# Legal-Chatbot-AI-Based
# AI-Based Legal Reference and Case Retrieval System

This project is a sophisticated legal chatbot built with Streamlit and powered by a Retrieval-Augmented Generation (RAG) pipeline. It provides a secure, user-specific interface where users can ask legal questions and receive answers based on a custom knowledge base of legal documents.

---

## ✨ Features

-   **User Authentication**: Secure sign-up, sign-in, and sign-out functionality.
-   **User Profiles**: Users can view and update their profile information.
-   **Persistent Chat History**: Chat sessions are saved per user and can be revisited or deleted.
-   **RAG-Powered Chatbot**: Utilizes a LangChain RAG pipeline to provide contextually accurate answers from a private collection of legal documents.
-   **Vector Search**: Employs Pinecone as a vector database for efficient document retrieval.
-   **Modern UI**: A clean and responsive user interface built with Streamlit.

---

## 🛠️ Technology Stack

-   **Frontend**: Streamlit
-   **Backend & Core Logic**: Python
-   **LLM Orchestration**: LangChain
-   **Language Model**: OpenAI `gpt-3.5-turbo`
-   **Embeddings**: HuggingFace `sentence-transformers`
-   **Vector Database**: Pinecone
-   **User & Chat Database**: SQLite

---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

-   Python 3.8+
-   An [OpenAI API Key](https://platform.openai.com/api-keys)
-   A [Pinecone API Key](https://www.pinecone.io/)

### 2. Installation & Setup

**1. Clone the repository:**
```bash
git clone <your-repository-url>
cd <repository-folder>
```

**2. Create and activate a virtual environment:**
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install the required dependencies:**
Create a file named `requirements.txt` with the content below and run `pip install -r requirements.txt`.
```text
# requirements.txt
streamlit
langchain
langchain-openai
langchain-community
langchain-pinecone
pinecone-client
datasets
sentence-transformers
pypdf
python-docx
unstructured
tiktoken
```
```bash
pip install -r requirements.txt
```

**4. Configure API Keys:**
Create a file named `config.py` in the root directory and add your API keys:
```python
# config.py
OPENAI_API_KEY = "sk-..."
PINECONE_API_KEY = "..."
```

**5. Prepare Your Knowledge Base:**
Create a folder named `Legal_Chatbot_Inputs` in the root directory and place your legal documents (`.pdf`, `.docx`, `.txt`, `.html`) inside it.

### 3. Running the Application

**1. Populate the Vector Database:**
Run the `datasets_utils.py` script once to process your documents and load them into your Pinecone index. This may take some time depending on the number and size of your documents.
```bash
python datasets_utils.py
```

**2. Launch the Streamlit App:**
Once the data processing is complete, run the main application.
```bash
streamlit run app.py
```
Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

---

## 📂 Project Structure

```
.
├── Legal_Chatbot_Inputs/ # Folder for your source documents
├── app.py                # Main Streamlit application file (UI and routing)
├── auth_pages.py         # UI functions for sign-in, sign-up, profile
├── auth_utils.py         # Backend functions for DB and user management
├── legal_chat_bot.py     # RAG chain creation and query logic
├── datasets_utils.py     # Script to process docs and update Pinecone
├── chatbot_system_template.py # System prompt for the LLM
├── config.py             # (You create this) Stores API keys
├── users.db              # (Auto-generated) SQLite database
├── bg.jpg                # Background image for the UI
├── requirements.txt      # List of Python dependencies
└── README.md             # Project documentation
```
