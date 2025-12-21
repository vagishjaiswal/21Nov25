# Enhanced Retail Promotional AI Agent - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB INTERFACE                      │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ├───────────────────────────────────┐
                               │                                   │
                               ▼                                   ▼
┌──────────────────────────────────────┐    ┌──────────────────────────────┐
│      Business Management             │    │   Data Upload & Processing   │
│  • Register business                 │    │  • Upload CSVs               │
│  • Select business                   │    │  • Process & vectorize       │
│  • Delete business                   │    │  • Load to vector store      │
└──────────────────────────────────────┘    └──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐     ┌───────────────┐     ┌────────────────┐
│  PERSONALIZED │     │   BROADCAST   │     │ EVENT CAMPAIGN │
│   MESSAGES    │     │   MESSAGES    │     │    MESSAGES    │
└───────────────┘     └───────────────┘     └────────────────┘
        │                      │                      │
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────────────────────────────────────────────────────┐
│                  MESSAGE GENERATION ENGINE                     │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │  Customer   │  │  Item Data   │  │  Purchase History │   │
│  │   Profiles  │  │   Catalog    │  │    Analytics      │   │
│  └─────────────┘  └──────────────┘  └───────────────────┘   │
│                                                                │
│                         ↓                                      │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            RAG ENGINE (Retail Focused)                  │  │
│  │  • Vector Store (ChromaDB)                             │  │
│  │  • Context Retrieval                                   │  │
│  │  • OpenAI API Integration                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│                         ↓                                      │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         SYSTEM PROMPTS (Business-Specific)              │  │
│  │  • Retail promotional tone                             │  │
│  │  • Indian cultural context                             │  │
│  │  • Multiple message tones                              │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GENERATED MESSAGES                            │
│  • Personalized (1-to-1)                                        │
│  • Broadcast (Mass distribution)                                │
│  • Campaign (Event-based, targeted)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Message Generation Flow

### 1. Personalized Message Flow

```
User Action: Select Customer + Item
        │
        ▼
Retrieve Customer Profile
 • Name, Age, Location
 • Purchase History
 • Preferences, Loyalty
        │
        ▼
Retrieve Item Details
 • Price, Discount
 • Specifications
 • Seasonal/Festival relevance
        │
        ▼
Build Personalized Query
 "Generate for [Customer Name]..."
        │
        ▼
RAG Engine Retrieval
 • Customer context chunks
 • Item detail chunks
 • Purchase history chunks
        │
        ▼
OpenAI API Call
 System Prompt + Query + Context
        │
        ▼
Generated Message
 "Hey Rahul! 😊 Remember your love for gaming?
  Check out this 40% OFF deal..."
```

---

### 2. Broadcast Message Flow

```
User Action: Select Items (1-5)
        │
        ▼
Retrieve Item Details ONLY
 • No customer data
 • Price, Discounts
 • Features
        │
        ▼
Build Broadcast Query
 "Generate BROADCAST (NO personalization)..."
        │
        ▼
RAG Engine Retrieval
 • Item detail chunks ONLY
 • No customer chunks
        │
        ▼
OpenAI API Call
 System Prompt + Query + Item Context
        │
        ▼
Generated Message
 "🎉 MEGA SALE! 50% OFF on Electronics!
  Samsung TV, LG Fridge, and more..."
```

---

### 3. Campaign Message Flow

