import os
from pathlib import Path
from typing import List, Dict
import base64
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import io
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process document based on file type"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return self._process_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self._process_docx(file_path)
        elif ext == '.txt':
            return self._process_txt(file_path)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return self._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _process_pdf(self, file_path: str) -> List[Dict]:
        """Extract text and images from PDF"""
        chunks = []
        
        # Extract text using PyPDF2
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Chunk text
        if full_text.strip():
            chunks.extend(self._chunk_text(full_text, {"source": file_path, "type": "text"}))
        
        # Extract images using PyMuPDF
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            images = page.get_images()
            for img_idx, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Analyze image with GPT-4 Vision
                    image_description = self._analyze_image(image_bytes)
                    if image_description:
                        chunks.append({
                            "text": f"[IMAGE DESCRIPTION] {image_description}",
                            "metadata": {
                                "source": file_path,
                                "page": page_num + 1,
                                "type": "image"
                            }
                        })
                except Exception as e:
                    print(f"Error processing image: {e}")
        
        return chunks
    
    def _process_docx(self, file_path: str) -> List[Dict]:
        """Extract text and images from DOCX"""
        chunks = []
        doc = Document(file_path)
        
        # Extract text
        full_text = "\n".join([para.text for para in doc.paragraphs])
        if full_text.strip():
            chunks.extend(self._chunk_text(full_text, {"source": file_path, "type": "text"}))
        
        # Extract images
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_data = rel.target_part.blob
                    image_description = self._analyze_image(image_data)
                    if image_description:
                        chunks.append({
                            "text": f"[IMAGE DESCRIPTION] {image_description}",
                            "metadata": {
                                "source": file_path,
                                "type": "image"
                            }
                        })
                except Exception as e:
                    print(f"Error processing image: {e}")
        
        return chunks
    
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
                "metadata": {
                    "source": file_path,
                    "type": "image"
                }
            }]
        return []
    
    def _analyze_image(self, image_bytes: bytes) -> str:
        """Analyze image using GPT-4 Vision"""
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail, including any text, diagrams, charts, or important visual elements."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return ""
    
    def _chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into chunks with overlap"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "metadata": metadata.copy()
                })
        
        return chunks
