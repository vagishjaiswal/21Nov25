"""
Retail Business Promotional Message Generator AI Agent
Multi-business support with dedicated vector stores
"""

import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from retail_data_processor import RetailDataProcessor
from retail_rag_engine import RetailRAGEngine
from retail_config import RetailSystemPrompts
from flexible_csv_processor import FlexibleCSVProcessor

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="🎯 Retail Promo AI Agent",
    page_icon="🛒",
    layout="wide"
)

class RetailBusinessManager:
    """Manages multiple retail businesses and their data"""
    
    def __init__(self, base_data_dir="retail_businesses", base_db_dir="retail_vector_dbs"):
        self.base_data_dir = Path(base_data_dir)
        self.base_db_dir = Path(base_db_dir)
        self.base_data_dir.mkdir(exist_ok=True)
        self.base_db_dir.mkdir(exist_ok=True)
        
        # Load businesses config
        self.config_file = self.base_data_dir / "businesses_config.json"
        self.businesses = self._load_businesses()
    
    def _load_businesses(self):
        """Load registered businesses from config"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_businesses(self):
        """Save businesses config"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.businesses, f, indent=2)
    
    def register_business(self, business_name, description=""):
        """Register a new retail business"""
        business_id = business_name.lower().replace(" ", "_")
        
        if business_id in self.businesses:
            return False, "Business already exists"
        
        # Create business directory structure
        business_dir = self.base_data_dir / business_id
        business_dir.mkdir(exist_ok=True)
        
        # Create vector db directory
        db_dir = self.base_db_dir / business_id
        db_dir.mkdir(exist_ok=True)
        
        # Add to config
        self.businesses[business_id] = {
            "name": business_name,
            "description": description,
            "data_dir": str(business_dir),
            "db_dir": str(db_dir),
            "created_at": datetime.now().isoformat(),
            "csv_files": {
                "items": None,
                "users": None,
                "purchase_history": None
            }
        }
        
        self._save_businesses()
        return True, f"Business '{business_name}' registered successfully!"
    
    def get_business_list(self):
        """Get list of all registered businesses"""
        return list(self.businesses.keys())
    
    def get_business_info(self, business_id):
        """Get information about a specific business"""
        return self.businesses.get(business_id)
    
    def save_csv_file(self, business_id, file_type, uploaded_file):
        """Save uploaded CSV file for a business"""
        if business_id not in self.businesses:
            return False, "Business not found"
        
        business_dir = Path(self.businesses[business_id]["data_dir"])
        
        # Save file
        file_path = business_dir / f"{business_id}_{file_type}.csv"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Update config
        self.businesses[business_id]["csv_files"][file_type] = str(file_path)
        self._save_businesses()
        
        return True, f"Saved {file_type} CSV successfully"
    
    def get_csv_paths(self, business_id):
        """Get paths to all CSV files for a business"""
        if business_id not in self.businesses:
            return None
        return self.businesses[business_id]["csv_files"]
    
    def delete_business(self, business_id):
        """Delete a business and all its data"""
        if business_id not in self.businesses:
            return False, "Business not found"
        
        try:
            import shutil
            
            business_info = self.businesses[business_id]
            
            # Delete data directory
            data_dir = Path(business_info["data_dir"])
            if data_dir.exists():
                shutil.rmtree(data_dir)
            
            # Delete vector DB directory
            db_dir = Path(business_info["db_dir"])
            if db_dir.exists():
                shutil.rmtree(db_dir)
            
            # Delete prompts file if exists
            prompts_file = Path(business_info["data_dir"]) / f"{business_id}_prompts.md"
            if prompts_file.exists():
                prompts_file.unlink()
            
            # Remove from config
            del self.businesses[business_id]
            self._save_businesses()
            
            return True, f"Business '{business_info['name']}' deleted successfully!"
        except Exception as e:
            return False, f"Error deleting business: {str(e)}"


# Initialize session state
if 'business_manager' not in st.session_state:
    st.session_state.business_manager = RetailBusinessManager()
if 'selected_business' not in st.session_state:
    st.session_state.selected_business = None
if 'rag_engines' not in st.session_state:
    st.session_state.rag_engines = {}
if 'data_processors' not in st.session_state:
    st.session_state.data_processors = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'csv_mappings' not in st.session_state:
    st.session_state.csv_mappings = {}
if 'flexible_processor' not in st.session_state:
    st.session_state.flexible_processor = FlexibleCSVProcessor()


