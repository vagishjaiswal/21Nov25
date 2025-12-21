# CODE MODIFICATIONS SUMMARY

## Files to Modify

### 1. retail_promo_agent.py → retail_promo_agent_enhanced.py

**Add these two new functions:**

```python
def generate_broadcast_message(selected_biz, selected_items, context):
    """Generate broadcast message based ONLY on item data - NO customer personalization"""
    data = st.session_state.data_processors[selected_biz]
    rag_engine = st.session_state.rag_engines[selected_biz]
    
    # Get item details
    items_data = []
    for item_id in selected_items:
        item = data['items'][data['items']['item_id'] == item_id].iloc[0]
        items_data.append(item)
    
    # Build items description
    items_text = "\n\n".join([
        f"""Item: {item['item_name']}
- Category: {item['category']} - {item['subcategory']}
- Brand: {item['brand']}
- Price: ₹{item['price']} (Original: ₹{item['original_price']}, {item['discount_percentage']}% OFF)
- Description: {item['description']}
- Seasonal: {item['seasonal_relevance']}
- Festival: {item['festival_relevance']}
- Specifications: {item['specifications']}"""
        for item in items_data
    ])
    
    # Build query - CRITICAL: No customer personalization
    query = f"""Generate a BROADCAST promotional message for the following item(s). 
This message will be sent to ALL customers, so do NOT personalize to any specific customer.

ITEMS TO PROMOTE:
{items_text}

Context:
- Current Season: {context['season']}
- Upcoming Festival: {context['festival']}
- Message Tone: {context['tone']}
- Target Audience: {context.get('target_audience', 'All Customers')}

CREATE A BROADCAST MESSAGE THAT:
1. Highlights product features and benefits
2. Emphasizes discounts and savings
3. Creates excitement and urgency
4. Appeals to a WIDE audience (no specific names/locations)
5. Includes clear call-to-action
6. Uses the specified tone ({context['tone']})

Make it engaging and suitable for mass distribution via SMS/WhatsApp!
"""
    
    message, sources = rag_engine.query(query)
    return message, sources, items_data


def generate_event_campaign_message(selected_biz, event_details, target_segment=None):
    """Generate campaign messages for events/festivals/seasons with optional targeting"""
    data = st.session_state.data_processors[selected_biz]
    rag_engine = st.session_state.rag_engines[selected_biz]
    items_df = data['items']
    
    # Auto-discover relevant products based on event
    if event_details['type'] == 'Season':
        relevant_items = items_df[
            items_df['seasonal_relevance'].str.contains(event_details['name'], case=False, na=False)
        ]
    elif event_details['type'] == 'Festival':
        relevant_items = items_df[
            items_df['festival_relevance'].str.contains(event_details['name'], case=False, na=False)
        ]
    else:
        relevant_items = items_df
    
    # Apply filters
    if event_details.get('category'):
        relevant_items = relevant_items[relevant_items['category'] == event_details['category']]
    
    if event_details.get('min_discount'):
        relevant_items = relevant_items[
            relevant_items['discount_percentage'] >= event_details['min_discount']
        ]
    
    # Sort by discount, take top 10
    relevant_items = relevant_items.sort_values('discount_percentage', ascending=False).head(10)
    
    # Optional customer segmentation
    users_data = None
    if target_segment and target_segment.get('use_segment'):
        users_df = data['users']
        if target_segment.get('age_group'):
            users_df = users_df[users_df['age_group'] == target_segment['age_group']]
        if target_segment.get('region'):
            users_df = users_df[users_df['region'] == target_segment['region']]
        if target_segment.get('min_loyalty_points'):
            users_df = users_df[users_df['loyalty_points'] >= target_segment['min_loyalty_points']]
        users_data = users_df
    
    # Build query
    items_summary = "\n".join([
        f"- {row['item_name']} ({row['brand']}): ₹{row['price']} ({row['discount_percentage']}% OFF)"
        for _, row in relevant_items.iterrows()
    ])
    
    segment_info = ""
    if users_data is not None and len(users_data) > 0:
        segment_info = f"""
TARGET AUDIENCE SEGMENT ({len(users_data)} customers):
- Age Group: {target_segment.get('age_group', 'All')}
- Region: {target_segment.get('region', 'All')}
- Loyalty Points: {target_segment.get('min_loyalty_points', 0)}+
"""
    
    query = f"""Generate a {event_details['type'].upper()} CAMPAIGN promotional message.

EVENT DETAILS:
- Type: {event_details['type']}
- Name: {event_details['name']}
- Date: {event_details.get('date', 'Upcoming')}
- Duration: {event_details.get('duration', 'Limited Time')}

{segment_info}

RELEVANT PRODUCTS ({len(relevant_items)} items):
{items_summary}

Campaign Strategy: {event_details.get('strategy', 'Create excitement around this event')}
Message Tone: {event_details.get('tone', 'Exciting and Festive')}

CREATE A CAMPAIGN MESSAGE THAT:
1. Announces the {event_details['type']} and creates excitement
2. Highlights top deals relevant to {event_details['name']}
3. Creates urgency
4. {f"Targets {target_segment.get('age_group', '')} {target_segment.get('region', '')} customers" if target_segment and target_segment.get('use_segment') else "Appeals to all customers"}
5. Uses Indian cultural references for {event_details['name']}
6. Includes multiple product options
7. Has strong call-to-action

Make it festive and compelling!
"""
    
    message, sources = rag_engine.query(query)
    return message, sources, relevant_items, users_data
```

