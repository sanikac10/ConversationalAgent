from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RAG_System.complete_rag_system import ProductionRAGSystem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize RAG system
try:
    rag_system = ProductionRAGSystem()
    logger.info("RAG System initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG system: {e}")
    rag_system = None

@app.route('/api/retrieve', methods=['POST'])
def retrieve_context():
    """Retrieve context for a given query"""
    try:
        if not rag_system:
            return jsonify({'error': 'RAG system not initialized'}), 500
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        query = data.get('query', '')
        conversation_history = data.get('conversation_history', [])
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Retrieve context
        retrieved_docs = rag_system.retrieve_context(
            query, 
            conversation_history=conversation_history, 
            top_k=top_k
        )
        
        # Format response
        response = {
            'query': query,
            'context': rag_system.format_context_for_llm(retrieved_docs),
            'sources': rag_system.get_sources(retrieved_docs),
            'retrieved_documents': [
                {
                    'content': doc.content,
                    'source': doc.source,
                    'relevance_score': doc.relevance_score,
                    'metadata': doc.metadata
                } for doc in retrieved_docs
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in retrieve endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_knowledge', methods=['POST'])
def add_knowledge():
    """Add new knowledge to the system"""
    try:
        if not rag_system:
            return jsonify({'error': 'RAG system not initialized'}), 500
            
        data = request.get_json()
        documents = data.get('documents', [])
        
        if not documents:
            return jsonify({'error': 'Documents are required'}), 400
        
        contents = [doc['content'] for doc in documents]
        sources = [doc['source'] for doc in documents]
        metadata = [doc.get('metadata', {}) for doc in documents]
        
        rag_system.vector_store.add_documents(contents, sources, metadata)
        
        return jsonify({
            'message': f'Successfully added {len(documents)} documents',
            'total_documents': len(rag_system.vector_store.documents)
        })
    
    except Exception as e:
        logger.error(f"Error in add_knowledge endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation', methods=['POST'])
def handle_conversation():
    """Handle a complete conversation turn with RAG"""
    try:
        if not rag_system:
            return jsonify({'error': 'RAG system not initialized'}), 500
            
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Retrieve context
        retrieved_docs = rag_system.retrieve_context(
            user_message, 
            conversation_history=conversation_history, 
            top_k=5
        )
        
        # Generate response context
        response = {
            'user_message': user_message,
            'retrieved_context': rag_system.format_context_for_llm(retrieved_docs),
            'sources': rag_system.get_sources(retrieved_docs),
            'ready_for_llm': True,
            'context_quality': len(retrieved_docs),
            'retrieved_documents': [
                {
                    'content': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
                    'source': doc.source,
                    'relevance_score': doc.relevance_score
                } for doc in retrieved_docs
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in conversation endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        documents_count = len(rag_system.vector_store.documents) if rag_system else 0
        return jsonify({
            'status': 'healthy',
            'documents_count': documents_count,
            'system': 'RAG System v1.0',
            'endpoints': [
                'POST /api/retrieve - Retrieve context for queries',
                'POST /api/add_knowledge - Add new documents',
                'POST /api/conversation - Handle conversation with RAG',
                'GET /api/health - Health check'
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        if not rag_system:
            return jsonify({'error': 'RAG system not initialized'}), 500
            
        return jsonify({
            'total_documents': len(rag_system.vector_store.documents),
            'embedding_dimension': rag_system.vector_store.dimension,
            'conversation_history_length': len(rag_system.conversation_memory.conversations),
            'system_status': 'operational'
        })
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting RAG API Server...")
    print("Available endpoints:")
    print("- POST /api/retrieve - Retrieve context for queries")
    print("- POST /api/add_knowledge - Add new documents")
    print("- POST /api/conversation - Handle conversation with RAG")
    print("- GET /api/health - Health check")
    print("- GET /api/stats - System statistics")
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)