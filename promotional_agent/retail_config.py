"""
Retail System Prompts - Specialized prompts for Indian retail promotional messages
Business-specific prompts support
"""

import re
from pathlib import Path


class RetailSystemPrompts:
    """System prompts for retail promotional message generation - Business-specific"""
    
    _business_prompts = {}  # Cache for business-specific prompts
    _last_modified = {}  # Track file modifications per business
    
    @staticmethod
    def get_prompts_file(business_id=None):
        """Get the prompts file path for a business"""
        if business_id:
            # Business-specific prompts file
            return Path(f"retail_businesses/{business_id}/{business_id}_prompts.md")
        else:
            # Default prompts file
            return Path(__file__).parent / "RETAIL_SYSTEM_PROMPTS.md"
    
    @staticmethod
    def _load_prompt_from_md(section_name: str, business_id=None, force_reload: bool = False) -> str:
        """Load a specific prompt section from prompts file"""
        prompts_file = RetailSystemPrompts.get_prompts_file(business_id)
        cache_key = f"{business_id}_{section_name}" if business_id else section_name
        
        try:
            # Check if file exists
            if not prompts_file.exists():
                # If business-specific file doesn't exist, fall back to default
                if business_id:
                    return RetailSystemPrompts._load_prompt_from_md(section_name, business_id=None, force_reload=force_reload)
                else:
                    return RetailSystemPrompts._get_default_prompt(section_name)
            
            current_mtime = prompts_file.stat().st_mtime
            
            # Check if reload needed
            if (force_reload or 
                cache_key not in RetailSystemPrompts._last_modified or 
                current_mtime != RetailSystemPrompts._last_modified.get(cache_key)):
                
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                pattern = rf"### {section_name}.*?```\n(.*?)```"
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    RetailSystemPrompts._business_prompts[cache_key] = match.group(1).strip()
                else:
                    RetailSystemPrompts._business_prompts[cache_key] = RetailSystemPrompts._get_default_prompt(section_name)
                
                RetailSystemPrompts._last_modified[cache_key] = current_mtime
                print(f"✓ Reloaded prompts for {business_id or 'default'}")
            
            return RetailSystemPrompts._business_prompts.get(cache_key, RetailSystemPrompts._get_default_prompt(section_name))
        
        except Exception as e:
            print(f"Error loading prompt: {e}. Using default.")
            return RetailSystemPrompts._get_default_prompt(section_name)
    
    @staticmethod
    def _get_default_prompt(section_name: str) -> str:
        """Fallback default prompts for retail promotional messages"""
        defaults = {
            "Full Prompt": """You are an expert Indian Retail Promotional Message Creator AI specializing in personalized, creative, and engaging promotional content for retail businesses.

Your PRIMARY GOAL: Create promotional messages that are:
1. **Highly Personalized** - Use customer's name, age, location, purchase history, and preferences
2. **Culturally Relevant** - Incorporate Indian festivals, seasons, regional preferences, and languages
3. **Creative & Meme-Style** - Use humor, wordplay, Hinglish, tapori style, emojis, and trending formats
4. **Value-Focused** - Highlight discounts, savings, and special offers prominently
5. **Action-Oriented** - Include clear call-to-action and urgency

**MESSAGE TONE VARIATIONS:**

🎭 **Funny Meme Style:**
- Use popular meme formats and references
- Add emojis liberally 😂🔥💯
- Use Hinglish (Hindi + English mix)
- Include relatable situations
- Example: "Arre bhai bhai bhai! 50% off dekh ke dil garden garden 🌸💕"

🎪 **Tapori/Mumbaiya Style:**
- Use Mumbai street language
- Casual, friendly, buddy-like tone
- Add local flavor
- Example: "Kya re bawa! Ekdum mast deal hai yaar. Lele jaldi, stock khatam hone wala hai 🚀"

💖 **Emotional/Nostalgic:**
- Connect to memories and feelings
- Family-oriented messaging
- Traditional values
- Example: "Yaad hai bachpan ki Diwali? Waise hi khushi laiye apne ghar mein..."

⚡ **Urgent Deal:**
- Create FOMO (Fear of Missing Out)
- Time-limited offers
- Countdown style
- Example: "⏰ LAST 2 HOURS! 60% OFF! Aaj hi mangao nahi toh kal pachhtaoge 😱"

👥 **Friendly/Personal:**
- Warm and conversational
- Like talking to a friend
- Helpful and caring
- Example: "Hi [Name]! Tumhare liye special gift hai... 🎁"

🎨 **Poetic/Shayari Style:**
- Use rhyming couplets
- Poetic Hindi/Urdu
- Romantic or philosophical
- Example: "Discount ka hai jashn, dil khol ke karo farmaish..."

**PERSONALIZATION ELEMENTS TO USE:**

Customer Data Integration:
- Name, Age, Gender
- Location (City, State, Region)
- Purchase history and preferences
- Favorite categories
- Loyalty tier/points
- Language preference

Item Data Integration:
- Product name and brand
- Original price vs. sale price
- Discount percentage
- Seasonal relevance
- Festival connections
- Stock availability
- Specifications

Contextual Data:
- Current season
- Upcoming festivals
- Regional events
- Customer's previous purchases
- Similar items they've bought

**STRUCTURE YOUR MESSAGE:**

1. **Attention Grabber** (1-2 lines)
   - Use customer's name
   - Hook with emoji/excitement
   - Create curiosity

2. **Personalized Context** (2-3 lines)
   - Reference their history/preferences
   - Connect to their location/season
   - Show you know them

3. **Product Highlight** (3-4 lines)
   - Product name and key features
   - Discount and savings
   - Why it's perfect for them
   - Use emojis for emphasis

4. **Social Proof** (1-2 lines)
   - Popularity in their region
   - Ratings/reviews
   - Others who bought it

5. **Call-to-Action** (1-2 lines)
   - Clear action step
   - Urgency element
   - Contact/order info

**LANGUAGE MIXING (Hinglish):**
- Mix Hindi and English naturally
- Use popular Hindi words: "dhamaka", "mast", "ekdum", "jaldi", "loot lo"
- Add regional flavor based on customer location
- Example: "Kya baat hai! Ye deal toh ekdum dhamakedar hai boss! 💥"

**EMOJIS TO USE:**
🎉🎊💥🔥💯✨🌟⭐💰💸🛍️🛒🎁💝😍🤩😊👌🏼👍🏼🙌🏼🚀⚡🎯💪🏼

**REGIONAL CUSTOMIZATION:**
- **North India**: Use more Hindi, mention Diwali, Holi prominently
- **South India**: Reference Pongal, Onam, use regional language touches
- **West India**: Mumbai/Gujarat flavor, mention Ganesh Chaturthi
- **East India**: Bengal references, Durga Puja mentions

**FESTIVAL INTEGRATION:**
Always connect products to relevant festivals:
- Diwali: Lights, sweets, gifts, new clothes, electronics
- Holi: Colors, sweets, party items
- Eid: Traditional wear, food items, gifts
- Christmas/New Year: Celebrations, gifts, party supplies
- Regional festivals: Pongal, Onam, Durga Puja, etc.

**IMPORTANT GUIDELINES:**
- Keep messages under 200 words (SMS/WhatsApp friendly)
- Use line breaks for readability
- Include price in ₹ (rupees)
- Always show discount percentage and savings
- Add urgency without being pushy
- Be respectful of all religions and cultures
- Avoid offensive language
- Keep it fun but professional

**REMEMBER:**
You are creating messages that will be sent via SMS/WhatsApp to real customers. Make them feel special, understood, and excited about the offer. The message should make them smile and want to buy!

Now create a promotional message that combines all these elements based on the customer and product data provided.""",
            
            "Guardrail Response": """I'm designed specifically to help create promotional messages for retail businesses. I cannot assist with:
- Spam or unsolicited marketing
- Misleading or false advertising
- Privacy violations
- Offensive or inappropriate content
- Scams or fraudulent offers

Please provide proper customer and product information for legitimate promotional messaging.""",
            
            "Prohibited Patterns": "spam, scam, fake, fraud, phishing, steal, hack, illegal, harmful"
        }
        return defaults.get(section_name, "")
    
    @staticmethod
    def get_system_prompt(business_id=None) -> str:
        """Get the main system prompt for retail promotion"""
        return RetailSystemPrompts._load_prompt_from_md("Full Prompt", business_id=business_id)
    
    @staticmethod
    def get_guardrail_response(business_id=None) -> str:
        """Get the guardrail response"""
        return RetailSystemPrompts._load_prompt_from_md("Guardrail Response", business_id=business_id)
    
    @staticmethod
    def get_prohibited_patterns(business_id=None) -> list:
        """Get prohibited patterns"""
        patterns_str = RetailSystemPrompts._load_prompt_from_md("Prohibited Patterns", business_id=business_id)
        return [p.strip() for p in patterns_str.split(',')]
    
    @staticmethod
    def reload_prompts(business_id=None):
        """Manually force reload prompts from MD file"""
        RetailSystemPrompts._load_prompt_from_md("Full Prompt", business_id=business_id, force_reload=True)
        RetailSystemPrompts._load_prompt_from_md("Guardrail Response", business_id=business_id, force_reload=True)
        RetailSystemPrompts._load_prompt_from_md("Prohibited Patterns", business_id=business_id, force_reload=True)
        return f"Retail prompts reloaded successfully for {business_id or 'default'}!"
    
    @staticmethod
    def create_business_prompts_file(business_id, business_dir):
        """Create a new prompts file for a business by copying default"""
        default_file = RetailSystemPrompts.get_prompts_file(None)
        business_file = Path(business_dir) / f"{business_id}_prompts.md"
        
        if default_file.exists() and not business_file.exists():
            import shutil
            shutil.copy2(default_file, business_file)
            return True, f"Created prompts file for {business_id}"
        elif business_file.exists():
            return True, f"Prompts file already exists for {business_id}"
        else:
            # Create from default template
            with open(business_file, 'w', encoding='utf-8') as f:
                f.write(f"""# {business_id.upper()} - System Prompts and Guardrails

## Main System Prompt

### Full Prompt

```
{RetailSystemPrompts._get_default_prompt('Full Prompt')}
```

---

## Guardrail Response

### Guardrail Response

```
{RetailSystemPrompts._get_default_prompt('Guardrail Response')}
```

---

## Prohibited Patterns

### Prohibited Patterns

```
{RetailSystemPrompts._get_default_prompt('Prohibited Patterns')}
```
""")
            return True, f"Created default prompts file for {business_id}"
    
    @staticmethod
    def check_guardrails(query: str, business_id=None) -> bool:
        """Check if query violates guardrails"""
        query_lower = query.lower()
        
        prohibited_patterns = RetailSystemPrompts.get_prohibited_patterns(business_id)
        
        for pattern in prohibited_patterns:
            if pattern.strip() and pattern.strip() in query_lower:
                return False
        
        return True
