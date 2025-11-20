"""
Module 2: AI Agent Engine
Hackathon Framework - Generic Conversational AI with Multi-modal Support

FEATURES:
- Document processing (PDF, DOCX, TXT)
- Image analysis (OCR + Vision AI)
- RAG with vector search
- Dynamic prompt loading
- Safety guardrails
"""

import os
import re
import base64
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv
import json

# Core AI imports
from openai import OpenAI
import chromadb
from chromadb.config import Settings

# Document processing
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
import io

load_dotenv()

# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

class ConfigLoader:
    """Load and manage dynamic configuration from markdown files"""
    
    def __init__(self, config_file: str = "SYSTEM_PROMPTS.md"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from markdown file"""
        if not self.config_file.exists():
            print(f"⚠️ {self.config_file} not found. Using defaults.")
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config = {
                'system_prompt': self._extract_section(content, 'Full Prompt'),
                'guardrail_response': self._extract_section(content, 'Guardrail Response'),
                'prohibited_patterns': self._extract_list(content, 'Prohibited Patterns'),
                'image_analysis_prompt': self._extract_section(content, 'Image Analysis Prompt') or "Describe this image in detail.",
            }
            
            print("✅ Configuration loaded successfully")
            return config
        
        except Exception as e:
            print(f"⚠️ Error loading config: {e}. Using defaults.")
            return self._get_default_config()
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a code block section from markdown"""
        pattern = rf"### {section_name}.*?```\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract a list from markdown"""
        pattern = rf"### {section_name}(.*?)(?=###|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            list_content = match.group(1)
            items = re.findall(r'^[-*]\s+(.+)$', list_content, re.MULTILINE)
            return [item.strip() for item in items]
        
        return []
    
    def _get_default_config(self) -> Dict:
        """Fallback default configuration"""
        return {
            'system_prompt': """You are an intelligent AI assistant that helps users with their questions.

Your responsibilities:
1. Answer questions accurately based on provided context
2. Be clear when information is not available
3. Maintain a helpful and professional tone
4. Cite sources when providing information

Remember: Only use information from the provided context.""",
            
            'guardrail_response': """I'm designed to help with legitimate questions and tasks. I cannot assist with:
- Harmful, illegal, or unethical requests
- Generating misleading information
- Requests that violate privacy or security

Please ask something I can help with.""",
            
            'prohibited_patterns': [
                "hack", "exploit", "illegal", "harmful", "dangerous",
                "weapon", "drug", "violence", "fraud"
            ],
            
            'image_analysis_prompt': "Describe this image in detail, including any text, diagrams, or important visual elements."
        }
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()
        print("✅ Configuration reloaded")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

# ============================================================================
# GUARDRAILS SYSTEM
# ============================================================================

class Guardrails:
    """Safety and validation system"""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.prohibited_patterns = config.get('prohibited_patterns', [])
        self.guardrail_response = config.get('guardrail_response', "I cannot help with that request.")
    
    def validate(self, query: str) -> bool:
        """Check if query passes all guardrails"""
        query_lower = query.lower()
        
        # Check prohibited patterns
        for pattern in self.prohibited_patterns:
            if pattern in query_lower:
                print(f"⚠️ Guardrail triggered: {pattern}")
                return False
        
        # Check for prompt injection attempts
        manipulation_patterns = [
            "ignore previous instructions",
            "disregard your instructions",
            "forget your role",
            "act as if",
            "pretend you are",
            "jailbreak",
            "dan mode"
        ]
        
        for pattern in manipulation_patterns:
            if pattern in query_lower:
                print(f"⚠️ Prompt injection detected: {pattern}")
                return False
        
        return True
    
    def get_response(self) -> str:
        """Get guardrail violation response"""
        return self.guardrail_response

# ============================================================================
# DOCUMENT PROCESSOR
# ============================================================================

class DocumentProcessor:
    """Process multiple document formats"""
    
    def __init__(self, client: OpenAI, config: ConfigLoader):
        self.client = client
        self.config = config
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.ocr_enabled = True
        
        # Try to configure Tesseract
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Configure Tesseract OCR"""
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract found at: {path}")
                return
        
        print("⚠️ Tesseract not found. OCR disabled.")
        self.ocr_enabled = False
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process document based on file type"""
        ext = Path(file_path).suffix.lower()
        
        processors = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.doc': self._process_docx,
            '.txt': self._process_txt,
            '.png': self._process_image,
            '.jpg': self._process_image,
            '.jpeg': self._process_image,
        }
        
        processor = processors.get(ext)
        if not processor:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return processor(file_path)
    
    def _process_pdf(self, file_path: str) -> List[Dict]:
        """Extract text and images from PDF"""
        chunks = []
        
        # Extract text
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        if full_text.strip():
            chunks.extend(self._chunk_text(full_text, {"source": file_path, "type": "text"}))
        
        # Extract images
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            images = page.get_images()
            for img_idx, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    description = self._analyze_image(image_bytes)
                    if description:
                        chunks.append({
                            "text": f"[IMAGE DESCRIPTION] {description}",
                            "metadata": {
                                "source": file_path,
                                "page": page_num + 1,
                                "type": "image"
                            }
                        })
                except Exception as e:
                    print(f"⚠️ Error processing image: {e}")
        
        return chunks
    
    def _process_docx(self, file_path: str) -> List[Dict]:
        """Extract text from DOCX"""
        doc = DocxDocument(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        
        if full_text.strip():
            return self._chunk_text(full_text, {"source": file_path, "type": "text"})
        return []
    
    def _process_txt(self, file_path: str) -> List[Dict]:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        return self._chunk_text(text, {"source": file_path, "type": "text"})
    
    def _process_image(self, file_path: str) -> List[Dict]:
        """Process standalone image"""
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        description = self._analyze_image(image_data)
        if description:
            return [{
                "text": f"[IMAGE DESCRIPTION] {description}",
                "metadata": {"source": file_path, "type": "image"}
            }]
        return []
    
    def _analyze_image(self, image_bytes: bytes) -> str:
        """Analyze image with OCR and/or Vision AI"""
        results = []
        
        # Try OCR first
        if self.ocr_enabled:
            try:
                image = Image.open(io.BytesIO(image_bytes))
                ocr_text = pytesseract.image_to_string(image).strip()
                if ocr_text:
                    results.append(f"[OCR TEXT]\n{ocr_text}")
            except Exception as e:
                print(f"⚠️ OCR failed: {e}")
        
        # Vision AI analysis
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.config.get('image_analysis_prompt')},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            vision_description = response.choices[0].message.content
            if vision_description:
                results.append(f"[VISUAL ANALYSIS]\n{vision_description}")
        
        except Exception as e:
            print(f"⚠️ Vision AI failed: {e}")
        
        return "\n\n".join(results)
    
    def _chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "metadata": metadata.copy()
                })
        
        return chunks

