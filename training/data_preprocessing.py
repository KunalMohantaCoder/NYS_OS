"""
Data preprocessing utilities for training.
"""
import re
from typing import List, Tuple


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()


def prepare_conversation_data(texts: List[str]) -> List[Tuple[str, str]]:
    """
    Prepare conversation pairs from texts.
    For single texts, create self-conversation pairs.
    
    Args:
        texts: List of texts
    
    Returns:
        List of (input, output) pairs
    """
    pairs = []
    
    for text in texts:
        text = clean_text(text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Create pairs from consecutive sentences
        for i in range(len(sentences) - 1):
            pairs.append((sentences[i], sentences[i + 1]))
        
        # Also create question-answer style pairs
        if len(sentences) >= 2:
            pairs.append((sentences[0], ' '.join(sentences[1:])))
    
    return pairs


def create_assistant_training_data() -> List[Tuple[str, str]]:
    """
    Create synthetic training data for assistant commands.
    
    Returns:
        List of (command, response) pairs
    """
    pairs = [
        ("create a file called test.txt", "I'll create the file test.txt for you."),
        ("delete the file test.txt", "I'll delete the file test.txt."),
        ("read the file test.txt", "I'll read the contents of test.txt."),
        ("list files in this directory", "I'll list the files in the current directory."),
        ("schedule a meeting tomorrow at 3pm", "I'll schedule a meeting for tomorrow at 3pm."),
        ("what time is it", "Let me check the current time for you."),
        ("what files are in this folder", "I'll list the files in this folder."),
        ("create a new folder called documents", "I'll create a new folder named documents."),
        ("help me with my tasks", "I can help you manage your tasks. What would you like to do?"),
        ("what can you do", "I can help you with file management, scheduling, answering questions, and more."),
    ]
    
    # Add variations
    variations = []
    for cmd, resp in pairs:
        variations.append((cmd, resp))
        variations.append((cmd.upper(), resp))
        variations.append((cmd.capitalize(), resp))
        variations.append((f"please {cmd}", f"Of course. {resp}"))
        variations.append((f"can you {cmd}", resp))
    
    return variations

