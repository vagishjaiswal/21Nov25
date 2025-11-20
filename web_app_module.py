"""
Module 1: Web Application UI
Hackathon Framework - Rapid Deployment Chat Interface

CUSTOMIZATION GUIDE:
1. Update PAGE_CONFIG for your use case
2. Modify WELCOME_MESSAGE for your domain
3. Adjust sidebar features in configure_sidebar()
4. Customize chat interface in main()
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment
load_dotenv()

# ============================================================================
# CONFIGURATION SECTION - CUSTOMIZE THIS FOR YOUR USE CASE
# ============================================================================

PAGE_CONFIG = {
    "page_title": "AI Assistant - Hackathon Demo",
    "page_icon": "🤖",
    "layout": "wide",
    "use_case_name": "Generic AI Assistant",
    "description": "Intelligent conversational AI for your needs"
}

WELCOME_MESSAGE = """
👋 **Welcome to the AI Assistant!**

I'm here to help you with your questions. Here's what I can do:

- 💬 Answer questions based on uploaded documents
- 🖼️ Analyze images and extract information
- 📊 Query databases in natural language
- 🔍 Retrieve relevant information quickly

**Get Started:**
1. Upload documents or images in the sidebar
2. Ask me anything related to your data
3. Get instant, accurate responses!
"""

# Custom styling (optional)
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
"""

# ============================================================================
# IMPORTS - Connect to AI Agent Module
# ============================================================================

try:
    from ai_agent_module import GenericAIAgent
    from database_module import UseCaseDatabase
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    st.error("⚠️ AI Agent module not found. Running in demo mode.")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'ai_agent' not in st.session_state and AI_AVAILABLE:
        st.session_state.ai_agent = GenericAIAgent()
    
    if 'database' not in st.session_state and AI_AVAILABLE:
        st.session_state.database = UseCaseDatabase()
    
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "chat"  # chat, database, settings
    
    if 'show_sources' not in st.session_state:
        st.session_state.show_sources = True
    
    if 'demo_data_loaded' not in st.session_state:
        st.session_state.demo_data_loaded = False

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

