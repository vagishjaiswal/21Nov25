# 🛒 Indian Retail Promotional AI Agent - Enhanced

## Three Message Types Supported

### 1. 📱 Personalized Messages
- **What**: One-to-one messages for specific customers
- **Uses**: Customer profile, purchase history, preferences
- **Example**: "Hey Rahul! Remember that gaming mouse you bought?"

### 2. 📢 Broadcast Messages  
- **What**: Mass messages for all customers
- **Uses**: ONLY product data, NO customer personalization
- **Example**: "🎉 MEGA SALE! 50% OFF on smartphones!"

### 3. 🎊 Event/Festival Campaigns
- **What**: Automated campaigns for seasons/festivals/events
- **Uses**: Auto-discovers relevant products, optional customer segmentation
- **Example**: "Diwali Special for Mumbai Electronics Lovers!"

---

## Quick Start

```bash
# Run the enhanced app
streamlit run retail_promo_agent_enhanced.py

# OR run the original (personalized only)
streamlit run retail_promo_agent.py
```

---

## What's New?

### ✨ New Features

1. **Broadcast Messages Tab**
   - Select multiple items (1-5)
   - No customer personalization
   - Perfect for mass SMS/WhatsApp campaigns

2. **Event Campaign Tab**
   - Automatically finds relevant products based on:
     - Seasonal relevance in items CSV
     - Festival relevance in items CSV
   - Optional customer segmentation by:
     - Age group
     - Region
     - Loyalty points
   - Product filters (category, minimum discount)

3. **Enhanced Message History**
   - Tracks all three message types
   - Filter by type
   - View campaign statistics

### 🔧 Technical Changes

**New Functions Added**:
- `generate_broadcast_message()` - For item-only messages
- `generate_event_campaign_message()` - For event-based campaigns

**No Changes Required**:
- Data processor ✓
- RAG engine ✓
- System prompts ✓
- CSV structure ✓

---

## Data Requirements

### Items CSV Must Have:
```csv
item_id, item_name, category, brand, price, original_price, discount_percentage,
seasonal_relevance,    # e.g., "Winter,Monsoon"
festival_relevance,    # e.g., "Diwali,Holi"  
region_popular,        # e.g., "North,South"
specifications, keywords
```

### Users CSV (for segmentation):
```csv
user_id, name, age, age_group, gender, region, city, state,
favorite_categories, loyalty_points, preferred_language
```

### Purchase History CSV:
```csv
purchase_id, user_id, item_id, purchase_date, quantity,
total_amount, payment_method, rating, review
```

---

## Usage Examples

### Example 1: Diwali Campaign for Electronics (Mumbai, 26-35 age group)

1. Go to **🎊 Event Campaign** tab
2. Select:
   - Event: Diwali
   - Category: Electronics
   - Min Discount: 30%
3. Enable segmentation:
   - Age: 26-35
   - Region: West (Mumbai)
   - Loyalty: 1000+
4. Click **Generate**

**Result**: Targeted Diwali message with electronics, customized for young professionals in Mumbai

---

### Example 2: Weekend Flash Sale (All Customers)

1. Go to **📢 Broadcast** tab
2. Select items:
   - Samsung TV
   - LG Refrigerator  
   - Whirlpool Washing Machine
3. Set tone: "Urgent Deal"
4. Click **Generate**

**Result**: Urgent flash sale message for mass distribution

---

### Example 3: Birthday Offer (Individual Customer)

1. Go to **📱 Personalized** tab
2. Select customer: "Rahul Sharma"
3. Select item based on his history
4. Click **Generate**

**Result**: Personalized birthday message with product recommendation

---

## File Structure

```
retail_promo_agent_enhanced.py    # Enhanced main app (NEW)
retail_promo_agent.py             # Original app (personalized only)
retail_data_processor.py          # Processes CSV data
retail_rag_engine.py              # RAG implementation  
retail_config.py                  # System prompts
ENHANCED_IMPLEMENTATION_GUIDE.md  # Detailed guide
MODIFICATIONS_SUMMARY.md          # Code changes summary
README_ENHANCED.md                # This file
```

---

## Key Differences

| Feature | Personalized | Broadcast | Campaign |
|---------|--------------|-----------|----------|
| **Customer Data** | ✅ Required | ❌ Never used | ⚙️ Optional (segments) |
| **Item Selection** | 1 item | 1-5 items | Auto-discovered |
| **Purchase History** | ✅ Analyzed | ❌ Not used | ⚙️ For segments |
| **Customer Name** | ✅ In message | ❌ Never | ❌ Never |
| **Product Discovery** | Manual | Manual | **Automatic** |
| **Best For** | Individual promos | Mass campaigns | Event marketing |

---

## How It Works

### Broadcast Messages
```
Query: "Generate BROADCAST message (NO personalization)"
  ↓
Uses ONLY: Item details + discounts + context
  ↓
Result: Generic exciting message for all
```

### Campaign Messages
```
Event: "Diwali" + Type: "Festival"
  ↓
Auto-filters items with: festival_relevance.contains("Diwali")
  ↓
Applies: Category filter + Min discount filter
  ↓
Optional: Segments customers (age/region/loyalty)
  ↓
Generates: Festive campaign message with top products
```

---

## API Usage

All three types use the same OpenAI API but with different prompts:

```python
# Personalized
"Generate personalized message for Rahul, age 28, Mumbai..."

# Broadcast  
"Generate BROADCAST message (NO customer names/data)..."

# Campaign
"Generate Diwali CAMPAIGN for Electronics (Age 26-35, Mumbai)..."
```

---

## Benefits

### For Marketing Teams:
- **Time Saving**: Auto-generates campaign content
- **Consistency**: Same brand voice across all messages
- **Personalization**: Individual, broadcast, or targeted campaigns
- **Analytics**: Track message history and performance

### For Retail Businesses:
- **Multi-business Support**: Manage multiple stores
- **Data-driven**: Uses purchase history and preferences
- **Culturally Relevant**: Indian festivals, regions, languages
- **Flexible**: Choose personalization level based on need

---

## Troubleshooting

**Q: Broadcast messages mention customer names?**  
A: Check query - must say "do NOT personalize"

**Q: Campaign finds no products?**  
A: Check items CSV has `seasonal_relevance` and `festival_relevance` data

**Q: Segmentation returns 0 customers?**  
A: Broaden filters or check users CSV has proper age_group/region data

---

## Next Steps

1. **Upload Data**: Add your business and upload 3 CSVs
2. **Process Data**: Click "Process Data & Load to Vector DB"
3. **Generate Messages**: Choose your message type and start creating!

---

## Documentation

- **ENHANCED_IMPLEMENTATION_GUIDE.md** - Full technical guide
- **MODIFICATIONS_SUMMARY.md** - Code changes details
- **README_ENHANCED.md** - This quick start (you're here!)

---

## Support

For issues or questions:
1. Check the implementation guide
2. Review the modifications summary
3. Test with sample Z-Mart data first

---

## License

Same as original project

---

**Happy Message Creating! 🚀**
