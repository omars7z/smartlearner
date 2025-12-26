from typing import Dict, Any, List
from app.core.base_agent import BaseAgent
from app.core.config import settings

# LangChain Imports
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

# FIX: Try importing from the new location first, fall back to old
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="rag_retriever_01")
        
        # 1. Initialize Embeddings
        # Ensure your OPENAI_API_KEY is set in .env
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        
        # 2. Mock Knowledge Base (In prod, this loads PDFs/DBs)
        raw_docs = [
            "Recursion is a programming technique where a function calls itself.",
            "The base case is crucial in recursion to prevent infinite loops.",
            "Python's recursion limit is usually 1000 stack frames.",
            "Memoization is an optimization technique used to speed up computer programs."
        ]
        
        # 3. Process & Index Documents
        docs = [Document(page_content=text) for text in raw_docs]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        splits = text_splitter.split_documents(docs)
        
        # 4. Create Vector Store (ChromaDB in-memory for this demo)
        self.vector_store = Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings,
            collection_name="smartlearner_knowledge"
        )
        
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = data.get("query", "")
        if not query:
            return {"retrieved_docs": []}

        # Use LangChain Retriever
        docs = self.retriever.invoke(query)
        
        # Convert Documents to string list for the next agent
        doc_contents = [doc.page_content for doc in docs]
        return {"retrieved_docs": doc_contents}