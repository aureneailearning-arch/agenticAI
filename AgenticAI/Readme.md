# Azure OpenAI Chatbot with Streamlit

This project creates a simple chatbot UI using Streamlit and Azure OpenAI.

## Requirements

- Python 3.9+
- An Azure OpenAI resource
- A deployed chat model in Azure OpenAI



## Setup

1. Install the dependencies:
   python -m venv .venv
   .\.venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

2. Create .env file and Update the values in the `.env` file with your Azure OpenAI settings and postgres password:
  AZURE_OPENAI_ENDPOINT=""
   AZURE_OPENAI_API_KEY=""
   AZURE_OPENAI_API_VERSION=""
   AZURE_OPENAI_DEPLOYMENT="model-router"
   POSTGRES_PASSWORD=""
   EMBEDDINGS_MODEL="text-embedding-3-small"
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small"
   EMBEDDING_API_VERSION="2025-01-01-preview"

3. Run the app:
   ```bash
   streamlit run app.py  //for normal chat bot
   streamlit run app_rag.py //for RAG chatbot
   ```

4. Open the local URL shown in the terminal.

## Notes

- Make sure your Azure OpenAI deployment is created and accessible.
- The app uses the chat completions API with a simple prompt and response flow.