---

### 2. Update main() function

**Change tabs from 4 to 6:**

```python
# OLD:
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Generate Messages", 
    "📤 Upload Data", 
    "📊 View Data",
    "⚙️ Settings"
])

# NEW:
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📱 Personalized",       # Existing functionality  
    "📢 Broadcast",          # NEW - Item-only messages
    "🎊 Event Campaign",     # NEW - Event-based campaigns
    "📤 Upload Data", 
    "📊 View Data",
    "⚙️ Settings"
])
```

---

### 3. Add Tab 2: Broadcast Messages

```python
with tab2:
    st.header("📢 Broadcast Promotional Messages")
    st.caption("Generate mass messages based on product features only")
    
    if selected_biz not in st.session_state.rag_engines:
        st.warning("⚠️ Please upload and process data first")
    else:
        data = st.session_state.data_processors[selected_biz]
        
        st.info("💡 Broadcast Mode: NO customer personalization")
        
        # Multi-select items (max 5)
        item_ids = data['items']['item_id'].tolist()
        selected_items = st.multiselect(
            "🛍️ Select Items (1-5)",
            item_ids,
            format_func=lambda x: f"{x} - {data['items'][data['items']['item_id']==x]['item_name'].values[0]}",
            max_selections=5
        )
        
        if selected_items:
            # Show selected
            for item_id in selected_items:
                item = data['items'][data['items']['item_id']==item_id].iloc[0]
                st.write(f"✓ {item['item_name']} - ₹{item['price']} ({item['discount_percentage']}% OFF)")
            
            st.divider()
            
            # Context inputs
            col1, col2 = st.columns(2)
            with col1:
                bc_season = st.selectbox("🌦️ Season", ["Winter", "Summer", "Monsoon", "Spring", "Autumn"], key="bc_season")
                bc_festival = st.selectbox("🎉 Festival", ["None", "Diwali", "Holi", "Eid", "Christmas", "New Year"], key="bc_festival")
            with col2:
                bc_tone = st.selectbox("🎭 Tone", ["Funny Meme", "Urgent Deal", "Friendly", "Poetic"], key="bc_tone")
                bc_audience = st.selectbox("🎯 Audience", ["All Customers", "Young Adults", "Families"], key="bc_audience")
            
            # Generate button
            if st.button("📢 Generate Broadcast Message", type="primary"):
                with st.spinner("Creating broadcast message..."):
                    context = {
                        'season': bc_season,
                        'festival': bc_festival,
                        'tone': bc_tone,
                        'target_audience': bc_audience
                    }
                    
                    message, sources, items_data = generate_broadcast_message(
                        selected_biz, selected_items, context
                    )
                    
                    st.markdown("### 📢 Broadcast Message")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                padding: 30px; border-radius: 15px; color: white;">
                    {message.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Customers", len(data['users']))
                    with col2:
                        avg_discount = sum([item['discount_percentage'] for item in items_data]) / len(items_data)
                        st.metric("Avg Discount", f"{avg_discount:.1f}%")
                    with col3:
                        total_savings = sum([item['original_price'] - item['price'] for item in items_data])
                        st.metric("Total Savings", f"₹{total_savings:.0f}")
                    
                    st.code(message, language=None)
                    
                    # Save to history
                    if selected_biz not in st.session_state.chat_history:
                        st.session_state.chat_history[selected_biz] = []
                    st.session_state.chat_history[selected_biz].append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'broadcast',
                        'items': selected_items,
                        'message': message,
                        'context': context
                    })
```

---

### 4. Add Tab 3: Event Campaigns

