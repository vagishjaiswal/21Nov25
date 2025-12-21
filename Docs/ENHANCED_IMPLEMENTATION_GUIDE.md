# Enhanced Retail Promotional AI Agent - Implementation Guide

## Overview

This enhanced system supports **THREE types of message generation**:

1. **📱 Personalized Messages** - One-to-one messages for specific customers
2. **📢 Broadcast Messages** - Mass messages based only on product data
3. **🎊 Event/Festival Campaigns** - Targeted campaigns for seasons/festivals/events

---

## Key Modifications Made

### 1. New Functions Added

#### `generate_broadcast_message(selected_biz, selected_items, context)`
- **Purpose**: Generate broadcast messages WITHOUT customer personalization
- **Input**: 
  - Multiple items (1-5)
  - Context (season, festival, tone, target audience)
- **Output**: Message suitable for mass distribution
- **Key Feature**: NO use of specific customer data

```python
def generate_broadcast_message(selected_biz, selected_items, context):
    """Generate broadcast message based only on item data"""
    # Collects item details only
    # Builds query emphasizing product features, discounts
    # Returns message suitable for ALL customers
```

#### `generate_event_campaign_message(selected_biz, event_details, target_segment=None)`
- **Purpose**: Generate campaign messages for events/festivals/seasons
- **Input**:
  - Event details (type, name, date, duration)
  - Optional customer segmentation filters
  - Product filters (category, min discount)
- **Output**: Campaign message with relevant products
- **Key Features**:
  - Automatically finds relevant products based on event
  - Can target specific customer segments (age, region, loyalty)
  - Analyzes purchase history for targeted campaigns

```python
def generate_event_campaign_message(selected_biz, event_details, target_segment=None):
    """Generate campaign messages for upcoming events/festivals/seasons"""
    # Filters items by season/festival relevance
    # Applies discount filters
    # Optionally segments customers
    # Returns campaign message with product recommendations
```

---

## How to Use Each Message Type

### 1. Personalized Messages (Tab 1)

**Use Case**: Individual customer promotions based on their profile

**Steps**:
1. Select a specific customer from dropdown
2. Select an item to promote
3. Choose season, festival, and tone
4. Click "Generate Personalized Message"

**What the AI considers**:
- Customer name, age, location
- Purchase history
- Favorite categories
- Loyalty points
- Item specifications and discounts
- Seasonal/festival relevance

**Example Output**:
```
Hey Rahul! 🙌
Remember that awesome gaming mouse you bought last month? 
We've got something even BETTER for you! 💥

The Logitech G502 HERO is now 40% OFF at just ₹3,999! 
(Original: ₹6,500)

Your fellow Mumbai gamers are going CRAZY for this deal! 🎮
Stock is flying off the shelves! ⚡

Grab yours NOW: [Link]
Limited stock, bro! Don't miss out! 🚀
```

---

### 2. Broadcast Messages (Tab 2)

**Use Case**: Mass promotional messages for all customers

**Steps**:
1. Select 1-5 items to promote
2. Choose season, festival, tone
3. Select target audience type (optional general targeting)
4. Click "Generate Broadcast Message"

**What the AI considers**:
- **ONLY** product features, prices, discounts
- **NO** specific customer data
- General appeal to target audience type
- Season/festival context

**Example Output**:
```
🎉 MEGA DIWALI SALE IS HERE! 🎉

💥 50% OFF on Premium Smartphones!
Samsung Galaxy S23 - NOW ₹39,999 (was ₹79,999)
iPhone 14 - NOW ₹59,999 (was ₹79,999)

🎁 Plus FREE gifts worth ₹5,000!
⚡ Today ONLY! Limited Stock!

Order NOW: [Link]
Diwali ki shopping, ab aur bhi special! ✨
```

---

### 3. Event/Festival Campaign Messages (Tab 3)

**Use Case**: Campaign planning for upcoming events with automated product selection

**Steps**:
1. Select event type (Festival/Season/Special Event)
2. Choose event name (e.g., Diwali, Winter, Grand Opening)
3. Set event date and duration
4. Apply product filters (category, min discount)
5. **Optional**: Enable customer segmentation
   - Filter by age group
   - Filter by region
   - Filter by loyalty points
