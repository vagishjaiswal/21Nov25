"""
Retail RAG Engine - Query engine for retail promotional messages
"""

import os
from typing import List, Tuple, Dict
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from retail_config import RetailSystemPrompts

load_dotenv()


class RetailRAGEngine:
    """RAG Engine specifically designed for retail promotional messages"""
    
    def __init__(self, persist_directory: str = "./retail_vector_dbs", collection_name: str = "retail_collection", business_id: str = None):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.business_id = business_id
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to vector store"""
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Get current count for ID generation
        current_count = len(self.collection.get()['ids'])
        ids = [f"{self.collection_name}_doc_{i}" for i in range(current_count, current_count + len(texts))]
        
        # Generate embeddings
        embeddings = self._get_embeddings(texts)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, question: str, top_k: int = 8) -> Tuple[str, List[str]]:
        """Query the retail RAG system for promotional message generation"""
        
        # Get question embedding
        question_embedding = self._get_embeddings([question])[0]
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        
        # Extract relevant documents
        if not results['documents'] or not results['documents'][0]:
            return "I don't have enough information to create a promotional message. Please ensure data is loaded.", []
        
        context_docs = results['documents'][0]
        
        # Check guardrails
        if not RetailSystemPrompts.check_guardrails(question, self.business_id):
            return RetailSystemPrompts.get_guardrail_response(self.business_id), []
        
        # Build context
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        
        # Generate promotional message
        message = self._generate_promotional_message(question, context)
        
        return message, context_docs
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def _generate_promotional_message(self, question: str, context: str) -> str:
        """Generate promotional message using GPT-4 with Indian retail context"""
        
        messages = [
            {"role": "system", "content": RetailSystemPrompts.get_system_prompt(self.business_id)},
            {"role": "user", "content": f"""Context from Business Data:
{context}

Customer Request:
{question}

Generate a creative, personalized promotional message based on the above information.
"""}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.8,  # Higher temperature for more creative messages
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def clear_database(self):
        """Clear all documents from the database"""
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error clearing database: {e}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        all_data = self.collection.get()
        
        stats = {
            "total_documents": len(all_data['ids']),
            "document_types": {}
        }
        
        # Count by type
        for metadata in all_data['metadatas']:
            if metadata and 'type' in metadata:
                doc_type = metadata['type']
                stats['document_types'][doc_type] = stats['document_types'].get(doc_type, 0) + 1
        
        return stats
