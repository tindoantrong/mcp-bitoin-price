"""
Base class for MCP HTTP Servers
Provides common functionality for all MCP servers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger('BaseMCPServer')


class BaseMCPServer(ABC):
    """Abstract base class for MCP servers"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize MCP server
        
        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f'MCP.{name}')
        
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools
        
        Returns:
            List of tool definitions following MCP protocol
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        pass
    
    def get_server_info(self) -> Dict[str, str]:
        """
        Get server information
        
        Returns:
            Dict with name and version
        """
        return {
            "name": self.name,
            "version": self.version
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get server capabilities
        
        Returns:
            Dict with server capabilities
        """
        return {
            "tools": {}
        }
    
    def format_tool_response(self, result: Any) -> Dict[str, Any]:
        """
        Format tool execution result for MCP protocol
        
        Args:
            result: Raw tool result
            
        Returns:
            Formatted response following MCP protocol
        """
        import json
        
        result_text = json.dumps(result, ensure_ascii=False, indent=2)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result_text
                }
            ]
        }
