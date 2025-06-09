import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WebRetriever:
    """Web retrieval component"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAGBot/1.0)'
        })
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search web for information"""
        try:
            # Using DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            if data.get('Abstract'):
                results.append({
                    'content': data['Abstract'],
                    'source': data.get('AbstractURL', 'DuckDuckGo'),
                    'title': data.get('Heading', query)
                })
            
            for topic in data.get('RelatedTopics', [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'content': topic['Text'],
                        'source': topic.get('FirstURL', 'DuckDuckGo'),
                        'title': topic.get('Text', '')[:100] + '...'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []

class DocumentRetriever:
    """Document retrieval coordinator"""
    def __init__(self, vector_store, web_retriever=None):
        self.vector_store = vector_store
        self.web_retriever = web_retriever or WebRetriever()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents from multiple sources"""
        # Get local results
        local_results = self.vector_store.search(query, top_k=top_k//2)
        
        # Get web results if needed
        if len(local_results) < top_k//2:
            web_results = self.web_retriever.search_web(query, max_results=top_k//2)
            
            # Convert web results to standard format
            for result in web_results:
                local_results.append({
                    "document": result['content'],
                    "metadata": {"source": result['source'], "type": "web"},
                    "score": 0.5  # Default score for web results
                })
        
        return local_results[:top_k]