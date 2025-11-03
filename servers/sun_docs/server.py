"""
Sun Docs MCP Server Implementation
Provides documentation search and retrieval tools
"""
from typing import Dict, List, Any
import logging
from core.base_server import BaseMCPServer
from .tools import search_docs, list_all_docs, get_doc_by_name, get_docs_by_category

logger = logging.getLogger('SunDocsServer')


class SunDocsServer(BaseMCPServer):
    """MCP Server for Sun documentation links"""
    
    def __init__(self):
        super().__init__(name="SunDocs", version="1.0.0")
        self.logger.info("Sun Docs Server initialized")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return [
            {
                "name": "search_docs",
                "description": "Search documentation by keyword in name or description. Use this when user asks: 'tìm tài liệu về server', 'search docs about billing', 'có tài liệu nào về security không?'",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search keyword (searches in document name and description)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_all_docs",
                "description": "List all available documentation links. Use when user asks: 'show all docs', 'danh sách tài liệu', 'có những tài liệu gì?'",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_doc_by_name",
                "description": "Get a specific document by exact name. Use when user asks for specific document: 'show me Sun SV doc', 'tài liệu IP List'",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Document name (case insensitive)"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_docs_by_category",
                "description": "Get documents by category keyword. Use for category searches: 'server documents', 'security docs', 'billing information'",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category keyword (e.g., 'server', 'security', 'billing', 'IP', 'meeting')"
                        }
                    },
                    "required": ["category"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        self.logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        if tool_name == "search_docs":
            result = search_docs(**arguments)
        elif tool_name == "list_all_docs":
            result = list_all_docs()
        elif tool_name == "get_doc_by_name":
            result = get_doc_by_name(**arguments)
        elif tool_name == "get_docs_by_category":
            result = get_docs_by_category(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return result
