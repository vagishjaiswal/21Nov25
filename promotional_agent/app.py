import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import tempfile
from document_processor import DocumentProcessor
from rag_engine import RAGEngine
from config import SystemPrompts

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False

def process_uploaded_files(uploaded_files):
    """Process and index uploaded documents"""
    with st.spinner("Processing documents..."):
        all_chunks = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for file_idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {file_idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                # Process document
                chunks = st.session_state.doc_processor.process_document(tmp_path)
                all_chunks.extend(chunks)
                st.success(f"✓ Processed: {uploaded_file.name} ({len(chunks)} chunks)")
            except Exception as e:
                st.error(f"✗ Error processing {uploaded_file.name}: {str(e)}")
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
            # Update progress
            progress_bar.progress((file_idx + 1) / len(uploaded_files))
        
        status_text.empty()
        progress_bar.empty()
        
        if all_chunks:
            # Add to vector store
            with st.spinner("Indexing chunks to database..."):
                st.session_state.rag_engine.add_documents(all_chunks)
                st.session_state.documents_loaded = True
            st.success(f"✅ Successfully indexed {len(all_chunks)} chunks from {len(uploaded_files)} file(s)!")
        else:
            st.warning("⚠️ No content extracted from uploaded files.")

def main():
    st.title("📚 RAG Document Assistant")
    st.markdown("Upload documents and ask questions using AI-powered retrieval")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🗄️ Database", "⚙️ System Prompts"])
    
    with tab1:
        # Sidebar for document upload
        with st.sidebar:
            st.header("📁 Document Upload")
            uploaded_files = st.file_uploader(
                "Upload documents",
                type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Supports PDF, DOCX, DOC, TXT, and images"
            )
            
            if uploaded_files:
                if st.button("Process Documents", type="primary", use_container_width=True):
                    process_uploaded_files(uploaded_files)
                
                # Show selected files count
                st.caption(f"📎 {len(uploaded_files)} file(s) selected")
            
            if st.session_state.documents_loaded:
                st.success("✓ Documents loaded")
                if st.button("Clear Database"):
                    st.session_state.rag_engine.clear_database()
                    st.session_state.documents_loaded = False
                    st.session_state.chat_history = []
                    st.rerun()
            
            st.divider()
            
            # Reload prompts button
            st.markdown("### ⚙️ Quick Actions")
            if st.button("🔄 Reload Prompts", help="Reload prompts from SYSTEM_PROMPTS.md"):
                from config import SystemPrompts
                message = SystemPrompts.reload_prompts()
                st.success(message)
                st.info("Applied to next query")
            
            st.divider()
            st.markdown("### 🎯 Features")
            st.markdown("""
            - 📄 Multi-format support
            - 🖼️ Image understanding
            - 🧠 Intelligent chunking
            - 💬 Natural language Q&A
            - 🔄 Dynamic prompt reload
            """)
        
        # Main chat interface
        # Display chat history
        for i, chat in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(chat['question'])
            with st.chat_message("assistant"):
                st.write(chat['answer'])
                if chat.get('sources'):
                    with st.expander("📚 Sources"):
                        for idx, source in enumerate(chat['sources'], 1):
                            st.markdown(f"**Source {idx}:**")
                            st.text(source[:300] + "..." if len(source) > 300 else source)
        
        # Chat input - always available
        if question := st.chat_input("Ask a question about your documents..."):
            with st.chat_message("user"):
                st.write(question)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Check if there are ANY documents in database (not just session state)
                    try:
                        collection_data = st.session_state.rag_engine.collection.get()
                        has_documents = len(collection_data['ids']) > 0
                    except:
                        has_documents = False
                    
                    if not has_documents:
                        answer = "👋 Hello! I'm your document assistant. I can help you understand and extract information from documents.\n\n📄 To get started, please upload some documents using the sidebar on the left. I support:\n- PDF files\n- Word documents (DOCX, DOC)\n- Text files (TXT)\n- Images (PNG, JPG, JPEG)\n\nOnce you upload documents, I'll be able to answer questions based on their content!"
                        sources = []
                    else:
                        # Update session state if documents exist but flag is false
                        if not st.session_state.documents_loaded:
                            st.session_state.documents_loaded = True
                        answer, sources = st.session_state.rag_engine.query(question)
                    
                    st.write(answer)
                    
                    if sources:
                        with st.expander("📚 Sources"):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"**Source {idx}:**")
                                st.text(source[:300] + "..." if len(source) > 300 else source)
            
            # Save to history
            st.session_state.chat_history.append({
                'question': question,
                'answer': answer,
                'sources': sources
            })
    
    with tab2:
        st.header("🗄️ Database Viewer")
        st.markdown("View and manage document chunks stored in ChromaDB")
        
        # Get all records from ChromaDB
        try:
            collection = st.session_state.rag_engine.collection
            all_data = collection.get()
            
            if not all_data['ids']:
                st.info("📭 No documents in database. Upload documents in the Chat tab to get started.")
            else:
                # Database statistics
                st.markdown("### 📊 Database Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Chunks", len(all_data['ids']))
                
                with col2:
                    unique_sources = set()
                    for meta in all_data['metadatas']:
                        if meta and 'source' in meta:
                            unique_sources.add(Path(meta['source']).name)
                    st.metric("Documents", len(unique_sources))
                
                with col3:
                    text_chunks = sum(1 for m in all_data['metadatas'] if m and m.get('type') == 'text')
                    st.metric("Text Chunks", text_chunks)
                
                with col4:
                    image_chunks = sum(1 for m in all_data['metadatas'] if m and m.get('type') == 'image')
                    st.metric("Image Chunks", image_chunks)
                
                st.divider()
                
                # Filters
                st.markdown("### 🔍 Filters")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Filter by document
                    doc_filter = st.selectbox(
                        "Filter by Document",
                        ["All Documents"] + sorted(list(unique_sources))
                    )
                
                with col2:
                    # Filter by type
                    type_filter = st.selectbox(
                        "Filter by Type",
                        ["All Types", "text", "image"]
                    )
                
                with col3:
                    # Search in content
                    search_query = st.text_input("Search in content", placeholder="Enter keywords...")
                
                # Apply filters
                filtered_indices = []
                for idx, (doc_id, metadata, document) in enumerate(zip(all_data['ids'], all_data['metadatas'], all_data['documents'])):
                    # Document filter
                    if doc_filter != "All Documents":
                        if not metadata or Path(metadata.get('source', '')).name != doc_filter:
                            continue
                    
                    # Type filter
                    if type_filter != "All Types":
                        if not metadata or metadata.get('type') != type_filter:
                            continue
                    
                    # Search filter
                    if search_query:
                        if search_query.lower() not in document.lower():
                            continue
                    
                    filtered_indices.append(idx)
                
                st.markdown(f"### 📄 Records ({len(filtered_indices)} shown)")
                
                if not filtered_indices:
                    st.warning("No records match the current filters.")
                else:
                    # Pagination
                    items_per_page = 10
                    total_pages = (len(filtered_indices) - 1) // items_per_page + 1
                    
                    page = st.number_input(
                        "Page",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        step=1
                    )
                    
                    start_idx = (page - 1) * items_per_page
                    end_idx = min(start_idx + items_per_page, len(filtered_indices))
                    
                    st.caption(f"Showing {start_idx + 1} to {end_idx} of {len(filtered_indices)} records")
                    
                    # Display records
                    for i in range(start_idx, end_idx):
                        idx = filtered_indices[i]
                        doc_id = all_data['ids'][idx]
                        metadata = all_data['metadatas'][idx]
                        document = all_data['documents'][idx]
                        
                        with st.expander(f"📄 Record {idx + 1}: {doc_id}", expanded=False):
                            # Metadata
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Metadata:**")
                                if metadata:
                                    st.json(metadata)
                                else:
                                    st.text("No metadata")
                            
                            with col2:
                                st.markdown("**Document ID:**")
                                st.code(doc_id, language="text")
                            
                            # Content
                            st.markdown("**Content:**")
                            st.text_area(
                                "Document content",
                                value=document,
                                height=150,
                                disabled=True,
                                key=f"doc_{idx}",
                                label_visibility="collapsed"
                            )
                            
                            # Action buttons for individual record
                            if st.button(f"🗑️ Delete Record", key=f"del_{idx}"):
                                try:
                                    collection.delete(ids=[doc_id])
                                    st.success(f"✅ Deleted record: {doc_id}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting record: {e}")
                
                # Bulk actions
                st.divider()
                st.markdown("### ⚡ Bulk Actions")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🗑️ Delete All Records", type="secondary"):
                        if st.session_state.get('confirm_delete', False):
                            st.session_state.rag_engine.clear_database()
                            st.session_state.documents_loaded = False
                            st.session_state.confirm_delete = False
                            st.success("✅ All records deleted!")
                            st.rerun()
                        else:
                            st.session_state.confirm_delete = True
                            st.warning("⚠️ Click again to confirm deletion")
                
                with col2:
                    if st.button("🔄 Refresh View"):
                        st.rerun()
                
                # Export functionality
                st.divider()
                st.markdown("### 📤 Export Data")
                
                import json
                export_data = {
                    'total_chunks': len(all_data['ids']),
                    'records': [
                        {
                            'id': doc_id,
                            'metadata': metadata,
                            'content': document
                        }
                        for doc_id, metadata, document in zip(all_data['ids'], all_data['metadatas'], all_data['documents'])
                    ]
                }
                
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_str,
                    file_name="chromadb_export.json",
                    mime="application/json"
                )
        
        except Exception as e:
            st.error(f"❌ Error accessing database: {e}")
            st.info("Make sure documents are loaded in the Chat tab first.")
    
    with tab3:
        st.header("⚙️ System Prompts Configuration")
        st.markdown("View and edit the system prompts used by the AI assistant")
        
        # Load current prompts file
        prompts_file = Path(__file__).parent / "SYSTEM_PROMPTS.md"
        
        if prompts_file.exists():
            with open(prompts_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Display current file info
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📄 File: {prompts_file.name}")
            with col2:
                file_size = prompts_file.stat().st_size
                st.metric("Size", f"{file_size} bytes")
            
            # Editable text area
            st.markdown("### 📝 Edit Prompts")
            st.markdown("Edit the content below and click **Save Changes** to update the file.")
            
            edited_content = st.text_area(
                "SYSTEM_PROMPTS.md Content",
                value=current_content,
                height=400,
                help="Edit your system prompts here. Make sure to keep the format with ### headers and code blocks.",
                label_visibility="collapsed"
            )
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 3])
            
            with col1:
                if st.button("💾 Save Changes", type="primary"):
                    try:
                        with open(prompts_file, 'w', encoding='utf-8') as f:
                            f.write(edited_content)
                        st.success("✅ File saved successfully!")
                        
                        # Auto-reload prompts
                        from config import SystemPrompts
                        SystemPrompts.reload_prompts()
                        st.success("✅ Prompts reloaded!")
                    except Exception as e:
                        st.error(f"❌ Error saving file: {e}")
            
            with col2:
                if st.button("🔄 Reset to Current"):
                    st.rerun()
            
            # Show live preview of loaded prompts
            st.divider()
            st.markdown("### 👁️ Live Preview")
            st.markdown("Current prompts loaded in memory:")
            
            from config import SystemPrompts
            
            with st.expander("🤖 Main System Prompt", expanded=True):
                st.code(SystemPrompts.get_system_prompt(), language="text")
            
            with st.expander("🛡️ Guardrail Response"):
                st.code(SystemPrompts.get_guardrail_response(), language="text")
            
            with st.expander("⚠️ Prohibited Patterns"):
                st.code(", ".join(SystemPrompts.PROHIBITED_PATTERNS), language="text")
        
        else:
            st.error(f"❌ SYSTEM_PROMPTS.md file not found at: {prompts_file}")
            st.info("The system is using default prompts.")
            
            if st.button("Create SYSTEM_PROMPTS.md file"):
                # Create default file
                default_content = """# System Prompts and Guardrails Documentation

## Main System Prompt

### Full Prompt

```
You are an intelligent document assistant that helps users understand and extract information from their uploaded documents.

Your responsibilities:
1. Answer questions accurately based ONLY on the provided context from documents
2. If information is not in the context, clearly state that you don't have that information
3. Provide clear, concise, and well-structured answers
4. When referencing specific information, be precise about which document it comes from
5. If you encounter images descriptions, treat them as valuable context
6. Maintain a helpful and professional tone

Guidelines:
- Be accurate and factual
- Don't make up information not in the context
- If uncertain, express that uncertainty
- Provide direct answers followed by supporting details
- Use natural, conversational language
- Break down complex information into digestible parts

Remember: Your knowledge is limited to the uploaded documents. Do not use external knowledge.
```

### Guardrail Response

```
I'm designed to help you with questions about your uploaded documents. I cannot assist with:
- Harmful, illegal, or unethical requests
- Personal advice outside document context
- Generating misleading information
- Requests that violate privacy or security

Please ask questions related to your documents.
```
"""
                try:
                    with open(prompts_file, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    st.success("✅ SYSTEM_PROMPTS.md created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating file: {e}")

if __name__ == "__main__":
    main()