# 🚀 Quick Start Guide - Hackathon AI Framework

**Time to Deploy:** 15-30 minutes  
**Last Updated:** November 2024

---

## 📦 What You Have

This framework consists of **4 files** that work together:

1. **HACKATHON_FRAMEWORK.md** - Master documentation (read this first!)
2. **web_app.py** - User interface (Module 1)
3. **ai_agent.py** - AI engine (Module 2)
4. **use_case_database.py** - Database system (Module 3)

Plus supporting files:
- **SYSTEM_PROMPTS.md** - AI behavior configuration
- **requirements.txt** - Python dependencies
- **.env** - API keys (you create this)

---

## ⚡ Ultra-Fast Setup (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install streamlit openai chromadb python-dotenv PyPDF2 python-docx Pillow PyMuPDF pytesseract
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File
```bash
# Create .env file
echo "OPENAI_API_KEY=your_actual_key_here" > .env
```

### Step 3: Create SYSTEM_PROMPTS.md
```markdown
# System Prompts

### Full Prompt
```
You are a helpful AI assistant.
Answer questions based on provided context.
Be clear, concise, and accurate.
```

### Guardrail Response
```
I can only help with legitimate questions about your documents.
```
```

### Step 4: Launch!
```bash
streamlit run web_app.py
```

Visit: `http://localhost:8501`

---

## 🎯 Hackathon Day Workflow

### Morning (Problem Revealed)

**1. Understand the Use Case (10 min)**
- Read problem statement
- Identify key features needed
- Sketch data model

**2. Choose Database Schema (5 min)**
Edit `use_case_database.py`:
```python
# Change schema_type to match your use case
db = UseCaseDatabase("demo.db", "healthcare")  # or "ecommerce", "education", etc.
```

**3. Customize System Prompts (10 min)**
Edit `SYSTEM_PROMPTS.md`:
```markdown
### Full Prompt
```
You are a [YOUR DOMAIN] assistant.

Your responsibilities:
1. [Key task 1]
2. [Key task 2]
3. [Key task 3]
```
```

**4. Load Demo Data (5 min)**
```python
# In Python console or web app
from use_case_database import UseCaseDatabase

db = UseCaseDatabase("demo.db", "healthcare")
db.setup_schema()
db.load_sample_data()
```

### Afternoon (Build & Test)

**5. Test AI Interactions (30 min)**
- Upload sample documents
- Ask test questions
- Refine prompts based on responses

**6. Customize UI (20 min)**
Edit `web_app.py`:
```python
PAGE_CONFIG = {
    "page_title": "Your App Name",
    "page_icon": "🏥",  # Your emoji
    "use_case_name": "Healthcare Assistant",
    "description": "Your description"
}
```

**7. Prepare Demo Flow (15 min)**
- Write 5 example questions
- Prepare 2-3 documents to upload
- Test complete user journey

---

## 🔧 Common Customizations

### Change AI Model
In `ai_agent.py`:
```python
self.settings = {
    'model': 'gpt-4o-mini',  # or 'gpt-4', 'gpt-3.5-turbo'
    'temperature': 0.3,       # Lower = more focused
    'max_tokens': 1000,       # Response length
}
```

### Add Custom Database Tables
In `use_case_database.py`:
```python
SCHEMA_TEMPLATES["your_usecase"] = """
    CREATE TABLE your_table (
        id INTEGER PRIMARY KEY,
        field1 TEXT NOT NULL,
        field2 INTEGER
    );
"""
```

### Modify Guardrails
In `SYSTEM_PROMPTS.md`:
```markdown
### Prohibited Patterns
- custom_bad_word1
- custom_bad_word2
```

---

## 🎨 Example Use Cases

### Use Case 1: Customer Support Bot

**Database:** CRM schema
```python
db = UseCaseDatabase("support.db", "crm")
```

**System Prompt:**
```markdown
You are a customer support AI.
Answer questions about products, orders, and account issues.
Escalate to humans for refunds or complex technical problems.
```

**Demo Questions:**
- "What's my order status?"
- "How do I reset my password?"
- "I need a refund"

---

### Use Case 2: Medical Triage

**Database:** Healthcare schema
```python
db = UseCaseDatabase("medical.db", "healthcare")
```

**System Prompt:**
```markdown
You are a medical triage assistant.
Assess symptom urgency and recommend care level.
NEVER diagnose or prescribe.
Always disclaimer that this is not medical advice.
```

**Demo Questions:**
- "I have a headache and fever"
- "When should I go to the ER?"
- "Can you prescribe antibiotics?" (should refuse)

---

### Use Case 3: Educational Tutor

**Database:** Education schema
```python
db = UseCaseDatabase("school.db", "education")
```

**System Prompt:**
```markdown
You are an educational tutor.
Help students understand concepts and complete assignments.
Explain step-by-step without giving direct answers.
```

**Demo Questions:**
- "What assignments are due this week?"
- "Explain the Pythagorean theorem"
- "Help me with my calculus homework"

---

## 🐛 Troubleshooting

### "Module not found" Error
```bash
# Install missing package
pip install [package_name]
```

### "OPENAI_API_KEY not found"
```bash
# Check .env file exists
cat .env

# Verify format (no quotes)
OPENAI_API_KEY=sk-...
```

### Database Won't Load
```python
# Reset database
import os
os.remove("use_case.db")

# Recreate
db = UseCaseDatabase()
db.setup_schema()
```