def process_business_data(business_id):
    """Process and load CSV data into vector store for a business"""
    manager = st.session_state.business_manager
    business_info = manager.get_business_info(business_id)
    
    if not business_info:
        return False, "Business not found"
    
    csv_paths = business_info["csv_files"]
    
    # Check if all CSV files are uploaded
    missing = [k for k, v in csv_paths.items() if not v]
    if missing:
        return False, f"Missing CSV files: {', '.join(missing)}"
    
    with st.spinner(f"Processing data for {business_info['name']}..."):
        try:
            # Initialize data processor
            processor = RetailDataProcessor()
            
            # Load and process CSVs
            items_df = pd.read_csv(csv_paths["items"])
            users_df = pd.read_csv(csv_paths["users"])
            history_df = pd.read_csv(csv_paths["purchase_history"])
            
            # Create document chunks
            chunks = processor.process_retail_data(items_df, users_df, history_df)
            
            # Initialize RAG engine with business-specific DB
            db_dir = business_info["db_dir"]
            rag_engine = RetailRAGEngine(
                persist_directory=db_dir,
                collection_name=f"{business_id}_collection",
                business_id=business_id
            )
            
            # Add to vector store
            rag_engine.add_documents(chunks)
            
            # Store in session
            st.session_state.rag_engines[business_id] = rag_engine
            st.session_state.data_processors[business_id] = {
                'items': items_df,
                'users': users_df,
                'history': history_df,
                'processor': processor
            }
            
            return True, f"Successfully processed {len(chunks)} data chunks!"
        
        except Exception as e:
            return False, f"Error processing data: {str(e)}"


