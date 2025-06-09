import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RAG_System.complete_rag_system import ProductionRAGSystem, ConversationMemory, EnhancedVectorStore

class TestRAGSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.rag_system = ProductionRAGSystem()
    
    def test_initialization(self):
        """Test RAG system initialization"""
        self.assertIsNotNone(self.rag_system)
        self.assertIsNotNone(self.rag_system.vector_store)
        self.assertIsNotNone(self.rag_system.web_retriever)
        self.assertIsNotNone(self.rag_system.conversation_memory)
    
    def test_document_retrieval(self):
        """Test document retrieval functionality"""
        query = "What is Swift programming?"
        results = self.rag_system.retrieve_context(query, top_k=3)
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)
        
        if results:
            for doc in results:
                self.assertTrue(hasattr(doc, 'content'))
                self.assertTrue(hasattr(doc, 'source'))
                self.assertTrue(hasattr(doc, 'relevance_score'))
    
    def test_conversation_memory(self):
        """Test conversation memory functionality"""
        memory = ConversationMemory()
        
        memory.add_exchange("Hello", "Hi there!")
        memory.add_exchange("How are you?", "I'm doing well!")
        
        self.assertEqual(len(memory.conversations), 2)
        self.assertIn("Hello", memory.get_context())
        self.assertIn("Hi there!", memory.get_context())
    
    def test_context_formatting(self):
        """Test context formatting for LLM"""
        query = "Swift programming"
        docs = self.rag_system.retrieve_context(query, top_k=2)
        context = self.rag_system.format_context_for_llm(docs)
        
        self.assertIsInstance(context, str)
        if docs:
            self.assertIn("[1]", context)
    
    def test_sources_extraction(self):
        """Test source extraction"""
        query = "SwiftUI"
        docs = self.rag_system.retrieve_context(query, top_k=2)
        sources = self.rag_system.get_sources(docs)
        
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), len(docs))

class TestVectorStore(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        import tempfile
        self.temp_db = tempfile.mktemp(suffix='.db')
        self.vector_store = EnhancedVectorStore(db_path=self.temp_db)
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)
    
    def test_add_documents(self):
        """Test adding documents to vector store"""
        contents = ["Test document 1", "Test document 2"]
        sources = ["Test Source 1", "Test Source 2"]
        
        initial_count = len(self.vector_store.documents)
        self.vector_store.add_documents(contents, sources)
        
        self.assertEqual(len(self.vector_store.documents), initial_count + 2)
    
    def test_search_documents(self):
        """Test searching documents"""
        contents = ["Swift is a programming language", "Python is also a programming language"]
        sources = ["Swift Docs", "Python Docs"]
        
        self.vector_store.add_documents(contents, sources)
        results = self.vector_store.search("Swift programming", top_k=1)
        
        self.assertGreater(len(results), 0)
        self.assertIn("Swift", results[0].content)

if __name__ == '__main__':
    unittest.main()