6. Add campaign strategy notes
7. Click "Generate Campaign Message"

**What the AI does**:
- **Automatically finds** relevant products based on event
- Filters by seasonal/festival relevance in product data
- Applies discount and category filters
- If segmentation enabled: targets specific customer group
- Analyzes purchase patterns for the segment

**Example Output (with segmentation)**:
```
🎊 SPECIAL DIWALI OFFER for our Mumbai Electronics Lovers! 🎊

Namaste Friends! 🙏

This Diwali, light up your homes with our BIGGEST tech deals ever!

🔥 TOP PICKS FOR YOU:
📱 Samsung 4K Smart TV (55") - ₹34,999 (60% OFF!)
💻 HP Pavilion Laptop - ₹42,999 (45% OFF!)
🎮 PS5 Console Bundle - ₹44,999 (30% OFF!)

✨ Special for our loyal customers:
EXTRA 10% OFF with your loyalty points!

📍 Available at all Mumbai stores
🚚 FREE delivery within 24 hours
💳 EMI options available

Diwali Dhamaka - 3 DAYS ONLY!
Order before Oct 24th!

Shop NOW: [Link]

Iss Diwali, ghar ko banao smart! 🏠✨
```

**Example Output (no segmentation - broadcast style)**:
```
🌸 HOLI COLORS SALE! 🌸

Rang barse! And so do our prices! 💥

🎨 HOME & LIFESTYLE FEST:
- Colorful Bedsheets - Starting ₹499
- Designer Cushions - Buy 2 Get 1 FREE
- Rangoli Stencils - Flat 50% OFF
- Pichkari Sets - Starting ₹99

🎁 PLUS: Free Herbal Gulal with every purchase!

Sale ends March 7th! ⏰

Play Holi in style! 🎉
Order: [Link]
```

---

## Technical Implementation Details

### Modified retail_promo_agent.py

**New Tabs Added**:
- Tab 2: "📢 Broadcast" - For item-only messages
- Tab 3: "🎊 Event Campaign" - For event-based campaigns

**Key Changes**:

1. **Broadcast Message Generation**:
   - Multi-select for items (up to 5)
   - Context inputs (season, festival, tone, audience type)
   - Query specifically instructs: "do NOT personalize to any specific customer"
   - Emphasizes product features and general appeal

2. **Campaign Message Generation**:
   - Event configuration (type, name, date, duration)
   - Product filters (category, minimum discount)
   - Automatic product discovery based on:
     - `seasonal_relevance` field in items CSV
     - `festival_relevance` field in items CSV
   - Optional customer segmentation:
     - Age group filter
     - Region filter  
     - Loyalty points filter
   - Purchase history analysis for segments
   - Campaign strategy input

3. **Query Construction**:
   - **Personalized**: Includes full customer profile + item details
   - **Broadcast**: ONLY item details + general context
   - **Campaign**: Event details + relevant items + optional segment data

---

## Data Requirements

### Items CSV
Must include these fields for campaign generation:
- `seasonal_relevance` - e.g., "Winter,Monsoon", "Summer", "All Seasons"
- `festival_relevance` - e.g., "Diwali,Holi", "Christmas,New Year", "None"
- `region_popular` - e.g., "North,South", "Mumbai,Delhi"

### Users CSV
For customer segmentation in campaigns:
- `age_group` - e.g., "18-25", "26-35", "36-50", "50+"
- `region` - e.g., "North", "South", "East", "West"
- `loyalty_points` - Integer value
- `favorite_categories` - For interest matching

### Purchase History CSV
Used for:
- Segment behavior analysis
- Product recommendation in campaigns
- Understanding customer preferences

---

## System Prompts Handling

Each message type uses the same base system prompt from `retail_config.py`, but with different query contexts:

1. **Personalized**: Query includes customer data → AI personalizes
2. **Broadcast**: Query explicitly states "no personalization" → AI creates general message
3. **Campaign**: Query includes event context + optional segment → AI creates targeted campaign

---

## Workflow Examples

### Scenario 1: Launch a Diwali Campaign for Electronics

1. Go to "🎊 Event Campaign" tab
2. Select:
   - Event Type: Festival
   - Event Name: Diwali
   - Date: Oct 24, 2024
   - Duration: 1 Week
   - Category: Electronics
   - Min Discount: 30%