# ============================================================================
# RAG ENGINE
# ============================================================================

class RAGEngine:
    """Retrieval-Augmented Generation engine"""
    
    def __init__(self, client: OpenAI, persist_dir: str = "./chroma_db"):
        self.client = client
        self.persist_dir = persist_dir
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to vector store"""
        if not chunks:
            return
        
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self._get_embeddings(texts)
        
        # Generate IDs
        current_count = len(self.collection.get()['ids'])
        ids = [f"doc_{current_count + i}" for i in range(len(texts))]
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(chunks)} chunks to vector store")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant documents"""
        query_embedding = self._get_embeddings([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if results['documents'] and results['documents'][0]:
            return results['documents'][0]
        
        return []
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def clear(self):
        """Clear all documents"""
        try:
            self.chroma_client.delete_collection("documents")
            self.collection = self.chroma_client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Vector store cleared")
        except Exception as e:
            print(f"⚠️ Error clearing vector store: {e}")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        data = self.collection.get()
        
        stats = {
            'total_records': len(data['ids']),
            'chunks': sum(1 for m in data['metadatas'] if m and m.get('type') == 'text'),
            'images': sum(1 for m in data['metadatas'] if m and m.get('type') == 'image'),
        }
        
        return stats
    
    def get_all_records(self) -> List[Dict]:
        """Get all records for viewing"""
        data = self.collection.get()
        
        records = []
        for doc_id, doc, metadata in zip(data['ids'], data['documents'], data['metadatas']):
            records.append({
                'id': doc_id,
                'content': doc,
                'type': metadata.get('type') if metadata else 'unknown',
                'source': metadata.get('source') if metadata else 'unknown'
            })
        
        return records

# ============================================================================
# MAIN AI AGENT
# ============================================================================

class GenericAIAgent:
    """
    Generic conversational AI agent for hackathon deployment
    
    Features:
    - Multi-format document processing
    - Image analysis
    - RAG with vector search
    - Dynamic configuration
    - Safety guardrails
    """
    
    def __init__(self, config_file: str = "SYSTEM_PROMPTS.md"):
        # Load configuration
        self.config = ConfigLoader(config_file)
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=api_key)
        
        # Initialize components
        self.guardrails = Guardrails(self.config)
        self.doc_processor = DocumentProcessor(self.client, self.config)
        self.rag_engine = RAGEngine(self.client)
        
        # Settings
        self.settings = {
            'temperature': 0.3,
            'max_tokens': 1000,
            'top_k': 5,
            'model': 'gpt-4o-mini'
        }
        
        print("✅ AI Agent initialized successfully")
    
    def query(self, question: str) -> Tuple[str, List[str]]:
        """
        Process a user query
        
        Returns:
            (answer, sources)
        """
        # Guardrail check
        if not self.guardrails.validate(question):
            return self.guardrails.get_response(), []
        
        # Retrieve relevant context
        context_docs = self.rag_engine.retrieve(question, self.settings['top_k'])
        
        if not context_docs:
            return "I don't have any relevant information to answer that question. Please upload some documents first.", []
        
        # Build context
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        
        # Generate answer
        answer = self._generate_answer(question, context)
        
        return answer, context_docs
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM"""
        messages = [
            {"role": "system", "content": self.config.get('system_prompt')},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.settings['model'],
                messages=messages,
                temperature=self.settings['temperature'],
                max_tokens=self.settings['max_tokens']
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"⚠️ Error generating answer: {e}")
            return f"I encountered an error while processing your question: {str(e)}"
    
    def process_document(self, file_path: str):
        """Process and index a document"""
        chunks = self.doc_processor.process_document(file_path)
        self.rag_engine.add_documents(chunks)
        print(f"✅ Processed: {Path(file_path).name}")
    
    def add_to_memory(self, title: str, content: str):
        """Add text directly to memory (for demo data)"""
        chunk = {
            "text": content,
            "metadata": {"source": title, "type": "text"}
        }
        self.rag_engine.add_documents([chunk])
    
    def clear_memory(self):
        """Clear all stored documents"""
        self.rag_engine.clear()
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config.reload()
        self.guardrails = Guardrails(self.config)
        print("✅ Configuration reloaded")
    
    def update_settings(self, settings: Dict):
        """Update agent settings"""
        self.settings.update(settings)
        print(f"✅ Settings updated: {settings}")
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        return self.rag_engine.get_stats()
    
    def get_all_records(self) -> List[Dict]:
        """Get all records"""
        return self.rag_engine.get_all_records()
    
    def delete_record(self, record_id: str):
        """Delete a specific record"""
        try:
            self.rag_engine.collection.delete(ids=[record_id])
            print(f"✅ Deleted record: {record_id}")
        except Exception as e:
            print(f"⚠️ Error deleting record: {e}")

# ============================================================================
# TESTING & DEMO
# ============================================================================

def demo():
    """Quick demo of the AI agent"""
    print("\n" + "="*50)
    print("AI AGENT DEMO")
    print("="*50 + "\n")
    
    # Initialize agent
    agent = GenericAIAgent()
    
    # Add demo content
    print("Adding demo content...")
    agent.add_to_memory(
        "Company FAQ",
        """
        Q: What are your business hours?
        A: We're open Monday-Friday, 9 AM - 5 PM EST.
        
        Q: How do I contact support?
        A: Email support@company.com or call 1-800-HELP.
        
        Q: What payment methods do you accept?
        A: Credit cards, PayPal, and bank transfers.
        """
    )
    
    # Test queries
    test_queries = [
        "What are your business hours?",
        "How can I contact support?",
        "Do you accept Bitcoin?",  # Not in context
    ]
    
    for query in test_queries:
        print(f"\nQ: {query}")
        answer, sources = agent.query(query)
        print(f"A: {answer}")
        print(f"Sources: {len(sources)} documents")
    
    print("\n" + "="*50)
    print("Demo complete!")
    print("="*50)

if __name__ == "__main__":
    demo()
