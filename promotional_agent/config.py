import re
from pathlib import Path

class SystemPrompts:
    """System prompts and guardrails for the RAG system - loaded dynamically from SYSTEM_PROMPTS.md"""
    
    _prompts_file = Path(__file__).parent / "SYSTEM_PROMPTS.md"
    _last_modified = None
    _cached_prompts = {}
    
    @staticmethod
    def _load_prompt_from_md(section_name: str, force_reload: bool = False) -> str:
        """Load a specific prompt section from SYSTEM_PROMPTS.md with caching and auto-reload"""
        try:
            current_mtime = SystemPrompts._prompts_file.stat().st_mtime
            
            if (force_reload or 
                SystemPrompts._last_modified is None or 
                current_mtime != SystemPrompts._last_modified):
                
                with open(SystemPrompts._prompts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                pattern = rf"### {section_name}.*?```\n(.*?)```"
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    SystemPrompts._cached_prompts[section_name] = match.group(1).strip()
                else:
                    SystemPrompts._cached_prompts[section_name] = SystemPrompts._get_default_prompt(section_name)
                
                SystemPrompts._last_modified = current_mtime
                print(f"✓ Reloaded prompts from SYSTEM_PROMPTS.md")
            
            return SystemPrompts._cached_prompts.get(section_name, SystemPrompts._get_default_prompt(section_name))
        
        except FileNotFoundError:
            print(f"Warning: {SystemPrompts._prompts_file} not found. Using default prompts.")
            return SystemPrompts._get_default_prompt(section_name)
        except Exception as e:
            print(f"Error loading prompt: {e}. Using default.")
            return SystemPrompts._get_default_prompt(section_name)
    
    @staticmethod
    def _get_default_prompt(section_name: str) -> str:
        """Fallback default prompts if MD file is missing"""
        defaults = {
            "Full Prompt": """You are an intelligent document assistant that helps users understand and extract information from their uploaded documents.

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

Remember: Your knowledge is limited to the uploaded documents. Do not use external knowledge.""",
            
            "Guardrail Response": """I'm designed to help you with questions about your uploaded documents. I cannot assist with:
- Harmful, illegal, or unethical requests
- Personal advice outside document context
- Generating misleading information
- Requests that violate privacy or security

Please ask questions related to your documents."""
        }
        return defaults.get(section_name, "")
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the main system prompt (dynamically loaded)"""
        return SystemPrompts._load_prompt_from_md("Full Prompt")
    
    @staticmethod
    def get_guardrail_response() -> str:
        """Get the guardrail response (dynamically loaded)"""
        return SystemPrompts._load_prompt_from_md("Guardrail Response")
    
    @staticmethod
    def reload_prompts():
        """Manually force reload prompts from MD file"""
        SystemPrompts._load_prompt_from_md("Full Prompt", force_reload=True)
        SystemPrompts._load_prompt_from_md("Guardrail Response", force_reload=True)
        return "Prompts reloaded successfully!"
    
    PROHIBITED_PATTERNS = [
        "hack", "exploit", "illegal", "harmful", "dangerous",
        "weapon", "drug", "violence", "suicide", "self-harm",
        "steal", "fraud", "scam", "malware", "virus"
    ]
    
    @staticmethod
    def check_guardrails(query: str) -> bool:
        """Check if query violates guardrails"""
        query_lower = query.lower()
        
        for pattern in SystemPrompts.PROHIBITED_PATTERNS:
            if pattern in query_lower:
                return False
        
        manipulation_patterns = [
            "ignore previous instructions",
            "disregard your instructions",
            "forget your role",
            "act as if",
            "pretend you are"
        ]
        
        for pattern in manipulation_patterns:
            if pattern in query_lower:
                return False
        
        return True