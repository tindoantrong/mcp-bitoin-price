"""
Server Registry
Manages multiple MCP servers and routes requests
"""
from typing import Dict, Optional, List, Any
import logging
from core.base_server import BaseMCPServer

logger = logging.getLogger('ServerRegistry')


class ServerRegistry:
    """Registry for managing multiple MCP servers"""
    
    def __init__(self):
        """Initialize server registry"""
        self._servers: Dict[str, BaseMCPServer] = {}
        self.logger = logger
    
    def register(self, server: BaseMCPServer) -> None:
        """
        Register a new server
        
        Args:
            server: Server instance to register
        """
        if server.name in self._servers:
            self.logger.warning(f"Server '{server.name}' already registered, replacing...")
        
        self._servers[server.name] = server
        self.logger.info(f"Registered server: {server.name} v{server.version}")
    
    def unregister(self, server_name: str) -> None:
        """
        Unregister a server
        
        Args:
            server_name: Name of server to unregister
        """
        if server_name in self._servers:
            del self._servers[server_name]
            self.logger.info(f"Unregistered server: {server_name}")
        else:
            self.logger.warning(f"Server '{server_name}' not found")
    
    def get_server(self, server_name: str) -> Optional[BaseMCPServer]:
        """
        Get a server by name
        
        Args:
            server_name: Name of server to retrieve
            
        Returns:
            Server instance or None if not found
        """
        return self._servers.get(server_name)
    
    def list_servers(self) -> List[Dict[str, str]]:
        """
        List all registered servers
        
        Returns:
            List of server info dictionaries
        """
        return [
            {
                "name": server.name,
                "version": server.version
            }
            for server in self._servers.values()
        ]
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools from all registered servers
        
        Returns:
            List of all tools with server prefix
        """
        all_tools = []
        
        for server_name, server in self._servers.items():
            tools = server.get_tools()
            
            # Add server prefix to tool names for namespacing
            for tool in tools:
                prefixed_tool = tool.copy()
                # Store original tool name and server name for routing
                prefixed_tool['_server'] = server_name
                prefixed_tool['_original_name'] = tool['name']
                # Optional: prefix tool name with server name
                # prefixed_tool['name'] = f"{server_name}_{tool['name']}"
                all_tools.append(prefixed_tool)
        
        return all_tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Call a tool on the appropriate server
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            server_name: Optional server name to route to. If not provided, 
                        will search all servers for the tool.
        
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool or server not found
        """
        if server_name:
            # Direct routing to specific server
            server = self.get_server(server_name)
            if not server:
                raise ValueError(f"Server '{server_name}' not found")
            
            return await server.call_tool(tool_name, arguments)
        
        # Search all servers for the tool
        for server in self._servers.values():
            tools = server.get_tools()
            tool_names = [t['name'] for t in tools]
            
            if tool_name in tool_names:
                return await server.call_tool(tool_name, arguments)
        
        raise ValueError(f"Tool '{tool_name}' not found in any registered server")
    
    def get_combined_server_info(self) -> Dict[str, Any]:
        """
        Get combined server information for all registered servers
        
        Returns:
            Dictionary with combined server information
        """
        servers = self.list_servers()
        
        return {
            "name": "MultiServer",
            "version": "1.0.0",
            "servers": servers,
            "count": len(servers)
        }