def configure_sidebar():
    """Configure sidebar with upload and settings"""
    with st.sidebar:
        st.markdown(f"## {PAGE_CONFIG['use_case_name']}")
        st.caption(PAGE_CONFIG['description'])
        
        st.divider()
        
        # Mode Selection
        st.markdown("### 🎯 Mode")
        mode = st.radio(
            "Choose mode:",
            options=["💬 Chat", "🗄️ Database", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        if mode == "💬 Chat":
            st.session_state.current_mode = "chat"
        elif mode == "🗄️ Database":
            st.session_state.current_mode = "database"
        else:
            st.session_state.current_mode = "settings"
        
        st.divider()
        
        # File Upload Section
        st.markdown("### 📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload files",
            type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg', 'csv'],
            accept_multiple_files=True,
            help="Supports documents and images",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.caption(f"📎 {len(uploaded_files)} file(s) selected")
            
            if st.button("🚀 Process Files", type="primary", use_container_width=True):
                process_uploaded_files(uploaded_files)
        
        st.divider()
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear DB", use_container_width=True):
                if AI_AVAILABLE:
                    st.session_state.ai_agent.clear_memory()
                st.session_state.documents_loaded = False
                st.success("Database cleared!")
        
        # Load Demo Data Button
        if not st.session_state.demo_data_loaded:
            if st.button("📊 Load Demo Data", use_container_width=True, help="Load sample data for demonstration"):
                load_demo_data()
                st.session_state.demo_data_loaded = True
                st.rerun()
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Statistics")
        st.metric("Messages", len(st.session_state.chat_history))
        st.metric("Documents", "✅" if st.session_state.documents_loaded else "❌")
        
        st.divider()
        
        # Export Chat
        if st.session_state.chat_history:
            chat_export = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                label="💾 Export Chat",
                data=chat_export,
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ============================================================================
# FILE PROCESSING
# ============================================================================

def process_uploaded_files(uploaded_files):
    """Process uploaded documents and images"""
    if not AI_AVAILABLE:
        st.warning("AI Agent not available. Cannot process files.")
        return
    
    with st.spinner("Processing files..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, file in enumerate(uploaded_files):
            status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {file.name}")
            
            try:
                # Save to temp file
                temp_path = Path(f"temp_{file.name}")
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                
                # Process with AI agent
                st.session_state.ai_agent.process_document(str(temp_path))
                
                st.success(f"✅ Processed: {file.name}")
                
                # Clean up
                temp_path.unlink()
                
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.empty()
        progress_bar.empty()
        
        st.session_state.documents_loaded = True
        st.success(f"🎉 Successfully processed {len(uploaded_files)} file(s)!")

# ============================================================================
# DEMO DATA LOADING
# ============================================================================

def load_demo_data():
    """Load demonstration data for quick testing"""
    if not AI_AVAILABLE:
        st.warning("Cannot load demo data without AI agent.")
        return
    
    demo_documents = [
        {
            "title": "Product Catalog",
            "content": """
            Our company offers three main products:
            
            1. Pro Plan ($99/month): Includes all features, priority support, and custom integrations
            2. Business Plan ($49/month): Standard features with email support
            3. Starter Plan ($19/month): Basic features for individuals
            
            All plans include a 14-day free trial and can be cancelled anytime.
            """
        },
        {
            "title": "Company Policy",
            "content": """
            Working Hours: 9 AM - 5 PM (Monday to Friday)
            Remote Work: Hybrid model - 3 days in office, 2 days remote
            Vacation Days: 15 days per year + public holidays
            Health Benefits: Comprehensive medical, dental, and vision coverage
            """
        },
        {
            "title": "FAQ",
            "content": """
            Q: How do I reset my password?
            A: Click "Forgot Password" on the login page and follow the email instructions.
            
            Q: What payment methods do you accept?
            A: We accept credit cards, PayPal, and bank transfers.
            
            Q: Is there a mobile app?
            A: Yes, available on iOS and Android stores.
            """
        }
    ]
    
    with st.spinner("Loading demo data..."):
        for doc in demo_documents:
            st.session_state.ai_agent.add_to_memory(
                doc["title"],
                doc["content"]
            )
        
        st.session_state.documents_loaded = True
        st.success("✅ Demo data loaded successfully!")

# ============================================================================
# CHAT INTERFACE
# ============================================================================

def render_chat_interface():
    """Main chat interface"""
    st.markdown(f'<h1 class="main-header">{PAGE_CONFIG["use_case_name"]}</h1>', unsafe_allow_html=True)
    
    # Welcome message if no chat history
    if not st.session_state.chat_history:
        st.markdown(WELCOME_MESSAGE)
        
        # Example questions
        st.markdown("### 💡 Try asking:")
        example_cols = st.columns(3)
        
        example_questions = [
            "What services do you offer?",
            "How do I get started?",
            "What are your pricing plans?"
        ]
        
        for idx, col in enumerate(example_cols):
            with col:
                if st.button(example_questions[idx], use_container_width=True):
                    process_user_message(example_questions[idx])
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat['question'])
        
        with st.chat_message("assistant"):
            st.write(chat['answer'])
            
            # Show sources if available and enabled
            if st.session_state.show_sources and chat.get('sources'):
                with st.expander("📚 View Sources"):
                    for idx, source in enumerate(chat['sources'], 1):
                        st.markdown(f"**Source {idx}:**")
                        st.text(source[:200] + "..." if len(source) > 200 else source)
    
    # Chat input
    if question := st.chat_input("Ask me anything..."):
        process_user_message(question)

def process_user_message(question: str):
    """Process user message and generate response"""
    # Display user message
    with st.chat_message("user"):
        st.write(question)
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if AI_AVAILABLE:
                try:
                    answer, sources = st.session_state.ai_agent.query(question)
                except Exception as e:
                    answer = f"I encountered an error: {str(e)}"
                    sources = []
            else:
                answer = "AI Agent not available. This is a demo response."
                sources = []
            
            st.write(answer)
            
            if st.session_state.show_sources and sources:
                with st.expander("📚 View Sources"):
                    for idx, source in enumerate(sources, 1):
                        st.markdown(f"**Source {idx}:**")
                        st.text(source[:200] + "..." if len(source) > 200 else source)
    
    # Save to history
    st.session_state.chat_history.append({
        'question': question,
        'answer': answer,
        'sources': sources,
        'timestamp': datetime.now().isoformat()
    })
    
    st.rerun()

# ============================================================================
# DATABASE VIEWER
# ============================================================================

def render_database_viewer():
    """Display database contents and stats"""
    st.header("🗄️ Database Viewer")
    st.markdown("Explore the knowledge base and data sources")
    
    if not AI_AVAILABLE:
        st.warning("Database functionality requires AI Agent module.")
        return
    
    # Database statistics
    st.markdown("### 📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        stats = st.session_state.ai_agent.get_memory_stats()
        
        with col1:
            st.metric("Total Records", stats.get('total_records', 0))
        with col2:
            st.metric("Document Chunks", stats.get('chunks', 0))
        with col3:
            st.metric("Images Processed", stats.get('images', 0))
        with col4:
            st.metric("Queries Made", len(st.session_state.chat_history))
    except Exception as e:
        st.error(f"Error loading statistics: {e}")
    
    st.divider()
    
    # View records
    st.markdown("### 📄 Records")
    
    try:
        records = st.session_state.ai_agent.get_all_records()
        
        if not records:
            st.info("No records in database. Upload documents to get started.")
        else:
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("Filter by type:", ["All", "text", "image"])
            with col2:
                search_term = st.text_input("Search:", placeholder="Enter keywords...")
            
            # Display filtered records
            for idx, record in enumerate(records):
                if filter_type != "All" and record.get('type') != filter_type:
                    continue
                
                if search_term and search_term.lower() not in record.get('content', '').lower():
                    continue
                
                with st.expander(f"Record {idx + 1}: {record.get('source', 'Unknown')}"):
                    st.markdown(f"**Type:** {record.get('type', 'N/A')}")
                    st.markdown(f"**Source:** {record.get('source', 'N/A')}")
                    st.text_area("Content:", record.get('content', ''), height=150, disabled=True)
                    
                    if st.button(f"Delete", key=f"del_{idx}"):
                        st.session_state.ai_agent.delete_record(record.get('id'))
                        st.success("Record deleted!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"Error loading records: {e}")

# ============================================================================
# SETTINGS INTERFACE
# ============================================================================

def render_settings():
    """Settings and configuration page"""
    st.header("⚙️ Settings & Configuration")
    
    # Display Configuration
    st.markdown("### 🎨 Display Settings")
    
    show_sources = st.checkbox(
        "Show sources with answers",
        value=st.session_state.show_sources
    )
    st.session_state.show_sources = show_sources
    
    st.divider()
    
    # System Prompts Editor
    st.markdown("### 📝 System Prompts")
    st.info("Edit system prompts to customize AI behavior. Changes apply to next query.")
    
    prompts_file = Path("SYSTEM_PROMPTS.md")
    
    if prompts_file.exists():
        with open(prompts_file, 'r', encoding='utf-8') as f:
            current_prompts = f.read()
        
        edited_prompts = st.text_area(
            "Edit System Prompts:",
            value=current_prompts,
            height=400,
            help="Modify the system prompts to change AI behavior"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", type="primary"):
                with open(prompts_file, 'w', encoding='utf-8') as f:
                    f.write(edited_prompts)
                st.success("✅ Prompts saved!")
                
                # Reload AI agent
                if AI_AVAILABLE:
                    st.session_state.ai_agent.reload_config()
                    st.success("✅ Configuration reloaded!")
        
        with col2:
            if st.button("🔄 Reset to Default"):
                st.rerun()
    else:
        st.warning("SYSTEM_PROMPTS.md not found. Using default configuration.")
        
        if st.button("Create Default File"):
            with open(prompts_file, 'w', encoding='utf-8') as f:
                f.write("# System Prompts\n\n### Full Prompt\n```\nYou are a helpful AI assistant.\n```")
            st.success("File created!")
            st.rerun()
    
    st.divider()
    
    # Advanced Settings
    st.markdown("### 🔧 Advanced Settings")
    
    if AI_AVAILABLE:
        col1, col2 = st.columns(2)
        
        with col1:
            temperature = st.slider("Response Temperature:", 0.0, 1.0, 0.3, 0.1)
            max_tokens = st.number_input("Max Response Tokens:", 100, 2000, 1000, 100)
        
        with col2:
            top_k = st.number_input("Retrieval Results (top_k):", 1, 10, 5, 1)
            chunk_size = st.number_input("Chunk Size:", 500, 2000, 1000, 100)
        
        if st.button("Apply Settings"):
            st.session_state.ai_agent.update_settings({
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_k': top_k,
                'chunk_size': chunk_size
            })
            st.success("Settings applied!")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Set page config
    # ...existing code...
    # Set page config
    allowed_keys = {"page_title", "page_icon", "layout", "initial_sidebar_state", "menu_items"}
    filtered_page_config = {k: v for k, v in PAGE_CONFIG.items() if k in allowed_keys}
    st.set_page_config(**filtered_page_config)
    # ...existing code...
    
    # Initialize session state
    initialize_session_state()
    
    # Configure sidebar
    configure_sidebar()
    
    # Render appropriate interface based on mode
    if st.session_state.current_mode == "chat":
        render_chat_interface()
    elif st.session_state.current_mode == "database":
        render_database_viewer()
    elif st.session_state.current_mode == "settings":
        render_settings()

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
