import numpy as np
import faiss
import sqlite3
import requests
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import json
import hashlib
from datetime import datetime
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import re
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Document:
    id: str
    content: str
    source: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    timestamp: datetime
    relevance_score: float = 0.0

class ConversationMemory:
    """Manages conversation history and context"""
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations = []
        self.context_summary = ""
    
    def add_exchange(self, user_message: str, assistant_response: str):
        """Add a conversation exchange"""
        exchange = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now()
        }
        self.conversations.append(exchange)
        
        # Maintain history limit
        if len(self.conversations) > self.max_history:
            self.conversations = self.conversations[-self.max_history:]
        
        # Update context summary
        self._update_context_summary()
    
    def _update_context_summary(self):
        """Create a summary of recent conversation context"""
        recent_context = ""
        for exchange in self.conversations[-5:]:  # Last 5 exchanges
            recent_context += f"User: {exchange['user']}\nAssistant: {exchange['assistant']}\n"
        self.context_summary = recent_context
    
    def get_context(self) -> str:
        """Get conversation context for RAG retrieval"""
        return self.context_summary

class EnhancedVectorStore:
    """Production-ready vector store with persistence"""
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", db_path: str = "Database/data/rag_store.db"):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents = {}
        
        # Initialize SQLite for metadata persistence
        self._init_database()
        self._load_from_database()
    
    def _init_database(self):
        """Initialize SQLite database for document persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def _load_from_database(self):
        """Load existing documents from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents')
        rows = cursor.fetchall()
        
        embeddings = []
        for row in rows:
            doc_id, content, source, embedding_blob, metadata_json, timestamp = row
            
            # Deserialize embedding
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            embeddings.append(embedding)
            
            # Create document object
            metadata = json.loads(metadata_json)
            doc = Document(
                id=doc_id,
                content=content,
                source=source,
                embedding=embedding,
                metadata=metadata,
                timestamp=datetime.fromisoformat(timestamp)
            )
            self.documents[doc_id] = doc
        
        # Rebuild FAISS index
        if embeddings:
            embeddings_array = np.vstack(embeddings)
            self.index.add(embeddings_array.astype('float32'))
        
        conn.close()
        logger.info(f"Loaded {len(self.documents)} documents from database")
    
    def add_documents(self, contents: List[str], sources: List[str], metadata_list: List[Dict] = None):
        """Add documents to the vector store"""
        if metadata_list is None:
            metadata_list = [{}] * len(contents)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(contents, normalize_embeddings=True)
        
        # Add to FAISS
        self.index.add(embeddings.astype('float32'))
        
        # Store documents
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for content, source, embedding, metadata in zip(contents, sources, embeddings, metadata_list):
            doc_id = hashlib.md5(f"{content}{source}".encode()).hexdigest()
            timestamp = datetime.now()
            
            doc = Document(
                id=doc_id,
                content=content,
                source=source,
                embedding=embedding,
                metadata=metadata,
                timestamp=timestamp
            )
            
            self.documents[doc_id] = doc
            
            # Save to database
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (id, content, source, embedding, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                content,
                source,
                embedding.tobytes(),
                json.dumps(metadata),
                timestamp.isoformat()
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Added {len(contents)} documents to vector store")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.3) -> List[Document]:
        """Search for similar documents"""
        if len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)
        
        # Search in FAISS
        scores, indices = self.index.search(query_embedding.astype('float32'), 
                                          min(top_k, len(self.documents)))
        
        results = []
        doc_list = list(self.documents.values())
        
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(doc_list) and score >= threshold:
                doc = doc_list[idx]
                # Create a copy to avoid modifying the original
                result_doc = Document(
                    id=doc.id,
                    content=doc.content,
                    source=doc.source,
                    embedding=doc.embedding,
                    metadata=doc.metadata,
                    timestamp=doc.timestamp,
                    relevance_score=float(score)
                )
                results.append(result_doc)
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)

class WebKnowledgeRetriever:
    """Retrieves information from web sources"""
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAGBot/1.0)'
        })
    
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Search Wikipedia for information"""
        try:
            # Wikipedia API search
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            
            # Clean query for Wikipedia
            clean_query = re.sub(r'[^\w\s]', '', query).replace(' ', '_')
            
            response = self.session.get(f"{search_url}{clean_query}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data and data['extract']:
                    return [{
                        'content': data['extract'],
                        'source': f"Wikipedia: {data.get('title', query)}",
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    }]
            
            # Fallback: search for articles
            search_api = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': max_results
            }
            
            response = self.session.get(search_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('query', {}).get('search', []):
                    title = item['title']
                    snippet = item['snippet']
                    # Clean HTML tags
                    snippet = re.sub(r'<[^>]+>', '', snippet)
                    
                    if snippet.strip():  # Only add if snippet has content
                        results.append({
                            'content': snippet,
                            'source': f"Wikipedia: {title}",
                            'url': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                        })
                
                return results[:max_results]
                
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
        
        return []
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search web using multiple sources"""
        results = []
        
        # Search Wikipedia
        wiki_results = self.search_wikipedia(query, max_results=min(max_results, 3))
        results.extend(wiki_results)
        
        # Add more sources here if needed (DuckDuckGo, etc.)
        
        return results[:max_results]

