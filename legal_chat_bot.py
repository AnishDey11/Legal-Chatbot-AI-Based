from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from chatbot_system_template import SYSTEM_TEMPLATE
from langchain.schema import AIMessage, HumanMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import OPENAI_API_KEY, PINECONE_API_KEY

# Your Pinecone index
INDEX_NAME = "legal-chatbot-index"


def create_rag_chain():
    print("Loading RAG chain resources...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.3, api_key=OPENAI_API_KEY)
    vectorstore = PineconeVectorStore.from_existing_index(index_name=INDEX_NAME, embedding=embeddings)
    print("Connected to Pinecone vectorstore")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    print("Retriever created")

    # Updated prompt to handle chat history
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_TEMPLATE + "\n\nUse the following retrieved context:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    question_answer_chain = create_stuff_documents_chain(llm, final_prompt)
    ragChain = create_retrieval_chain(retriever, question_answer_chain)
    print("RAG chain loaded successfully")
    return ragChain


def ask_query(ragChain, user_query, chat_history):
    # Convert chat history from Streamlit's dict format to LangChain's Message format
    formatted_history = []
    for msg in chat_history:
        if msg["role"] == "user":
            formatted_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            formatted_history.append(AIMessage(content=msg["content"]))

    response = ragChain.invoke({
        "input": user_query,
        "chat_history": formatted_history
    })
    return response["answer"]
