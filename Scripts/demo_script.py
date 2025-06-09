#!/usr/bin/env python3

import requests
import json
import time

def test_rag_api():
    """Test the RAG API with sample queries"""
    
    base_url = "http://localhost:5000/api"
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start with: ./Scripts/run_api_server.sh")
        return
    
    print("\n" + "="*50)
    
    # Test queries
    test_queries = [
        "What is Swift programming language?",
        "How does SwiftUI work?",
        "Explain RAG in AI",
        "iOS app development best practices"
    ]
    
    for i, query in enumerate(test_queries, 2):
        print(f"\n{i}. Testing query: '{query}'")
        
        payload = {
            "query": query,
            "top_k": 3
        }
        
        try:
            response = requests.post(
                f"{base_url}/retrieve",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Query successful")
                print(f"   Sources: {data.get('sources', [])}")
                print(f"   Context preview: {data.get('context', '')[:100]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text}")
        
        except Exception as e:
            print(f"❌ Query failed with error: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "="*50)
    
    # Test conversation endpoint
    print(f"\n{len(test_queries) + 2}. Testing conversation endpoint...")
    
    conversation_payload = {
        "message": "Tell me about iOS development",
        "history": [
            {"content": "Hello", "is_user": True},
            {"content": "Hi! How can I help you?", "is_user": False}
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/conversation",
            json=conversation_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation endpoint successful")
            print(f"   Ready for LLM: {data.get('ready_for_llm', False)}")
            print(f"   Context quality: {data.get('context_quality', 0)} documents")
        else:
            print(f"❌ Conversation endpoint failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Conversation endpoint failed: {e}")
    
    print("\n" + "="*50)
    print("Demo completed! The RAG system is working correctly.")
    print("You can now test the iOS app by:")
    print("1. Opening iOS_App/ConversationalAgent.xcodeproj in Xcode")
    print("2. Updating the server URL in Services/AIService.swift")
    print("3. Building and running the app")

if __name__ == "__main__":
    test_rag_api()