class ProductionRAGSystem:
    """Complete RAG system for production use"""
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.vector_store = EnhancedVectorStore(embedding_model)
        self.web_retriever = WebKnowledgeRetriever()
        self.conversation_memory = ConversationMemory()
        self.knowledge_cache = {}
        
        # Initialize with some base knowledge
        self._initialize_base_knowledge()
    
    def _initialize_base_knowledge(self):
        """Initialize with basic knowledge about common topics"""
        base_knowledge = [
            {
                "content": "Swift is a powerful and intuitive programming language for iOS, iPadOS, macOS, tvOS, and watchOS development. It was developed by Apple and first released in 2014. Swift combines the performance and efficiency of compiled languages with the simplicity and interactivity of popular scripting languages.",
                "source": "Apple Developer Documentation"
            },
            {
                "content": "SwiftUI is Apple's modern declarative framework for building user interfaces across all Apple platforms. It uses a declarative syntax that's easy to read and natural to write. SwiftUI provides tools to declare user interfaces for any Apple device.",
                "source": "Apple SwiftUI Documentation"
            },
            {
                "content": "Retrieval-Augmented Generation (RAG) is an AI framework that combines parametric and non-parametric memory to generate more accurate and up-to-date responses. It retrieves relevant documents from a knowledge base and uses them to enhance the generation process.",
                "source": "AI Research Papers"
            },
            {
                "content": "iOS app development involves creating applications for Apple's mobile operating system using Xcode, Swift programming language, and various frameworks like UIKit and SwiftUI. Best practices include following Apple's Human Interface Guidelines and ensuring proper memory management.",
                "source": "iOS Development Guide"
            },
            {
                "content": "Machine learning in mobile apps can provide personalized experiences, intelligent recommendations, and advanced features like image recognition and natural language processing. Core ML is Apple's framework for integrating machine learning models into iOS apps.",
                "source": "Apple Core ML Documentation"
            }
        ]
        
        # Check if documents already exist
        if len(self.vector_store.documents) == 0:
            contents = [item["content"] for item in base_knowledge]
            sources = [item["source"] for item in base_knowledge]
            
            self.vector_store.add_documents(contents, sources)
            logger.info("Initialized base knowledge")
    
    def retrieve_context(self, query: str, conversation_history: List[Dict] = None, top_k: int = 5) -> List[Document]:
        """Retrieve relevant context for a query"""
        # 1. Get conversation context
        context_query = query
        if conversation_history:
            # Add recent conversation context to query
            recent_context = " ".join([
                f"{msg.get('content', '')}" 
                for msg in conversation_history[-3:] 
                if msg.get('content')
            ])
            context_query = f"{recent_context} {query}"
        
        # 2. Search local vector store
        local_results = self.vector_store.search(context_query, top_k=top_k)
        
        # 3. Search web if not enough local results or low relevance
        all_results = local_results.copy()
        
        if len(local_results) < top_k//2 or (local_results and max(r.relevance_score for r in local_results) < 0.6):
            web_results = self.web_retriever.search_web(query, max_results=top_k//2 + 1)
            
            # Convert web results to Document objects
            for web_result in web_results:
                embedding = self.vector_store.embedding_model.encode(
                    [web_result['content']], 
                    normalize_embeddings=True
                )[0]
                
                doc = Document(
                    id=hashlib.md5(web_result['content'].encode()).hexdigest(),
                    content=web_result['content'],
                    source=web_result['source'],
                    embedding=embedding,
                    metadata={'url': web_result.get('url', ''), 'type': 'web'},
                    timestamp=datetime.now(),
                    relevance_score=0.7  # Default score for web results
                )
                all_results.append(doc)
            
            # Add new web knowledge to vector store for future use
            if web_results:
                contents = [r['content'] for r in web_results]
                sources = [r['source'] for r in web_results]
                metadata = [{'url': r.get('url', ''), 'type': 'web'} for r in web_results]
                self.vector_store.add_documents(contents, sources, metadata)
        
        # 4. Sort by relevance and return top_k
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_results[:top_k]
    
    def add_conversation_exchange(self, user_message: str, assistant_response: str):
        """Add a conversation exchange to memory"""
        self.conversation_memory.add_exchange(user_message, assistant_response)
    
    def format_context_for_llm(self, retrieved_docs: List[Document]) -> str:
        """Format retrieved context for LLM consumption"""
        if not retrieved_docs:
            return "No additional context available."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"[{i}] {doc.content}\nSource: {doc.source}")
        
        return "\n\n".join(context_parts)
    
    def get_sources(self, retrieved_docs: List[Document]) -> List[str]:
        """Extract source information"""
        return [doc.source for doc in retrieved_docs]

# Example usage and testing
def test_rag_system():
    """Test the RAG system"""
    rag = ProductionRAGSystem()
    
    # Test queries
    test_queries = [
        "What is Swift programming language?",
        "How does SwiftUI work?",
        "Explain RAG in AI",
        "iOS app development best practices",
        "Machine learning in mobile apps"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        retrieved_docs = rag.retrieve_context(query, top_k=3)
        
        print("Retrieved Context:")
        context = rag.format_context_for_llm(retrieved_docs)
        print(context)
        
        print("Sources:", rag.get_sources(retrieved_docs))
        print("-" * 80)

if __name__ == "__main__":
    test_rag_system()
