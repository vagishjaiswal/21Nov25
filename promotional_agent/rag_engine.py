import os
from typing import List, Tuple, Dict
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from config import SystemPrompts

load_dotenv()

class RAGEngine:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to vector store"""
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [f"doc_{i}" for i in range(len(self.collection.get()['ids']), len(self.collection.get()['ids']) + len(texts))]
        
        # Generate embeddings
        embeddings = self._get_embeddings(texts)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, question: str, top_k: int = 5) -> Tuple[str, List[str]]:
        """Query the RAG system"""
        # Get question embedding
        question_embedding = self._get_embeddings([question])[0]
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        
        # Extract relevant documents
        if not results['documents'] or not results['documents'][0]:
            return "I couldn't find any relevant information in the uploaded documents.", []
        
        context_docs = results['documents'][0]
        
        # Check guardrails
        if not SystemPrompts.check_guardrails(question):
            return SystemPrompts.get_guardrail_response(), []
        
        # Build context
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        
        # Generate answer
        answer = self._generate_answer(question, context)
        
        return answer, context_docs
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using GPT-4 with dynamically loaded prompt"""
        messages = [
            {"role": "system", "content": SystemPrompts.get_system_prompt()},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def clear_database(self):
        """Clear all documents from the database"""
        try:
            self.chroma_client.delete_collection("documents")
            self.collection = self.chroma_client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error clearing database: {e}")
