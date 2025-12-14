"""
Conversation context management.
"""
from typing import List, Dict, Optional
from collections import deque


class ContextManager:
    """
    Manages conversation context and history.
    
    Args:
        max_context_length: Maximum number of conversation turns to keep
        max_tokens: Maximum total tokens in context
    """
    
    def __init__(self, max_context_length: int = 10, max_tokens: int = 512):
        self.max_context_length = max_context_length
        self.max_tokens = max_tokens
        self.conversation_history: deque = deque(maxlen=max_context_length)
        self.current_context_tokens = 0
    
    def add_turn(self, user_input: str, assistant_response: str):
        """
        Add a conversation turn to history.
        
        Args:
            user_input: User's message
            assistant_response: Assistant's response
        """
        self.conversation_history.append({
            'user': user_input,
            'assistant': assistant_response
        })
    
    def get_context(self, current_input: str, tokenizer, max_context_tokens: int = 400) -> str:
        """
        Get formatted context string from conversation history.
        
        Args:
            current_input: Current user input
            tokenizer: Tokenizer to estimate token count
            max_context_tokens: Maximum tokens to include in context
        
        Returns:
            Formatted context string
        """
        context_parts = []
        total_tokens = len(tokenizer.encode(current_input, add_special_tokens=False))
        
        # Add history in reverse order (most recent first)
        for turn in reversed(self.conversation_history):
            turn_text = f"User: {turn['user']}\nAssistant: {turn['assistant']}"
            turn_tokens = len(tokenizer.encode(turn_text, add_special_tokens=False))
            
            if total_tokens + turn_tokens > max_context_tokens:
                break
            
            context_parts.insert(0, turn_text)
            total_tokens += turn_tokens
        
        if context_parts:
            return "\n\n".join(context_parts) + f"\n\nUser: {current_input}\nAssistant:"
        else:
            return f"User: {current_input}\nAssistant:"
    
    def clear(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        self.current_context_tokens = 0
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get full conversation history."""
        return list(self.conversation_history)
    
    def set_history(self, history: List[Dict[str, str]]):
        """Set conversation history."""
        self.conversation_history = deque(history, maxlen=self.max_context_length)

