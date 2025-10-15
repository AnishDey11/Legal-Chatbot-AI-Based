import streamlit as st
import os

# For deployment, Streamlit secrets are used.
# For local development, it falls back to environment variables.
# Create a .env file locally with your keys (e.g., OPENAI_API_KEY="sk-...")
# Or set them as environment variables in your system.

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", os.getenv("PINECONE_API_KEY"))
