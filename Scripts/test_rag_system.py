#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RAG_System.complete_rag_system import ProductionRAGSystem
import time

def test_rag_system():
    """Test the RAG system functionality"""
    
    print("Initializing RAG System...")
    rag = ProductionRAGSystem()
    
    print(f"✅ RAG System initialized with {len(rag.vector_store.documents)} documents")
    
    # Test queries
    test_queries = [
        "What is Swift programming language?",
        "How does SwiftUI work for iOS development?",
        "Explain Retrieval-Augmented Generation",
        "What are iOS app development best practices?",
        "How does machine learning work in mobile apps?"
    ]
    
    print("\n" + "="*60)
    print("TESTING RAG RETRIEVAL")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        start_time = time.time()
        retrieved_docs = rag.retrieve_context(query, top_k=3)
        end_time = time.time()
        
        print(f"⏱️  Retrieval time: {end_time - start_time:.2f} seconds")
        print(f"📄 Retrieved {len(retrieved_docs)} documents")
        
        if retrieved_docs:
            print("\n📋 Retrieved Documents:")
            for j, doc in enumerate(retrieved_docs, 1):
                print(f"   [{j}] Source: {doc.source}")
                print(f"       Score: {doc.relevance_score:.3f}")
                print(f"       Content: {doc.content[:100]}...")
        else:
            print("⚠️  No documents retrieved")
        
        print(f"\n🔗 Sources: {rag.get_sources(retrieved_docs)}")
    
    print("\n" + "="*60)
    print("TESTING CONVERSATION MEMORY")
    print("="*60)
    
    # Test conversation memory
    rag.add_conversation_exchange(
        "What is Swift?",
        "Swift is Apple's programming language for iOS development."
    )
    
    rag.add_conversation_exchange(
        "How do I use it for UI?",
        "You can use SwiftUI framework with Swift for building user interfaces."
    )
    
    # Test context-aware retrieval
    context_query = "Tell me more about the framework"
    print(f"\nContext-aware query: {context_query}")
    retrieved_docs = rag.retrieve_context(
        context_query, 
        conversation_history=[
            {"content": "What is Swift?", "is_user": True},
            {"content": "How do I use it for UI?", "is_user": True}
        ]
    )
    
    print(f"📄 Retrieved {len(retrieved_docs)} contextual documents")
    for doc in retrieved_docs:
        print(f"   - {doc.source}: {doc.content[:80]}...")
    
    print("\n" + "="*60)
    print("✅ RAG SYSTEM TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print(f"\n📊 Final Statistics:")
    print(f"   Total documents in store: {len(rag.vector_store.documents)}")
    print(f"   Conversation exchanges: {len(rag.conversation_memory.conversations)}")
    print(f"   Embedding dimension: {rag.vector_store.dimension}")
    
    return True

if __name__ == "__main__":
    try:
        test_rag_system()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)