```
User Action: Define Event + Filters
 • Event Type (Festival/Season)
 • Event Name (Diwali/Winter)
 • Product Filters (Category, Min Discount)
 • Optional: Customer Segment Filters
        │
        ▼
Auto-Discover Products
 Filter items WHERE:
  - seasonal_relevance CONTAINS event
  - festival_relevance CONTAINS event
  - discount >= min_discount
  - category = selected (if any)
        │
        ▼
Sort by Discount (Top 10)
        │
        ▼
Optional: Segment Customers
 IF segmentation enabled:
  Filter users WHERE:
   - age_group = selected
   - region = selected
   - loyalty_points >= min
        │
        ▼
Build Campaign Query
 "Generate [EVENT] CAMPAIGN for [Products]
  Targeting [Segment]..."
        │
        ▼
RAG Engine Retrieval
 • Product chunks (auto-discovered)
 • Segment behavior chunks (if enabled)
 • Seasonal/festival context
        │
        ▼
OpenAI API Call
 System Prompt + Query + Context
        │
        ▼
Generated Message
 "🎊 Diwali Special for Mumbai!
  Top Electronics - 30-60% OFF!
  Samsung TV, iPhone, PS5..."
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       CSV FILES                              │
├─────────────────────────────────────────────────────────────┤
│  items.csv              users.csv         purchase_history  │
│  • item_id              • user_id         • purchase_id     │
│  • item_name            • name            • user_id         │
│  • category             • age_group       • item_id         │
│  • price                • region          • date            │
│  • discount             • loyalty         • rating          │
│  • seasonal_relevance   • preferences     • review          │
│  • festival_relevance                                       │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              RetailDataProcessor                             │
├─────────────────────────────────────────────────────────────┤
│  process_retail_data()                                      │
│   ├─> _process_items()         → Item chunks                │
│   ├─> _process_users()         → User profile chunks        │
│   ├─> _process_purchase_history() → History chunks          │
│   └─> _create_insights()       → Aggregate insights         │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Document Chunks                            │
├─────────────────────────────────────────────────────────────┤
│  Chunk Type: "item"                                         │
│   Metadata: {item_id, category, price, discount}            │
│   Text: Full item description                               │
│                                                              │
│  Chunk Type: "user"                                         │
│   Metadata: {user_id, age_group, region}                    │
│   Text: Customer profile                                    │
│                                                              │
│  Chunk Type: "purchase_history"                             │
│   Metadata: {user_id, total_spent, avg_rating}              │
│   Text: Purchase patterns                                   │
│                                                              │
│  Chunk Type: "insight"                                      │
│   Metadata: {insight_type}                                  │
│   Text: Aggregated analytics                                │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              ChromaDB Vector Store                           │
├─────────────────────────────────────────────────────────────┤
│  Collection: [business_id]_collection                       │
│   • Embeddings (OpenAI ada-002)                             │
│   • Metadata filters                                        │
│   • Similarity search                                       │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                RAG Engine Query                              │
├─────────────────────────────────────────────────────────────┤
│  query(user_query, filters)                                 │
│   ├─> Embed query                                           │
│   ├─> Search vector store (top-k=5)                         │
│   ├─> Retrieve relevant chunks                              │
│   ├─> Build context                                         │
│   └─> Call OpenAI with system prompt + context + query      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   OpenAI API                                 │
├─────────────────────────────────────────────────────────────┤
│  Model: GPT-4 / GPT-3.5-turbo                               │
│  Input: System Prompt + Context + User Query                │
│  Output: Generated promotional message                      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Generated Message                               │
├─────────────────────────────────────────────────────────────┤
│  • Creative, engaging text                                  │
│  • Culturally relevant (Indian context)                     │
│  • Appropriate tone (meme/tapori/emotional)                 │
│  • Action-oriented call-to-action                           │
│  • Emojis and Hinglish mix                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Interactions

```
┌───────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Sidebar:    │  │ Main Area:  │  │ Session State:      │  │
│  │ • Businesses│  │ • Tabs      │  │ • selected_business │  │
│  │ • Select    │  │ • Forms     │  │ • rag_engines       │  │
│  │ • Add/Del   │  │ • Results   │  │ • data_processors   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Business Manager │  │ Data         │  │ RAG Engine       │
│                  │  │ Processor    │  │                  │
│ • Register biz   │  │              │  │ • Query vector   │
│ • Save CSVs      │  │ • Process    │  │ • Call OpenAI    │
│ • Get config     │  │ • Chunk      │  │ • Return msg     │
│ • Delete biz     │  │ • Vectorize  │  │                  │
└──────────────────┘  └──────────────┘  └──────────────────┘
        │                      │                    │
        ▼                      ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│              Persistent Storage                           │
