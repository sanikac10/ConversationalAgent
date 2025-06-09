from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages conversation memory and context"""
    def __init__(self, max_history: int = 20, context_window: int = 4000):
        self.max_history = max_history
        self.context_window = context_window
        self.conversation_history = []
        self.important_facts = []
        self.user_preferences = {}
    
    def add_exchange(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """Add a conversation exchange"""
        exchange = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(exchange)
        
        # Maintain history limit
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # Extract important facts
        self._extract_important_facts(user_message, assistant_response)
    
    def get_context(self, recent_turns: int = 5) -> str:
        """Get formatted conversation context"""
        recent_history = self.conversation_history[-recent_turns:]
        
        context_parts = []
        for exchange in recent_history:
            context_parts.append(f"User: {exchange['user_message']}")
            context_parts.append(f"Assistant: {exchange['assistant_response']}")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > self.context_window:
            context = context[-self.context_window:]
        
        return context
    
    def _extract_important_facts(self, user_message: str, assistant_response: str):
        """Extract and store important facts from conversation"""
        # Simple fact extraction based on keywords
        keywords = ["name is", "I am", "I work", "I like", "my favorite"]
        
        for keyword in keywords:
            if keyword in user_message.lower():
                fact = {
                    "fact": user_message,
                    "timestamp": datetime.now().isoformat(),
                    "context": "user_statement"
                }
                self.important_facts.append(fact)
                break
    
    def get_user_context(self) -> str:
        """Get relevant user context and preferences"""
        if not self.important_facts:
            return ""
        
        recent_facts = [f["fact"] for f in self.important_facts[-5:]]
        return "User context: " + "; ".join(recent_facts)
    
    def save_memory(self, filepath: str):
        """Save memory to file"""
        memory_data = {
            "conversation_history": self.conversation_history,
            "important_facts": self.important_facts,
            "user_preferences": self.user_preferences
        }
        
        with open(filepath, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    def load_memory(self, filepath: str):
        """Load memory from file"""
        try:
            with open(filepath, 'r') as f:
                memory_data = json.load(f)
            
            self.conversation_history = memory_data.get("conversation_history", [])
            self.important_facts = memory_data.get("important_facts", [])
            self.user_preferences = memory_data.get("user_preferences", {})
            
            logger.info(f"Loaded memory with {len(self.conversation_history)} exchanges")
        except FileNotFoundError:
            logger.info("No existing memory file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading memory: {e}")