3. Enable segmentation (optional):
   - Age Group: 26-35
   - Region: North
   - Min Loyalty: 1000
4. Add strategy: "Target tech-savvy customers with premium products"
5. Generate

**Result**: Campaign message featuring top electronics with 30%+ discounts, targeted to 26-35 age group in North region with loyalty points

---

### Scenario 2: Weekend Flash Sale Broadcast

1. Go to "📢 Broadcast" tab
2. Select items:
   - Samsung TV
   - LG Refrigerator
   - Whirlpool Washing Machine
3. Choose:
   - Season: Current
   - Festival: None
   - Tone: Urgent Deal
   - Audience: All Customers
4. Generate

**Result**: Urgent flash sale message highlighting all 3 items, suitable for mass SMS/WhatsApp

---

### Scenario 3: Birthday Special for Individual Customer

1. Go to "📱 Personalized" tab
2. Select customer: C001 - Rahul Sharma
3. Select item based on his purchase history
4. Choose appropriate tone
5. Generate

**Result**: Personalized birthday message with product recommendation based on Rahul's preferences

---

## Message History Tracking

All generated messages are saved with:
- Timestamp
- Message type (personalized/broadcast/campaign)
- Context used
- Products included
- Customer count (for campaigns)

View in "📊 View Data" tab → Message Generation History section

---

## Best Practices

### For Broadcast Messages:
- Select products with strong discounts (30%+)
- Use urgent or exciting tones
- Keep it short and punchy
- Focus on value proposition
- Include clear call-to-action

### For Campaign Messages:
- Plan ahead - set appropriate event dates
- Use meaningful segmentation (don't over-filter)
- Let the system find relevant products automatically
- Review the products list before sending
- Test with small segments first

### For Personalized Messages:
- Check customer's recent purchase history
- Match products to their favorite categories
- Consider their region for cultural references
- Use appropriate language preference

---

## API Integration Notes

The system uses OpenAI API through the RAG engine. Each message type sends different prompts:

```python
# Personalized
query = f"Generate PERSONALIZED message for {customer_name}..."

# Broadcast  
query = f"Generate BROADCAST message (NO personalization)..."

# Campaign
query = f"Generate {event_type} CAMPAIGN message..."
```

The RAG engine retrieves relevant context from vector store and generates accordingly.

---

## Troubleshooting

### Issue: Broadcast messages still seem personalized
**Solution**: Check the query prompt - ensure it explicitly states "do NOT personalize"

### Issue: Campaign finds no relevant products
**Solution**: 
- Check items CSV has proper `seasonal_relevance` and `festival_relevance` data
- Lower the minimum discount filter
- Remove category filter

### Issue: Customer segmentation returns 0 customers
**Solution**:
- Broaden the filters
- Check users CSV has proper age_group, region data
- Remove loyalty points filter

---

## Future Enhancements

1. **Bulk Campaign Generation**: Generate multiple campaigns at once
2. **A/B Testing**: Create multiple variations for testing
3. **Analytics Dashboard**: Track message performance
4. **Scheduled Campaigns**: Schedule messages for future dates
5. **Multi-language Support**: Generate in regional languages
6. **Image Generation**: Add promotional images to messages

---

## File Structure

```
retail_promo_agent_enhanced.py       # Main Streamlit app (enhanced)
retail_data_processor.py              # Processes CSV data
retail_rag_engine.py                  # RAG implementation
retail_config.py                      # System prompts
ENHANCED_IMPLEMENTATION_GUIDE.md      # This file
```

---

## Quick Start Command

```bash
# Install dependencies
pip install -r retail_requirements.txt

# Run the enhanced app
streamlit run retail_promo_agent_enhanced.py
```

---

## Summary

The enhanced system now supports:
✅ Personalized one-to-one messages
✅ Broadcast messages (item-only, no customer data)
✅ Event/Festival campaigns with auto product discovery
✅ Optional customer segmentation for campaigns  
✅ Purchase history analysis
✅ Multiple message tones
✅ Message history tracking

All three modes use the same infrastructure but with different query strategies to achieve the desired personalization level.
