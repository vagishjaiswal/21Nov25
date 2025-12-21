# 📚 RAG Document Assistant

A lightweight Retrieval-Augmented Generation (RAG) system built with Streamlit, ChromaDB, and OpenAI for intelligent document analysis and question answering.

## 🌟 Features

- **Multi-Format Support**: Process PDF, DOCX, DOC, TXT, and image files
- **Image Understanding**: Automatically extracts and analyzes images from PDFs and DOCX files using GPT-4 Vision
- **Intelligent Chunking**: Smart text segmentation with overlap for better context retention
- **Vector Search**: Fast semantic search using ChromaDB
- **Natural Language QA**: Get accurate answers based on your documents
- **Source Attribution**: See which documents your answers come from
- **Guardrails**: Built-in safety measures to prevent misuse

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Tesseract OCR (for image text extraction)

### Installation

1. **Install Tesseract OCR**

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Run installer (recommended: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
- Default installation path: `C:\Program Files\Tesseract-OCR\`
- Add to PATH or the app will auto-detect it

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

2. **Clone or download the project files**

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_api_key_here
```

5. **Run the application**
```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
rag-document-assistant/
├── app.py                    # Main Streamlit application
├── document_processor.py     # Document processing & chunking
├── rag_engine.py            # RAG query engine
├── config.py                # System prompts & guardrails
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your actual API keys (create this)
├── SYSTEM_PROMPTS.md       # Detailed prompt documentation
└── README.md               # This file
```

## 🎯 Usage

1. **Upload Documents**
   - Click "Browse files" in the sidebar
   - Select one or more documents (PDF, DOCX, TXT, or images)
   - Click "Process Documents"

2. **Ask Questions**
   - Type your question in the chat input
   - Get AI-powered answers based on your documents
   - View source excerpts for verification

3. **Manage Database**
   - Click "Clear Database" to remove all documents and start fresh

## 🔧 Configuration

### Chunk Settings
Modify in `document_processor.py`:
```python
self.chunk_size = 1000        # Words per chunk
self.chunk_overlap = 200      # Overlap between chunks
```

### Model Selection
Modify in `rag_engine.py` and `document_processor.py`:
```python
model="gpt-4o-mini"          # For text generation
model="text-embedding-3-small"  # For embeddings
```

### Retrieval Settings
Modify in `rag_engine.py`:
```python
top_k = 5  # Number of relevant chunks to retrieve
```

## 🛡️ Guardrails

The system includes built-in safety measures:
- Blocks harmful or illegal requests
- Prevents prompt injection attempts
- Ensures answers stay within document context
- See `config.py` for detailed guardrail logic

## 📊 Supported File Types

| Format | Extension | Image Support |
|--------|-----------|---------------|
| PDF | `.pdf` | ✅ Yes |
| Word | `.docx`, `.doc` | ✅ Yes |
| Text | `.txt` | ❌ N/A |
| Images | `.png`, `.jpg`, `.jpeg` | ✅ Standalone |

## 🎨 How It Works

1. **Document Processing**
   - Extracts text from documents
   - **Tesseract OCR** extracts text from images (fast, free)
   - **GPT-4 Vision** analyzes visual elements and context
   - Chunks text into manageable segments

2. **Vectorization**
   - Converts text chunks to embeddings
   - Stores in local ChromaDB database
   - Enables semantic search

3. **Query Processing**
   - Converts question to embedding
   - Retrieves relevant chunks via similarity search
   - Generates natural language answer using GPT-4

4. **Response Generation**
   - Combines retrieved context with question
   - Uses system prompts for consistency
   - Returns answer with source attribution

## 💡 Tips for Best Results

- **Upload related documents** together for better cross-referencing
- **Ask specific questions** for more accurate answers
- **Use clear language** in your queries
- **Check sources** provided with each answer
- **Re-upload documents** if you need to update information

## 🐛 Troubleshooting

**"No relevant information found"**
- Ensure documents uploaded successfully
- Try rephrasing your question
- Check if the information actually exists in your documents

**Image analysis not working**
- Verify OpenAI API key has GPT-4 Vision access
- Check image quality and format
- Some images may not contain extractable information

**Slow processing**
- Large PDFs take time to process
- Image analysis requires API calls
- Consider splitting very large documents

## 📝 License

This project is open-source and available for personal and educational use.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## ⚠️ Disclaimer

This tool uses OpenAI's API and incurs costs based on usage. Monitor your API usage to avoid unexpected charges.
