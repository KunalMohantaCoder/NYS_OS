"""
Main personal assistant that coordinates all components.
"""
from typing import Dict, Any, Optional
from .task_parser import TaskParser, IntentType
from .file_manager import FileManager
from .system_commands import SystemCommandExecutor
from .scheduler import Scheduler


class PersonalAssistant:
    """
    Main personal assistant that handles user requests.
    """
    
    def __init__(self, base_path: Optional[str] = None, data_dir: str = "data/assistant"):
        """
        Initialize personal assistant.
        
        Args:
            base_path: Base directory for file operations
            data_dir: Directory for assistant data
        """
        self.task_parser = TaskParser()
        self.file_manager = FileManager(base_path)
        self.command_executor = SystemCommandExecutor()
        self.scheduler = Scheduler(data_dir)
    
    def process_request(self, user_input: str, inference_engine=None) -> Dict[str, Any]:
        """
        Process user request and execute appropriate action.
        
        Args:
            user_input: User's input text
            inference_engine: Optional inference engine for chat responses
        
        Returns:
            Dictionary with response information
        """
        # Parse intent
        intent, parameters = self.task_parser.parse(user_input)
        
        response = {
            'intent': intent.value,
            'success': False,
            'message': '',
            'data': None
        }
        
        # Handle different intents
        if intent == IntentType.FILE_CREATE:
            filename = parameters.get('filename', 'untitled.txt')
            success, message = self.file_manager.create_file(filename)
            response['success'] = success
            response['message'] = message
        
        elif intent == IntentType.FILE_READ:
            filename = parameters.get('filename')
            if filename:
                success, message, content = self.file_manager.read_file(filename)
                response['success'] = success
                response['message'] = message
                response['data'] = content
            else:
                response['message'] = "Please specify a filename to read"
        
        elif intent == IntentType.FILE_DELETE:
            filename = parameters.get('filename')
            if filename:
                success, message = self.file_manager.delete_file(filename)
                response['success'] = success
                response['message'] = message
            else:
                response['message'] = "Please specify a filename to delete"
        
        elif intent == IntentType.FILE_LIST:
            directory = parameters.get('directory', '.')
            success, message, files = self.file_manager.list_files(directory)
            response['success'] = success
            response['message'] = message
            response['data'] = files
        
        elif intent == IntentType.FILE_SEARCH:
            query = parameters.get('query')
            if query:
                success, message, matches = self.file_manager.search_files(query)
                response['success'] = success
                response['message'] = message
                response['data'] = matches
            else:
                response['message'] = "Please specify a search query"
        
        elif intent == IntentType.FOLDER_CREATE:
            foldername = parameters.get('foldername')
            if foldername:
                success, message = self.file_manager.create_folder(foldername)
                response['success'] = success
                response['message'] = message
            else:
                response['message'] = "Please specify a folder name"
        
        elif intent == IntentType.SCHEDULE:
            description = parameters.get('description', 'Event')
            time_str = parameters.get('time')
            success, message = self.scheduler.add_event(description, time_str)
            response['success'] = success
            response['message'] = message
        
        elif intent == IntentType.SYSTEM_COMMAND:
            command = parameters.get('command')
            if command:
                success, message, output = self.command_executor.execute(command)
                response['success'] = success
                response['message'] = message
                response['data'] = output
            else:
                response['message'] = "Please specify a command to execute"
        
        elif intent == IntentType.QUESTION or intent == IntentType.CHAT:
            # Use inference engine for chat/question responses
            if inference_engine:
                try:
                    ai_response = inference_engine.chat(user_input)
                    response['success'] = True
                    response['message'] = ai_response
                except Exception as e:
                    response['message'] = f"Error generating response: {str(e)}"
            else:
                response['message'] = "I'm here to help! What would you like to know?"
        
        else:
            response['message'] = "I didn't understand that. Can you rephrase?"
        
        return response