│  • retail_businesses/[biz_id]/                           │
│    ├─ [biz_id]_items.csv                                 │
│    ├─ [biz_id]_users.csv                                 │
│    ├─ [biz_id]_purchase_history.csv                      │
│    └─ [biz_id]_prompts.md                                │
│  • retail_vector_dbs/[biz_id]/                           │
│    └─ ChromaDB files                                     │
│  • businesses_config.json                                │
└──────────────────────────────────────────────────────────┘
```

---

## Query Processing Pipeline

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────────┐
│ Message Type Selection                  │
│ • Personalized → Include customer data  │
│ • Broadcast    → EXCLUDE customer data  │
│ • Campaign     → Auto-discover + filter │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Query Builder                           │
│ • Format: "[TYPE] message for..."      │
│ • Include: Context, filters, segment   │
│ • Exclude: Based on message type       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ RAG Context Retrieval                   │
│ • Embed query → similarity search       │
│ • Filter by metadata (type, category)  │
│ • Retrieve top-k chunks (k=5)           │
│ • Aggregate context text                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ System Prompt Selection                 │
│ • Load business-specific prompt         │
│ • Or fallback to default                │
│ • Check guardrails                      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ OpenAI API Call                         │
│ • Messages: [system, user]              │
│ • Temperature: 0.7                      │
│ • Max tokens: 500                       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Post-Processing                         │
│ • Validate output                       │
│ • Format for display                    │
│ • Save to history                       │
└─────────────────────────────────────────┘
    │
    ▼
GENERATED MESSAGE
```

---

## Multi-Business Architecture

```
┌───────────────────────────────────────────────────────────┐
│                Global Configuration                        │
│  businesses_config.json                                   │
│  {                                                         │
│    "zmart": {                                             │
│      "name": "Z-Mart",                                    │
│      "data_dir": "retail_businesses/zmart/",             │
│      "db_dir": "retail_vector_dbs/zmart/",               │
│      "csv_files": {...}                                   │
│    },                                                      │
│    "bigbazaar": {...},                                    │
│    "reliance_fresh": {...}                                │
│  }                                                         │
└───────────────────────────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ Z-Mart          │  │ BigBazaar       │  │ Reliance Fresh   │
│                 │  │                 │  │                  │
│ • Own CSVs      │  │ • Own CSVs      │  │ • Own CSVs       │
│ • Own VectorDB  │  │ • Own VectorDB  │  │ • Own VectorDB   │
│ • Own Prompts   │  │ • Own Prompts   │  │ • Own Prompts    │
│ • Own History   │  │ • Own History   │  │ • Own History    │
└─────────────────┘  └─────────────────┘  └──────────────────┘

Each business is completely isolated!
```

---

## Key Design Decisions

### 1. Message Type Differentiation
- **Personalized**: Query includes "for [Customer Name]"
- **Broadcast**: Query includes "do NOT personalize"
- **Campaign**: Query includes "[EVENT] CAMPAIGN"

### 2. Product Discovery
- **Manual**: Personalized & Broadcast (user selects)
- **Automatic**: Campaign (filters by relevance fields)

### 3. Context Retrieval
- **Full**: Personalized (customer + item + history)
- **Limited**: Broadcast (items only)
- **Filtered**: Campaign (relevant products + optional segment)

### 4. Data Isolation
- Each business has separate vector store
- No data mixing between businesses
- Business-specific system prompts

---

This architecture ensures:
✅ Scalability (multiple businesses)
✅ Flexibility (three message types)
✅ Privacy (data isolation)
✅ Accuracy (RAG-based context)
✅ Customization (business-specific prompts)