### AI Responses Are Wrong
1. Check system prompt clarity
2. Verify documents uploaded correctly
3. Test with simple queries first
4. Lower temperature for consistency

---

## 📊 Testing Checklist

Before demo:
- [ ] API key working
- [ ] Database populated
- [ ] System prompts customized
- [ ] 5 test queries prepared
- [ ] Upload feature tested
- [ ] Guardrails tested
- [ ] UI customized
- [ ] Demo script written

---

## 🏆 Judge Presentation Tips

### Opening (30 seconds)
"We built an AI-powered [USE CASE] system that [KEY VALUE PROP]. Watch as I..."

### Demo Flow (2 minutes)
1. Upload a document (10 sec)
2. Ask simple question (20 sec)
3. Ask complex question (30 sec)
4. Show database/sources (30 sec)
5. Highlight unique feature (30 sec)

### Closing (30 seconds)
"This framework is modular and can be adapted to any use case in minutes. Questions?"

### Key Points to Emphasize
- **Speed:** "Built in 4 hours"
- **Flexibility:** "Dynamic configuration"
- **Multi-modal:** "Text + images"
- **Production-ready:** "Safety guardrails"

---

## 🔥 Advanced Features (If Time Permits)

### Add Voice Input
```python
# In web_app.py
from streamlit_mic_recorder import mic_recorder

audio = mic_recorder(key='recorder')
if audio:
    # Convert to text using Whisper
    transcription = openai.Audio.transcribe("whisper-1", audio)
    question = transcription.text
```

### Add Charts
```python
# In web_app.py
import plotly.express as px

data = db.query("SELECT category, COUNT(*) as count FROM products GROUP BY category")
fig = px.bar(data, x='category', y='count')
st.plotly_chart(fig)
```

### Real-time Streaming
```python
# In ai_agent.py
response = self.client.chat.completions.create(
    model=self.settings['model'],
    messages=messages,
    stream=True  # Enable streaming
)

for chunk in response:
    if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content
```

---

## 📚 File Structure

```
hackathon-project/
│
├── HACKATHON_FRAMEWORK.md     # Master documentation
├── QUICK_START_GUIDE.md       # This file
├── SYSTEM_PROMPTS.md          # AI behavior config
│
├── web_app.py                 # Module 1: UI
├── ai_agent.py                # Module 2: AI Engine
├── use_case_database.py       # Module 3: Database
│
├── requirements.txt           # Dependencies
├── .env                       # API keys (create this)
│
├── chroma_db/                 # Vector store (auto-created)
├── use_case.db                # SQLite database (auto-created)
│
└── temp/                      # Uploaded files (auto-created)
```

---

## 🎓 Learning Resources

### If You're New to This

**Streamlit (UI):**
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)

**OpenAI (AI):**
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

**SQLite (Database):**
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [SQL for Data Science](https://mode.com/sql-tutorial/)

**RAG (Retrieval):**
- [What is RAG?](https://www.anthropic.com/index/retrieval-augmented-generation)
- [Vector Databases 101](https://www.pinecone.io/learn/vector-database/)

---

## 💡 Pro Tips

1. **Start Simple:** Get basic Q&A working first, add features later
2. **Test Early:** Upload docs and query within first 30 minutes
3. **Have Backups:** Prepare canned responses if API fails
4. **Show, Don't Tell:** Live demo > PowerPoint
5. **Iterate Fast:** System prompts reload instantly, no restart needed
6. **Use Demo Data:** Pre-load realistic data for smooth demos
7. **Practice Pitch:** Rehearse 2-minute demo at least once

---

## 🚨 Emergency Fixes

### API Rate Limit Hit
```python
# Add delay between calls
import time
time.sleep(1)
```

### Database Corrupted
```python
# Quick reset
os.remove("use_case.db")
db = UseCaseDatabase()
db.setup_schema()
db.load_sample_data()
```

### UI Not Updating
```bash
# Force refresh
streamlit run web_app.py --server.runOnSave true
```

### ChromaDB Error
```bash
# Clear vector store
rm -rf chroma_db/
# Restart app
```

---

## 📞 Support During Hackathon

### Quick Reference Commands

```bash
# Check if everything installed
python -c "import streamlit, openai, chromadb; print('All good!')"

# Test API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"

# Launch app
streamlit run web_app.py

# Reset everything
rm -rf chroma_db/ use_case.db temp/
```

### Debug Mode
```python
# In web_app.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🎉 Success Criteria

You've succeeded when you can:
- [ ] Upload a document
- [ ] Ask a question
- [ ] Get a relevant answer
- [ ] Show sources
- [ ] Demo in under 3 minutes
- [ ] Handle judge questions confidently

---

## 🚀 Next Steps After Hackathon

1. **Deploy to Cloud:** Streamlit Cloud, Heroku, or AWS
2. **Add Authentication:** User accounts and permissions
3. **Scale Database:** PostgreSQL or MongoDB
4. **Fine-tune Model:** Custom training on domain data
5. **Mobile App:** React Native or Flutter wrapper
6. **Analytics:** Track usage and improve prompts

---

## 📝 Feedback & Improvements

After the hackathon:
- Document what worked
- Note what was confusing
- Suggest template improvements
- Share your use case!

---

**Remember:** The goal is to solve the problem creatively with AI, not to build the perfect system. Good luck! 🍀

**Questions?** Check the main HACKATHON_FRAMEWORK.md for detailed explanations.

---

*Framework Version: 2.0*  
*Last Updated: November 2024*  
*Ready to win! 🏆*
