"""
File system operations for personal assistant.
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import json


class FileManager:
    """
    Manages file system operations with safety restrictions.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize file manager.
        
        Args:
            base_path: Base directory for file operations (restricts access)
        """
        if base_path:
            self.base_path = Path(base_path).resolve()
        else:
            # Default to user's home directory
            self.base_path = Path.home()
        
        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, path: str) -> Path:
        """
        Validate and resolve path to ensure it's within base_path.
        
        Args:
            path: File or directory path
        
        Returns:
            Resolved Path object
        
        Raises:
            ValueError: If path is outside base_path
        """
        resolved = (self.base_path / path).resolve()
        
        # Ensure path is within base_path
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Path {path} is outside allowed directory")
        
        return resolved
    
    def create_file(self, filename: str, content: str = "") -> Tuple[bool, str]:
        """
        Create a new file.
        
        Args:
            filename: Name of file to create
            content: Initial content (optional)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            file_path = self._validate_path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"Created file: {filename}"
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def read_file(self, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Read file contents.
        
        Args:
            filename: Name of file to read
        
        Returns:
            Tuple of (success, message, content)
        """
        try:
            file_path = self._validate_path(filename)
            
            if not file_path.exists():
                return False, f"File not found: {filename}", None
            
            if not file_path.is_file():
                return False, f"Not a file: {filename}", None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, f"Read file: {filename}", content
        except Exception as e:
            return False, f"Error reading file: {str(e)}", None
    
    def delete_file(self, filename: str) -> Tuple[bool, str]:
        """
        Delete a file.
        
        Args:
            filename: Name of file to delete
        
        Returns:
            Tuple of (success, message)
        """
        try:
            file_path = self._validate_path(filename)
            
            if not file_path.exists():
                return False, f"File not found: {filename}"
            
            if file_path.is_dir():
                return False, f"Cannot delete directory with delete_file: {filename}"
            
            file_path.unlink()
            return True, f"Deleted file: {filename}"
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def list_files(self, directory: str = ".") -> Tuple[bool, str, List[str]]:
        """
        List files in a directory.
        
        Args:
            directory: Directory path (default: current)
        
        Returns:
            Tuple of (success, message, file_list)
        """
        try:
            dir_path = self._validate_path(directory)
            
            if not dir_path.exists():
                return False, f"Directory not found: {directory}", []
            
            if not dir_path.is_dir():
                return False, f"Not a directory: {directory}", []
            
            files = []
            for item in sorted(dir_path.iterdir()):
                if item.is_file():
                    files.append(f"📄 {item.name}")
                elif item.is_dir():
                    files.append(f"📁 {item.name}/")
            
            return True, f"Files in {directory}:", files
        except Exception as e:
            return False, f"Error listing files: {str(e)}", []
    
    def create_folder(self, foldername: str) -> Tuple[bool, str]:
        """
        Create a new folder.
        
        Args:
            foldername: Name of folder to create
        
        Returns:
            Tuple of (success, message)
        """
        try:
            folder_path = self._validate_path(foldername)
            folder_path.mkdir(parents=True, exist_ok=True)
            
            return True, f"Created folder: {foldername}"
        except Exception as e:
            return False, f"Error creating folder: {str(e)}"
    
    def search_files(self, query: str, directory: str = ".") -> Tuple[bool, str, List[str]]:
        """
        Search for files matching query.
        
        Args:
            query: Search query
            directory: Directory to search in
        
        Returns:
            Tuple of (success, message, matching_files)
        """
        try:
            dir_path = self._validate_path(directory)
            
            if not dir_path.exists() or not dir_path.is_dir():
                return False, f"Invalid directory: {directory}", []
            
            matches = []
            query_lower = query.lower()
            
            for item in dir_path.rglob('*'):
                if query_lower in item.name.lower():
                    rel_path = item.relative_to(self.base_path)
                    if item.is_file():
                        matches.append(f"📄 {rel_path}")
                    elif item.is_dir():
                        matches.append(f"📁 {rel_path}/")
            
            return True, f"Found {len(matches)} matches for '{query}':", matches[:20]  # Limit results
        except Exception as e:
            return False, f"Error searching files: {str(e)}", []

