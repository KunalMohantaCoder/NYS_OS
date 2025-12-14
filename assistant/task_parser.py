"""
Intent parsing and task recognition.
"""
import re
from typing import Dict, Optional, Tuple, List
from enum import Enum


class IntentType(Enum):
    """Types of user intents."""
    FILE_CREATE = "file_create"
    FILE_READ = "file_read"
    FILE_DELETE = "file_delete"
    FILE_LIST = "file_list"
    FILE_SEARCH = "file_search"
    FOLDER_CREATE = "folder_create"
    SCHEDULE = "schedule"
    SYSTEM_COMMAND = "system_command"
    QUESTION = "question"
    CHAT = "chat"
    UNKNOWN = "unknown"


class TaskParser:
    """
    Parses user input to identify intents and extract parameters.
    """
    
    def __init__(self):
        # Intent patterns
        self.patterns = {
            IntentType.FILE_CREATE: [
                r'create\s+(?:a\s+)?file\s+(?:called|named)?\s+([^\s]+)',
                r'create\s+([^\s]+\.\w+)',
                r'make\s+(?:a\s+)?file\s+(?:called|named)?\s+([^\s]+)',
            ],
            IntentType.FILE_READ: [
                r'read\s+(?:the\s+)?file\s+([^\s]+)',
                r'open\s+(?:the\s+)?file\s+([^\s]+)',
                r'show\s+(?:me\s+)?(?:the\s+)?(?:contents\s+of\s+)?([^\s]+)',
            ],
            IntentType.FILE_DELETE: [
                r'delete\s+(?:the\s+)?file\s+([^\s]+)',
                r'remove\s+(?:the\s+)?file\s+([^\s]+)',
                r'rm\s+([^\s]+)',
            ],
            IntentType.FILE_LIST: [
                r'list\s+(?:files|files\s+in\s+(?:this\s+)?(?:directory|folder))',
                r'show\s+(?:me\s+)?(?:the\s+)?files',
                r'what\s+files\s+(?:are\s+)?(?:in\s+(?:this\s+)?(?:directory|folder))?',
            ],
            IntentType.FILE_SEARCH: [
                r'search\s+for\s+([^\s]+)',
                r'find\s+(?:file\s+)?([^\s]+)',
            ],
            IntentType.FOLDER_CREATE: [
                r'create\s+(?:a\s+)?(?:new\s+)?(?:folder|directory)\s+(?:called|named)?\s+([^\s]+)',
                r'make\s+(?:a\s+)?(?:new\s+)?(?:folder|directory)\s+(?:called|named)?\s+([^\s]+)',
                r'mkdir\s+([^\s]+)',
            ],
            IntentType.SCHEDULE: [
                r'schedule\s+(?:a\s+)?(?:meeting|event|appointment)',
                r'add\s+(?:a\s+)?(?:meeting|event|appointment)',
                r'remind\s+me\s+(?:to|about)',
            ],
            IntentType.SYSTEM_COMMAND: [
                r'run\s+command\s+(.+)',
                r'execute\s+(.+)',
                r'system\s+(.+)',
            ],
        }
    
    def parse(self, text: str) -> Tuple[IntentType, Dict[str, any]]:
        """
        Parse user input to identify intent and extract parameters.
        
        Args:
            text: User input text
        
        Returns:
            Tuple of (intent_type, parameters_dict)
        """
        text = text.lower().strip()
        parameters = {'original_text': text}
        
        # Check each intent pattern
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if intent_type == IntentType.FILE_CREATE:
                        parameters['filename'] = match.group(1)
                    elif intent_type == IntentType.FILE_READ:
                        parameters['filename'] = match.group(1)
                    elif intent_type == IntentType.FILE_DELETE:
                        parameters['filename'] = match.group(1)
                    elif intent_type == IntentType.FILE_SEARCH:
                        parameters['query'] = match.group(1)
                    elif intent_type == IntentType.FOLDER_CREATE:
                        parameters['foldername'] = match.group(1)
                    elif intent_type == IntentType.SCHEDULE:
                        # Extract time/date if present
                        time_match = re.search(r'(?:at|on)\s+([^\s]+(?:\s+[^\s]+)*)', text)
                        if time_match:
                            parameters['time'] = time_match.group(1)
                        desc_match = re.search(r'(?:meeting|event|appointment)\s+(?:called|named)?\s+([^\s]+)', text)
                        if desc_match:
                            parameters['description'] = desc_match.group(1)
                    elif intent_type == IntentType.SYSTEM_COMMAND:
                        parameters['command'] = match.group(1)
                    
                    return intent_type, parameters
        
        # Check for questions
        if text.endswith('?') or text.startswith(('what', 'when', 'where', 'who', 'why', 'how', 'which')):
            return IntentType.QUESTION, parameters
        
        # Default to chat
        return IntentType.CHAT, parameters