def main():
    st.title("🛒 Indian Retail Promotional Meme Message AI Agent")
    st.markdown("### 🎯 Create Personalized Promotional Messages for Retail Businesses")
    
    manager = st.session_state.business_manager
    
    # Sidebar for business management
    with st.sidebar:
        st.header("🏪 Business Management")
        
        # Register new business
        with st.expander("➕ Register New Business", expanded=False):
            new_business_name = st.text_input("Business Name", key="new_biz_name")
            new_business_desc = st.text_area("Description (optional)", key="new_biz_desc")
            
            if st.button("Register Business", type="primary"):
                if new_business_name:
                    success, message = manager.register_business(
                        new_business_name, 
                        new_business_desc
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter business name")
        
        st.divider()
        
        # Select business
        business_list = manager.get_business_list()
        
        if not business_list:
            st.info("📭 No businesses registered yet. Register one above!")
        else:
            # Display as cards
            st.markdown("### 🏪 Select Business")
            
            for biz_id in business_list:
                biz_info = manager.get_business_info(biz_id)
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{biz_info['name']}**")
                        if biz_info.get('description'):
                            st.caption(biz_info['description'])
                    
                    with col2:
                        is_selected = st.session_state.selected_business == biz_id
                        button_label = "✓ Selected" if is_selected else "Select"
                        button_type = "secondary" if is_selected else "primary"
                        
                        if st.button(button_label, key=f"sel_{biz_id}", type=button_type, disabled=is_selected):
                            st.session_state.selected_business = biz_id
                            if biz_id not in st.session_state.chat_history:
                                st.session_state.chat_history[biz_id] = []
                            st.rerun()
                            
                            # Delete business button
                if st.button("🗑️ Delete", key=f"del_{biz_id}", type="secondary", help="Delete this business"):
                    if st.session_state.get(f'confirm_delete_biz_{biz_id}', False):
                        success, message = manager.delete_business(biz_id)
                        if success:
                            # Clean up session state
                            if biz_id in st.session_state.rag_engines:
                                del st.session_state.rag_engines[biz_id]
                            if biz_id in st.session_state.data_processors:
                                del st.session_state.data_processors[biz_id]
                            if biz_id in st.session_state.chat_history:
                                del st.session_state.chat_history[biz_id]
                            if st.session_state.selected_business == biz_id:
                                st.session_state.selected_business = None
                            st.session_state[f'confirm_delete_biz_{biz_id}'] = False
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.session_state[f'confirm_delete_biz_{biz_id}'] = True
                        st.warning("⚠️ Click again to confirm deletion")
                    
                    # Show status
                    csv_files = biz_info["csv_files"]
                    uploaded_count = sum(1 for v in csv_files.values() if v)
                    
                    if uploaded_count == 3:
                        st.success(f"✅ {uploaded_count}/3 CSV files")
                    elif uploaded_count > 0:
                        st.warning(f"⚠️ {uploaded_count}/3 CSV files")
                    else:
                        st.info("📄 No CSV files")
                    
                    st.divider()
    
    # Main content area
    selected_biz = st.session_state.selected_business
    
    if not selected_biz:
        st.info("👈 Please select or register a business from the sidebar to continue")
        
        # Show instructions
        st.markdown("""
        ## 🚀 Getting Started
        
        ### Step 1: Register a Business
        1. Click "➕ Register New Business" in the sidebar
        2. Enter business name (e.g., "Z-Mart", "ShopEasy")
        3. Optionally add a description
        4. Click "Register Business"
        
        ### Step 2: Upload CSV Data
        After registering, you'll need to upload 3 CSV files:
        - **Items CSV**: Product catalog
        - **Users CSV**: Customer database
        - **Purchase History CSV**: Transaction records
        
        ### Step 3: Generate Messages
        Select customers and items to create personalized promotional messages!
        """)
        return
    
    biz_info = manager.get_business_info(selected_biz)
    
    st.success(f"🏪 Selected Business: **{biz_info['name']}**")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Generate Messages", 
        "📢 Broadcast Messages",
        "📤 Upload Data", 
        "📊 View Data",
        "⚙️ Settings"
    ])
    
    with tab1:
        st.header("💬 Generate Promotional Messages")
        
        # Check if data is loaded
        if selected_biz not in st.session_state.rag_engines:
            st.warning("⚠️ Please upload and process CSV data first in the 'Upload Data' tab")
            st.info("You need to upload 3 CSV files: items, users, and purchase_history")
        else:
            # Get data
            data = st.session_state.data_processors[selected_biz]
            rag_engine = st.session_state.rag_engines[selected_biz]
            
            # User selection
            col1, col2 = st.columns(2)
            
            with col1:
                user_ids = data['users']['user_id'].tolist()
                selected_user = st.selectbox(
                    "👤 Select Customer",
                    user_ids,
                    format_func=lambda x: f"{x} - {data['users'][data['users']['user_id']==x]['name'].values[0]}"
                )
            
            with col2:
                item_ids = data['items']['item_id'].tolist()
                selected_item = st.selectbox(
                    "🛍️ Select Item to Promote",
                    item_ids,
                    format_func=lambda x: f"{x} - {data['items'][data['items']['item_id']==x]['item_name'].values[0]}"
                )
            
            # Additional context
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_season = st.selectbox(
                    "🌦️ Current Season",
                    ["Winter", "Summer", "Monsoon", "Spring", "Autumn"]
                )
            
            with col2:
                upcoming_festival = st.selectbox(
                    "🎉 Upcoming Festival",
                    ["None", "Diwali", "Holi", "Eid", "Christmas", "New Year", 
                     "Pongal", "Onam", "Raksha Bandhan", "Dussehra", "Ganesh Chaturthi"]
                )
            
            with col3:
                message_tone = st.selectbox(
                    "🎭 Message Tone",
                    ["Funny Meme", "Tapori Style", "Emotional", "Urgent Deal", "Friendly", "Poetic"]
                )
            
            # Generate button
            if st.button("🎯 Generate Promotional Message", type="primary"):
                with st.spinner("Creating your promotional message..."):
                    # Build query
                    user_data = data['users'][data['users']['user_id']==selected_user].iloc[0]
                    item_data = data['items'][data['items']['item_id']==selected_item].iloc[0]
                    
                    # Get purchase history
                    user_history = data['history'][data['history']['user_id']==selected_user]
                    
                    query = f"""Generate a creative promotional message for:
                    
Customer: {user_data['name']}
- Age: {user_data['age']} ({user_data['age_group']})
- Region: {user_data['region']} - {user_data['city']}, {user_data['state']}
- Preferred Language: {user_data['preferred_language']}
- Favorite Categories: {user_data['favorite_categories']}
- Total Purchases: {user_data['total_purchases']}
- Loyalty Points: {user_data['loyalty_points']}

Item to Promote: {item_data['item_name']}
- Category: {item_data['category']} - {item_data['subcategory']}
- Brand: {item_data['brand']}
- Price: ₹{item_data['price']} (Original: ₹{item_data['original_price']}, {item_data['discount_percentage']}% OFF)
- Description: {item_data['description']}
- Seasonal Relevance: {item_data['seasonal_relevance']}
- Festival Relevance: {item_data['festival_relevance']}
- Specifications: {item_data['specifications']}

Context:
- Current Season: {current_season}
- Upcoming Festival: {upcoming_festival}
- Message Tone: {message_tone}

Create a personalized promotional message in {message_tone} style that connects with the customer."""
                    
                    message, sources = rag_engine.query(query)
                    
                    st.markdown("### 📱 Generated Promotional Message")
                    st.markdown("---")
                    
                    # Display in a nice card
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px;
                        border-radius: 15px;
                        color: white;
                        font-size: 18px;
                        line-height: 1.6;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                        margin: 20px 0;
                    ">
                    {message.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show item details
                    with st.expander("🛍️ Item Details"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Price", f"₹{item_data['price']}")
                            st.metric("Original Price", f"₹{item_data['original_price']}")
                        with col2:
                            st.metric("Discount", f"{item_data['discount_percentage']}%")
                            st.metric("Stock", item_data['stock_quantity'])
                    
                    # Show customer insights
                    with st.expander("👤 Customer Insights"):
                        st.write(f"**Purchase History**: {len(user_history)} items")
                        if len(user_history) > 0:
                            recent_items = user_history.sort_values('purchase_date', ascending=False).head(5)
                            st.dataframe(recent_items[['item_id', 'purchase_date', 'quantity', 'total_amount', 'rating']], use_container_width=True)
                    
                    # Copy button
                    st.code(message, language=None)
                    
                    # Save to history
                    if selected_biz not in st.session_state.chat_history:
                        st.session_state.chat_history[selected_biz] = []
                    
                    st.session_state.chat_history[selected_biz].append({
                        'timestamp': datetime.now().isoformat(),
                        'user': selected_user,
                        'item': selected_item,
                        'message': message,
                        'context': {
                            'season': current_season,
                            'festival': upcoming_festival,
                            'tone': message_tone
                        }
                    })
            
            # Chat history
            st.divider()
            st.subheader("📜 Message History")
            
            if selected_biz in st.session_state.chat_history and st.session_state.chat_history[selected_biz]:
                for idx, entry in enumerate(reversed(st.session_state.chat_history[selected_biz])):
                    with st.expander(f"Message {len(st.session_state.chat_history[selected_biz]) - idx}: {entry['user']} - {entry['item']}", expanded=False):
                        st.caption(f"Generated at: {entry['timestamp']}")
                        st.write(entry['message'])
                        st.json(entry['context'])
            else:
                st.info("No messages generated yet")
    
    with tab2:
        st.header("📢 Generate Broadcast Messages")
        
        if selected_biz not in st.session_state.rag_engines:
            st.warning("⚠️ Please upload and process CSV data first in the 'Upload Data' tab")
        else:
            data = st.session_state.data_processors[selected_biz]
            rag_engine = st.session_state.rag_engines[selected_biz]
            
            st.info("📣 Send promotional messages to all users for a selected item")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                item_ids = data['items']['item_id'].tolist()
                selected_item = st.selectbox(
                    "🛍️ Select Item to Broadcast",
                    item_ids,
                    format_func=lambda x: f"{x} - {data['items'][data['items']['item_id']==x]['item_name'].values[0]}",
                    key="broadcast_item"
                )
            
            with col2:
                item_data = data['items'][data['items']['item_id']==selected_item].iloc[0]
                st.metric("Price", f"₹{item_data['price']}")
                st.metric("Discount", f"{item_data['discount_percentage']}%")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_season = st.selectbox(
                    "🌦️ Season",
                    ["Winter", "Summer", "Monsoon", "Spring", "Autumn"],
                    key="broadcast_season"
                )
            
            with col2:
                upcoming_festival = st.selectbox(
                    "🎉 Festival",
                    ["None", "Diwali", "Holi", "Eid", "Christmas", "New Year", 
                     "Pongal", "Onam", "Raksha Bandhan", "Dussehra", "Ganesh Chaturthi"],
                    key="broadcast_festival"
                )
            
            with col3:
                message_tone = st.selectbox(
                    "🎭 Tone",
                    ["Funny Meme", "Tapori Style", "Emotional", "Urgent Deal", "Friendly", "Poetic"],
                    key="broadcast_tone"
                )
            
            st.divider()
            st.subheader("🎯 Target Audience")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                age_groups = ["All"] + sorted(data['users']['age_group'].unique().tolist())
                selected_age = st.multiselect("Age Group", age_groups, default=["All"])
            
            with col2:
                regions = ["All"] + sorted(data['users']['region'].unique().tolist())
                selected_regions = st.multiselect("Region", regions, default=["All"])
            
            with col3:
                genders = ["All"] + sorted(data['users']['gender'].unique().tolist())
                selected_genders = st.multiselect("Gender", genders, default=["All"])
            
            filtered_users = data['users'].copy()
            
            if "All" not in selected_age:
                filtered_users = filtered_users[filtered_users['age_group'].isin(selected_age)]
            
            if "All" not in selected_regions:
                filtered_users = filtered_users[filtered_users['region'].isin(selected_regions)]
            
            if "All" not in selected_genders:
                filtered_users = filtered_users[filtered_users['gender'].isin(selected_genders)]
            
            st.info(f"👥 Target Audience: {len(filtered_users)} users")
            
            if st.button("📢 Generate Broadcast Message", type="primary"):
                if len(filtered_users) == 0:
                    st.error("❌ No users match the filters")
                else:
                    with st.spinner(f"Generating broadcast message for {len(filtered_users)} users..."):
                        
                        # Get aggregate audience info
                        age_summary = filtered_users['age_group'].value_counts().to_dict()
                        region_summary = filtered_users['region'].value_counts().to_dict()
                        
                        query = f"""Generate ONE creative promotional message for:

Target Audience: {len(filtered_users)} users
- Age Groups: {', '.join([f"{k}: {v}" for k,v in age_summary.items()])}
- Regions: {', '.join([f"{k}: {v}" for k,v in region_summary.items()])}

Item to Promote: {item_data['item_name']}
- Category: {item_data['category']} - {item_data['subcategory']}
- Brand: {item_data['brand']}
- Price: ₹{item_data['price']} (Original: ₹{item_data['original_price']}, {item_data['discount_percentage']}% OFF)
- Description: {item_data['description']}
- Seasonal Relevance: {item_data['seasonal_relevance']}
- Festival Relevance: {item_data['festival_relevance']}

Context:
- Season: {current_season}
- Festival: {upcoming_festival}
- Tone: {message_tone}

Create ONE broadcast message in {message_tone} style that appeals to all users."""
                        
                        message, _ = rag_engine.query(query)
                        
                        broadcast_results = []
                        for _, user in filtered_users.iterrows():
                            broadcast_results.append({
                                'user_id': user['user_id'],
                                'name': user['name'],
                                'phone': user['phone'],
                                'message': message
                            })
                    
                    st.success(f"✅ Generated broadcast message for {len(broadcast_results)} users!")
                    
                    st.divider()
                    st.subheader("📱 Broadcast Message")
                    
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px;
                        border-radius: 15px;
                        color: white;
                        font-size: 18px;
                        line-height: 1.6;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                        margin: 20px 0;
                    ">
                    {message.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.code(message, language=None)
                    
                    st.divider()
                    st.subheader(f"👥 Recipients ({len(broadcast_results)} users)")
                    
                    for idx, result in enumerate(broadcast_results, 1):
                        with st.expander(f"{idx}. {result['name']} ({result['user_id']}) - 📞 {result['phone']}"):
                            st.markdown(result['message'])
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        df_export = pd.DataFrame(broadcast_results)
                        csv = df_export.to_csv(index=False)
                        st.download_button(
                            "📥 Download as CSV",
                            csv,
                            f"{selected_biz}_broadcast_{selected_item}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            "text/csv"
                        )
                    
                    with col2:
                        import json
                        json_str = json.dumps(broadcast_results, indent=2)
                        st.download_button(
                            "📥 Download as JSON",
                            json_str,
                            f"{selected_biz}_broadcast_{selected_item}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            "application/json"
                        )
    
    with tab3:
        st.header("📤 Upload CSV Data")
        st.markdown(f"Upload data files for **{biz_info['name']}**")
        
        csv_files = biz_info["csv_files"]
        
        # Items CSV
        st.subheader("1️⃣ Items Data")
        st.caption("🤖 AI will auto-detect and map your CSV columns")
        
        items_file = st.file_uploader(
            "Upload items CSV",
            type=['csv'],
            key=f"items_upload_{selected_biz}",
            help="CSV with product catalog - any format accepted"
        )
        
        if items_file:
            try:
                df = pd.read_csv(items_file)
                st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
                
                # Schema detection
                with st.expander("🔍 Analyze CSV Schema", expanded=True):
                    if st.button("🤖 Detect Schema", key="detect_items"):
                        with st.spinner("Analyzing columns with AI..."):
                            detection = st.session_state.flexible_processor.detect_csv_schema(df, 'items')
                            st.session_state.csv_mappings[f"{selected_biz}_items"] = detection
                    
                    if f"{selected_biz}_items" in st.session_state.csv_mappings:
                        det = st.session_state.csv_mappings[f"{selected_biz}_items"]
                        
                        st.info(st.session_state.flexible_processor.get_schema_summary(det))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Detected Mappings:**")
                            for exp, usr in det.get('mappings', {}).items():
                                conf = det.get('confidence', {}).get(exp, 0)
                                st.write(f"{exp} ← {usr} ({conf*100:.0f}%)")
                        
                        with col2:
                            if det.get('missing_fields'):
                                st.markdown("**Will Auto-Generate:**")
                                for field in det['missing_fields']:
                                    st.write(f"✨ {field}")
                
                with st.expander("Preview Data"):
                    st.dataframe(df.head(), use_container_width=True)
                
                if st.button("💾 Save & Transform Items CSV", key="save_items"):
                    if f"{selected_biz}_items" not in st.session_state.csv_mappings:
                        st.warning("⚠️ Please detect schema first")
                    else:
                        det = st.session_state.csv_mappings[f"{selected_biz}_items"]
                        
                        with st.spinner("Transforming data..."):
                            transformed_df = st.session_state.flexible_processor.transform_dataframe(
                                df, det['mappings'], det['missing_fields'], 'items'
                            )
                            transformed_df = st.session_state.flexible_processor.auto_convert_types(transformed_df, 'items')
                            
                            # Save transformed CSV
                            temp_path = Path(biz_info["data_dir"]) / f"{selected_biz}_items.csv"
                            transformed_df.to_csv(temp_path, index=False)
                            
                            manager.businesses[selected_biz]["csv_files"]["items"] = str(temp_path)
                            manager._save_businesses()
                            
                            st.success("✅ Data transformed and saved!")
                            st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        if csv_files["items"]:
            st.info(f"✅ Items CSV saved: {Path(csv_files['items']).name}")
        
        st.divider()
        
        # Users CSV
        st.subheader("2️⃣ Users Data")
        st.caption("🤖 AI will auto-detect and map your CSV columns")
       
        users_file = st.file_uploader(
            "Upload users CSV",
            type=['csv'],
            key=f"users_upload_{selected_biz}",
            help="CSV with customer database - any format accepted"
        )
        
        if users_file:
            try:
                df = pd.read_csv(users_file)
                st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
                
                with st.expander("🔍 Analyze CSV Schema", expanded=True):
                    if st.button("🤖 Detect Schema", key="detect_users"):
                        with st.spinner("Analyzing columns with AI..."):
                            detection = st.session_state.flexible_processor.detect_csv_schema(df, 'users')
                            st.session_state.csv_mappings[f"{selected_biz}_users"] = detection
                    
                    if f"{selected_biz}_users" in st.session_state.csv_mappings:
                        det = st.session_state.csv_mappings[f"{selected_biz}_users"]
                        st.info(st.session_state.flexible_processor.get_schema_summary(det))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Detected Mappings:**")
                            for exp, usr in det.get('mappings', {}).items():
                                conf = det.get('confidence', {}).get(exp, 0)
                                st.write(f"{exp} ← {usr} ({conf*100:.0f}%)")
                        
                        with col2:
                            if det.get('missing_fields'):
                                st.markdown("**Will Auto-Generate:**")
                                for field in det['missing_fields']:
                                    st.write(f"✨ {field}")
                
                with st.expander("Preview Data"):
                    st.dataframe(df.head(), use_container_width=True)
                
                if st.button("💾 Save & Transform Users CSV", key="save_users"):
                    if f"{selected_biz}_users" not in st.session_state.csv_mappings:
                        st.warning("⚠️ Please detect schema first")
                    else:
                        det = st.session_state.csv_mappings[f"{selected_biz}_users"]
                        
                        with st.spinner("Transforming data..."):
                            transformed_df = st.session_state.flexible_processor.transform_dataframe(
                                df, det['mappings'], det['missing_fields'], 'users'
                            )
                            transformed_df = st.session_state.flexible_processor.auto_convert_types(transformed_df, 'users')
                            
                            temp_path = Path(biz_info["data_dir"]) / f"{selected_biz}_users.csv"
                            transformed_df.to_csv(temp_path, index=False)
                            
                            manager.businesses[selected_biz]["csv_files"]["users"] = str(temp_path)
                            manager._save_businesses()
                            
                            st.success("✅ Data transformed and saved!")
                            st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        if csv_files["users"]:
            st.info(f"✅ Users CSV saved: {Path(csv_files['users']).name}")
        
        st.divider()
        
        # Purchase History CSV
        st.subheader("3️⃣ Purchase History Data")
        st.caption("🤖 AI will auto-detect and map your CSV columns")
      
        
        history_file = st.file_uploader(
            "Upload purchase_history CSV",
            type=['csv'],
            key=f"history_upload_{selected_biz}",
            help="CSV with transaction records - any format accepted"
        )
        
        if history_file:
            try:
                df = pd.read_csv(history_file)
                st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
                
                with st.expander("🔍 Analyze CSV Schema", expanded=True):
                    if st.button("🤖 Detect Schema", key="detect_history"):
                        with st.spinner("Analyzing columns with AI..."):
                            detection = st.session_state.flexible_processor.detect_csv_schema(df, 'purchase_history')
                            st.session_state.csv_mappings[f"{selected_biz}_history"] = detection
                    
                    if f"{selected_biz}_history" in st.session_state.csv_mappings:
                        det = st.session_state.csv_mappings[f"{selected_biz}_history"]
                        st.info(st.session_state.flexible_processor.get_schema_summary(det))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Detected Mappings:**")
                            for exp, usr in det.get('mappings', {}).items():
                                conf = det.get('confidence', {}).get(exp, 0)
                                st.write(f"{exp} ← {usr} ({conf*100:.0f}%)")
                        
                        with col2:
                            if det.get('missing_fields'):
                                st.markdown("**Will Auto-Generate:**")
                                for field in det['missing_fields']:
                                    st.write(f"✨ {field}")
                
                with st.expander("Preview Data"):
                    st.dataframe(df.head(), use_container_width=True)
                
                if st.button("💾 Save & Transform Purchase History CSV", key="save_history"):
                    if f"{selected_biz}_history" not in st.session_state.csv_mappings:
                        st.warning("⚠️ Please detect schema first")
                    else:
                        det = st.session_state.csv_mappings[f"{selected_biz}_history"]
                        
                        with st.spinner("Transforming data..."):
                            transformed_df = st.session_state.flexible_processor.transform_dataframe(
                                df, det['mappings'], det['missing_fields'], 'purchase_history'
                            )
                            transformed_df = st.session_state.flexible_processor.auto_convert_types(transformed_df, 'purchase_history')
                            
                            temp_path = Path(biz_info["data_dir"]) / f"{selected_biz}_purchase_history.csv"
                            transformed_df.to_csv(temp_path, index=False)
                            
                            manager.businesses[selected_biz]["csv_files"]["purchase_history"] = str(temp_path)
                            manager._save_businesses()
                            
                            st.success("✅ Data transformed and saved!")
                            st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        if csv_files["purchase_history"]:
            st.info(f"✅ Purchase History CSV saved: {Path(csv_files['purchase_history']).name}")
        
        st.divider()
        
        # Image Upload
        st.subheader("🖼️ Business Images (Optional)")
        st.markdown("Upload promotional images, product photos, store images for better message generation")
        
        image_files = st.file_uploader(
            "Upload business images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key=f"images_upload_{selected_biz}",
            help="Images will be analyzed and used to enhance promotional messages"
        )
        
        if image_files:
            st.success(f"✅ Selected {len(image_files)} image(s)")
            with st.expander("Preview Images"):
                cols = st.columns(min(len(image_files), 3))
                for idx, img_file in enumerate(image_files):
                    with cols[idx % 3]:
                        st.image(img_file, caption=img_file.name, use_container_width=True)
            
            if st.button("💾 Save & Process Images", key="save_images"):
                if 'image_chunks' not in st.session_state:
                    st.session_state.image_chunks = {}
                
                processor = st.session_state.data_processors.get(selected_biz, {}).get('processor', RetailDataProcessor())
                
                with st.spinner("Processing images..."):
                    img_chunks = processor.process_business_images(selected_biz, image_files)
                    st.session_state.image_chunks[selected_biz] = img_chunks
                    
                    if selected_biz in st.session_state.rag_engines:
                        st.session_state.rag_engines[selected_biz].add_documents(img_chunks)
                    
                    st.success(f"✅ Processed and indexed {len(img_chunks)} image chunks!")
                    st.balloons()
        
        if selected_biz in st.session_state.get('image_chunks', {}):
            st.info(f"✅ {len(st.session_state.image_chunks[selected_biz])} image chunks loaded")
        
        st.divider()
        
        # Process data button
        all_uploaded = all(csv_files.values())
        
        if all_uploaded:
            st.success("✅ All CSV files uploaded!")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("🚀 Process Data & Load to Vector DB", type="primary", use_container_width=True):
                    success, message = process_business_data(selected_biz)
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
            
            with col2:
                # Show if already processed
                if selected_biz in st.session_state.rag_engines:
                    st.success("✅ Data Loaded")
        else:
            missing = [k for k, v in csv_files.items() if not v]
            st.warning(f"⚠️ Please upload all CSV files. Missing: {', '.join(missing)}")
    
    with tab4:
        st.header("📊 View Business Data")
        
        if selected_biz not in st.session_state.data_processors:
            st.info("📭 No data loaded yet. Upload and process data first in the 'Upload Data' tab.")
        else:
            data = st.session_state.data_processors[selected_biz]
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Total Users", len(data['users']))
            with col2:
                st.metric("🛍️ Total Items", len(data['items']))
            with col3:
                st.metric("🛒 Total Purchases", len(data['history']))
            with col4:
                total_revenue = data['history']['total_amount'].sum()
                st.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
            
            st.divider()
            
            # Data views
            view_tab1, view_tab2, view_tab3 = st.tabs(["Items", "Users", "Purchase History"])
            
            with view_tab1:
                st.dataframe(data['items'], use_container_width=True, height=400)
                st.download_button(
                    "📥 Download Items CSV",
                    data['items'].to_csv(index=False),
                    f"{selected_biz}_items.csv",
                    "text/csv"
                )
            
            with view_tab2:
                st.dataframe(data['users'], use_container_width=True, height=400)
                st.download_button(
                    "📥 Download Users CSV",
                    data['users'].to_csv(index=False),
                    f"{selected_biz}_users.csv",
                    "text/csv"
                )
            
            with view_tab3:
                st.dataframe(data['history'], use_container_width=True, height=400)
                st.download_button(
                    "📥 Download Purchase History CSV",
                    data['history'].to_csv(index=False),
                    f"{selected_biz}_purchase_history.csv",
                    "text/csv"
                )
    
    with tab5:
        st.header("⚙️ Settings & Configuration")
        
        # System prompt editing - Business specific
        st.subheader("📝 System Prompts")
        st.info(f"🏪 Business: **{biz_info['name']}**")
        
        # Get business-specific prompts file
        business_prompts_file = RetailSystemPrompts.get_prompts_file(selected_biz)
        
        # Create business prompts file if it doesn't exist
        if not business_prompts_file.exists():
            st.warning("⚠️ Business-specific prompts file not found. Creating from default template...")
            success, message = RetailSystemPrompts.create_business_prompts_file(selected_biz, biz_info["data_dir"])
            if success:
                st.success(message)
            else:
                st.error(message)
        
        if business_prompts_file.exists():
            with open(business_prompts_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            st.info(f"📄 File: {business_prompts_file.name}")
            st.caption(f"Path: {business_prompts_file}")
            
            # Tabs for different sections
            prompt_tab1, prompt_tab2, prompt_tab3 = st.tabs(["Main Prompt", "Guardrails", "Prohibited Patterns"])
            
            with prompt_tab1:
                st.markdown("### Main System Prompt")
                st.caption("This prompt defines how the AI generates promotional messages")
                
                current_main_prompt = RetailSystemPrompts.get_system_prompt(selected_biz)
                edited_main_prompt = st.text_area(
                    "Edit Main System Prompt",
                    value=current_main_prompt,
                    height=400,
                    key="main_prompt"
                )
            
            with prompt_tab2:
                st.markdown("### Guardrail Response")
                st.caption("Response shown when unsafe queries are detected")
                
                current_guardrail = RetailSystemPrompts.get_guardrail_response(selected_biz)
                edited_guardrail = st.text_area(
                    "Edit Guardrail Response",
                    value=current_guardrail,
                    height=200,
                    key="guardrail"
                )
            
            with prompt_tab3:
                st.markdown("### Prohibited Patterns")
                st.caption("Comma-separated list of words/phrases to block")
                
                current_patterns = ', '.join(RetailSystemPrompts.get_prohibited_patterns(selected_biz))
                edited_patterns = st.text_area(
                    "Edit Prohibited Patterns",
                    value=current_patterns,
                    height=150,
                    key="patterns",
                    help="Separate patterns with commas"
                )
            
            # Save all sections
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💾 Save All Changes", type="primary"):
                    try:
                        # Reconstruct the file with all sections
                        new_content = f"""# {selected_biz.upper()} - System Prompts and Guardrails

## Main System Prompt

### Full Prompt

```
{edited_main_prompt}
```

---

## Guardrail Response

### Guardrail Response

```
{edited_guardrail}
```

---

## Prohibited Patterns

### Prohibited Patterns

```
{edited_patterns}
```
"""
                        with open(business_prompts_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        # Reload prompts
                        RetailSystemPrompts.reload_prompts(selected_biz)
                        
                        st.success("✅ All prompts saved and reloaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving: {e}")
            
            with col2:
                if st.button("🔄 Reload from File"):
                    RetailSystemPrompts.reload_prompts(selected_biz)
                    st.success("✅ Prompts reloaded!")
                    st.rerun()
            
            with col3:
                if st.button("↩️ Reset Form"):
                    st.rerun()
            
            with col4:
                if st.button("📄 Use Default"):
                    if st.session_state.get('confirm_reset_prompts', False):
                        # Copy default prompts
                        default_file = RetailSystemPrompts.get_prompts_file(None)
                        if default_file.exists():
                            import shutil
                            shutil.copy2(default_file, business_prompts_file)
                            RetailSystemPrompts.reload_prompts(selected_biz)
                            st.success("✅ Reset to default prompts!")
                            st.session_state.confirm_reset_prompts = False
                            st.rerun()
                    else:
                        st.session_state.confirm_reset_prompts = True
                        st.warning("⚠️ Click again to reset to default")
        else:
            st.error(f"❌ Prompt file not found: {business_prompts_file}")
            
            if st.button("Create Prompts File"):
                success, message = RetailSystemPrompts.create_business_prompts_file(selected_biz, biz_info["data_dir"])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.divider()
        
        # Current prompts preview
        st.subheader("👁️ Current Active Prompts")
        st.caption(f"Prompts currently being used by {biz_info['name']}")
        
        with st.expander("🤖 Main System Prompt", expanded=False):
            st.code(RetailSystemPrompts.get_system_prompt(selected_biz), language="text")
        
        with st.expander("🛡️ Guardrail Response", expanded=False):
            st.code(RetailSystemPrompts.get_guardrail_response(selected_biz), language="text")
        
        with st.expander("⚠️ Prohibited Patterns", expanded=False):
            patterns = RetailSystemPrompts.get_prohibited_patterns(selected_biz)
            st.write(", ".join(patterns))
        
        st.divider()
        
        # Business info
        st.subheader("🏪 Business Information")
        st.json(biz_info)
        
        st.divider()
        
        # Vector DB stats
        if selected_biz in st.session_state.rag_engines:
            st.subheader("📊 Vector Database Statistics")
            try:
                stats = st.session_state.rag_engines[selected_biz].get_statistics()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Documents", stats['total_documents'])
                with col2:
                    st.json(stats['document_types'])
            except Exception as e:
                st.error(f"Error getting stats: {e}")
        
        st.divider()
        
        # Danger zone
        st.subheader("⚠️ Danger Zone")
        
        if st.button("🗑️ Clear Vector Database", type="secondary"):
            if st.session_state.get('confirm_clear_db', False):
                if selected_biz in st.session_state.rag_engines:
                    st.session_state.rag_engines[selected_biz].clear_database()
                    del st.session_state.rag_engines[selected_biz]
                    if selected_biz in st.session_state.data_processors:
                        del st.session_state.data_processors[selected_biz]
                    st.session_state.confirm_clear_db = False
                    st.success("✅ Vector database cleared!")
                    st.rerun()
            else:
                st.session_state.confirm_clear_db = True
                st.warning("⚠️ Click again to confirm deletion")


if __name__ == "__main__":
    main()