"""
Sun Docs Tools Module
Provides functions to search and retrieve documentation links
"""
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger('SunDocs.Tools')

# Path to the JSON file
DOCS_FILE = Path(__file__).parent.parent.parent / "SUN-LINKS.json"


def load_docs() -> List[Dict[str, str]]:
    """Load documentation links from JSON file"""
    try:
        with open(DOCS_FILE, 'r', encoding='utf-8') as f:
            docs = json.load(f)
            logger.info(f"Loaded {len(docs)} documentation links")
            return docs
    except Exception as e:
        logger.error(f"Error loading docs: {e}")
        return []


def search_docs(query: str) -> Dict[str, Any]:
    """
    Search documentation links by keyword
    
    Args:
        query: Search keyword (searches in name and description)
    
    Returns:
        Dictionary containing:
        - success: True if search completed
        - results: List of matching documents
        - count: Number of results found
        - query: The search query used
    """
    try:
        docs = load_docs()
        
        if not docs:
            return {
                'success': False,
                'error': 'No documentation available',
                'message': 'Failed to load documentation file'
            }
        
        # Search in name and description (case insensitive)
        query_lower = query.lower()
        results = [
            doc for doc in docs
            if query_lower in doc.get('name', '').lower() or 
               query_lower in doc.get('description', '').lower()
        ]
        
        logger.info(f"Search '{query}' found {len(results)} results")
        
        return {
            'success': True,
            'query': query,
            'count': len(results),
            'results': results,
            'message': f'Found {len(results)} document(s) matching "{query}"'
        }
        
    except Exception as e:
        error_msg = f"Search error: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'message': 'An error occurred during search'
        }


def list_all_docs() -> Dict[str, Any]:
    """
    List all available documentation links
    
    Returns:
        Dictionary containing:
        - success: True if successful
        - docs: List of all documents
        - count: Total number of documents
    """
    try:
        docs = load_docs()
        
        if not docs:
            return {
                'success': False,
                'error': 'No documentation available',
                'message': 'Failed to load documentation file'
            }
        
        logger.info(f"Retrieved {len(docs)} documents")
        
        return {
            'success': True,
            'count': len(docs),
            'docs': docs,
            'message': f'Retrieved {len(docs)} document(s)'
        }
        
    except Exception as e:
        error_msg = f"Error listing docs: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'message': 'An error occurred while retrieving documents'
        }


def get_doc_by_name(name: str) -> Dict[str, Any]:
    """
    Get a specific document by exact name
    
    Args:
        name: Document name (case insensitive)
    
    Returns:
        Dictionary containing:
        - success: True if found
        - doc: The document information
    """
    try:
        docs = load_docs()
        
        if not docs:
            return {
                'success': False,
                'error': 'No documentation available',
                'message': 'Failed to load documentation file'
            }
        
        # Find document by name (case insensitive)
        name_lower = name.lower()
        doc = next(
            (d for d in docs if d.get('name', '').lower() == name_lower),
            None
        )
        
        if doc:
            logger.info(f"Found document: {doc['name']}")
            return {
                'success': True,
                'doc': doc,
                'message': f'Found document: {doc["name"]}'
            }
        else:
            return {
                'success': False,
                'error': 'Document not found',
                'message': f'No document found with name "{name}"'
            }
        
    except Exception as e:
        error_msg = f"Error getting document: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'message': 'An error occurred while retrieving the document'
        }


def get_docs_by_category(category: str) -> Dict[str, Any]:
    """
    Get documents by category keyword
    
    Args:
        category: Category keyword (e.g., 'server', 'security', 'billing')
    
    Returns:
        Dictionary containing matching documents
    """
    try:
        docs = load_docs()
        
        if not docs:
            return {
                'success': False,
                'error': 'No documentation available',
                'message': 'Failed to load documentation file'
            }
        
        # Search by category keyword
        category_lower = category.lower()
        results = [
            doc for doc in docs
            if category_lower in doc.get('name', '').lower() or
               category_lower in doc.get('description', '').lower()
        ]
        
        logger.info(f"Category '{category}' found {len(results)} results")
        
        return {
            'success': True,
            'category': category,
            'count': len(results),
            'results': results,
            'message': f'Found {len(results)} document(s) in category "{category}"'
        }
        
    except Exception as e:
        error_msg = f"Error getting category: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'message': 'An error occurred while retrieving category'
        }