```python
with tab3:
    st.header("🎊 Event/Festival Campaign Messages")
    st.caption("Automated campaign generation for seasons, festivals, events")
    
    if selected_biz not in st.session_state.rag_engines:
        st.warning("⚠️ Please upload and process data first")
    else:
        data = st.session_state.data_processors[selected_biz]
        
        st.info("💡 Campaign Mode: Auto-finds relevant products, optional customer targeting")
        
        # Event config
        col1, col2 = st.columns(2)
        with col1:
            event_type = st.selectbox("📅 Event Type", ["Festival", "Season", "Special Event"])
            if event_type == "Festival":
                event_name = st.selectbox("🎉 Festival", ["Diwali", "Holi", "Eid", "Christmas", "New Year"])
            elif event_type == "Season":
                event_name = st.selectbox("🌦️ Season", ["Winter", "Summer", "Monsoon", "Spring", "Autumn"])
            else:
                event_name = st.text_input("📝 Event Name", placeholder="e.g., Grand Opening")
        
        with col2:
            event_date = st.date_input("📆 Date")
            event_duration = st.selectbox("⏱️ Duration", ["1 Day", "3 Days", "1 Week", "2 Weeks", "1 Month"])
        
        # Product filters
        st.markdown("#### 🎯 Product Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            categories = ['All'] + data['items']['category'].unique().tolist()
            selected_category = st.selectbox("Category", categories)
        with col2:
            min_discount = st.slider("Min Discount %", 0, 100, 20)
        with col3:
            campaign_tone = st.selectbox("🎭 Tone", ["Festive & Exciting", "Urgent Deal", "Friendly"])
        
        # Optional segmentation
        st.markdown("#### 👥 Target Audience (Optional)")
        use_segmentation = st.checkbox("Enable customer segmentation")
        
        target_segment = None
        if use_segmentation:
            col1, col2, col3 = st.columns(3)
            with col1:
                age_groups = ['All'] + data['users']['age_group'].unique().tolist()
                seg_age = st.selectbox("Age Group", age_groups)
            with col2:
                regions = ['All'] + data['users']['region'].unique().tolist()
                seg_region = st.selectbox("Region", regions)
            with col3:
                seg_loyalty = st.number_input("Min Loyalty Points", 0, 10000, 0, 100)
            
            target_segment = {
                'age_group': None if seg_age == 'All' else seg_age,
                'region': None if seg_region == 'All' else seg_region,
                'min_loyalty_points': seg_loyalty,
                'use_segment': True
            }
        
        campaign_strategy = st.text_area("📝 Strategy", placeholder="Campaign goals...")
        
        # Generate button
        if st.button("🎊 Generate Campaign", type="primary"):
            if not event_name:
                st.error("Please provide event name")
            else:
                with st.spinner(f"Creating {event_name} campaign..."):
                    event_details = {
                        'type': event_type,
                        'name': event_name,
                        'date': event_date.strftime('%B %d, %Y'),
                        'duration': event_duration,
                        'category': None if selected_category == 'All' else selected_category,
                        'min_discount': min_discount,
                        'tone': campaign_tone,
                        'strategy': campaign_strategy or f"Create excitement for {event_name}"
                    }
                    
                    message, sources, relevant_items, users_data = generate_event_campaign_message(
                        selected_biz, event_details, target_segment
                    )
                    
                    st.markdown(f"### 🎊 {event_name} Campaign")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                                padding: 30px; border-radius: 15px; color: #333;">
                    {message.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Campaign stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Products", len(relevant_items))
                    with col2:
                        target_count = len(users_data) if users_data is not None else len(data['users'])
                        st.metric("Customers", target_count)
                    with col3:
                        st.metric("Avg Discount", f"{relevant_items['discount_percentage'].mean():.1f}%")
                    with col4:
                        st.metric("Total Stock", f"{relevant_items['stock_quantity'].sum():,}")
                    
                    # Show products
                    with st.expander(f"🛍️ Campaign Products ({len(relevant_items)})"):
                        st.dataframe(relevant_items[['item_name', 'brand', 'price', 'discount_percentage']])
                    
                    st.code(message, language=None)
                    
                    # Save to history
                    if selected_biz not in st.session_state.chat_history:
                        st.session_state.chat_history[selected_biz] = []
                    st.session_state.chat_history[selected_biz].append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'campaign',
                        'event': event_details,
                        'message': message,
                        'products_count': len(relevant_items),
                        'customers_count': target_count
                    })
```

---

## That's It!

### Summary of Changes:

1. **Added 2 new functions**: `generate_broadcast_message()` and `generate_event_campaign_message()`
2. **Added 2 new tabs**: "Broadcast" and "Event Campaign"
3. **Updated message history**: Now tracks message type (personalized/broadcast/campaign)

### Key Differences:

| Feature | Personalized | Broadcast | Campaign |
|---------|--------------|-----------|----------|
| User Selection | ✅ Required | ❌ None | ⚙️ Optional (segmented) |
| Item Selection | 1 item | 1-5 items | Auto-discovered |
| Purchase History | ✅ Used | ❌ Not used | ⚙️ Used for segments |
| Customer Name | ✅ In message | ❌ Never | ❌ Never |
| Product Filtering | Manual | Manual | Automatic + filters |

### Files Modified:
- `retail_promo_agent.py` → `retail_promo_agent_enhanced.py` (with new functions and tabs)

### No Changes Needed:
- `retail_data_processor.py` ✓
- `retail_rag_engine.py` ✓
- `retail_config.py` ✓
- CSV structure ✓

The system now supports all three message types! 🎉
