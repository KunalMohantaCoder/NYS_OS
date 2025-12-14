"""
System command execution with safety restrictions.
"""
import subprocess
import os
import platform
from typing import Tuple, List, Optional


class SystemCommandExecutor:
    """
    Executes system commands with safety restrictions.
    """
    
    def __init__(self, allowed_commands: Optional[List[str]] = None):
        """
        Initialize command executor.
        
        Args:
            allowed_commands: List of allowed command prefixes (for security)
        """
        self.allowed_commands = allowed_commands or [
            'ls', 'dir', 'pwd', 'cd', 'echo', 'cat', 'type',
            'date', 'time', 'whoami', 'hostname', 'uname'
        ]
        
        # Dangerous commands to block
        self.blocked_commands = [
            'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd',
            'shutdown', 'reboot', 'rmdir', 'rd', 'rd /s',
            'sudo', 'su', 'chmod', 'chown'
        ]
    
    def is_safe(self, command: str) -> Tuple[bool, str]:
        """
        Check if command is safe to execute.
        
        Args:
            command: Command to check
        
        Returns:
            Tuple of (is_safe, reason)
        """
        command_lower = command.lower().strip()
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if command_lower.startswith(blocked):
                return False, f"Command '{blocked}' is not allowed for safety"
        
        # Check if command starts with allowed prefix
        for allowed in self.allowed_commands:
            if command_lower.startswith(allowed):
                return True, "Command is safe"
        
        # Block commands with dangerous operators
        dangerous_ops = ['&&', '||', ';', '|', '>', '<', '`', '$(']
        for op in dangerous_ops:
            if op in command:
                return False, f"Command contains dangerous operator: {op}"
        
        return False, "Command not in allowed list"
    
    def execute(self, command: str, timeout: int = 5) -> Tuple[bool, str, Optional[str]]:
        """
        Execute a system command safely.
        
        Args:
            command: Command to execute
            timeout: Execution timeout in seconds
        
        Returns:
            Tuple of (success, message, output)
        """
        is_safe, reason = self.is_safe(command)
        
        if not is_safe:
            return False, f"Command blocked: {reason}", None
        
        try:
            # Determine shell based on OS
            shell = platform.system() == 'Windows'
            
            # Execute command
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return True, f"Command executed successfully", output
            else:
                error = result.stderr.strip()
                return False, f"Command failed: {error}", None
        
        except subprocess.TimeoutExpired:
            return False, "Command timed out", None
        except Exception as e:
            return False, f"Error executing command: {str(e)}", None

