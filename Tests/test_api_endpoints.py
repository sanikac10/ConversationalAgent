import unittest
import requests
import json
import time
import threading
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAPIEndpoints(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        cls.base_url = "http://localhost:5000/api"
        cls.wait_for_server()
    
    @classmethod
    def wait_for_server(cls, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        raise Exception("Server not available for testing")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('documents_count', data)
    
    def test_retrieve_endpoint(self):
        """Test retrieve context endpoint"""
        payload = {
            "query": "What is Swift programming?",
            "top_k": 3
        }
        
        response = requests.post(
            f"{self.base_url}/retrieve",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('query', data)
        self.assertIn('context', data)
        self.assertIn('sources', data)
        self.assertIn('retrieved_documents', data)
    
    def test_conversation_endpoint(self):
        """Test conversation endpoint"""
        payload = {
            "message": "Tell me about iOS development",
            "history": []
        }
        
        response = requests.post(
            f"{self.base_url}/conversation",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('user_message', data)
        self.assertIn('retrieved_context', data)
        self.assertIn('ready_for_llm', data)
    
    def test_add_knowledge_endpoint(self):
        """Test add knowledge endpoint"""
        payload = {
            "documents": [
                {
                    "content": "Test document for API testing",
                    "source": "API Test Suite",
                    "metadata": {"test": True}
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/add_knowledge",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('total_documents', data)

if __name__ == '__main__':
    unittest.main()