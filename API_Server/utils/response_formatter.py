from typing import Any, Dict, List, Optional
from datetime import datetime

def format_response(data: Any, status: str = "success", message: str = None) -> Dict[str, Any]:
    """Format API response in standard format"""
    response = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return response

def format_error(error_message: str, error_code: str = None, details: Dict = None) -> Dict[str, Any]:
    """Format error response"""
    response = {
        "status": "error",
        "timestamp": datetime.now().isoformat(),
        "error": {
            "message": error_message
        }
    }
    
    if error_code:
        response["error"]["code"] = error_code
    
    if details:
        response["error"]["details"] = details
    
    return response

def format_rag_response(
    query: str,
    retrieved_docs: List[Dict],
    context: str,
    sources: List[str]
) -> Dict[str, Any]:
    """Format RAG-specific response"""
    return format_response({
        "query": query,
        "context": context,
        "sources": sources,
        "retrieved_documents": retrieved_docs,
        "document_count": len(retrieved_docs)
    })
