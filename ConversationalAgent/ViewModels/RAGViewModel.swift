//
//  RAGViewModel.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation
import Combine

class RAGViewModel: ObservableObject {
    @Published var retrievedDocuments: [RAGDocument] = []
    @Published var isRetrieving = false
    
    private let ragService: RAGService
    private let embeddingService: EmbeddingService
    
    init() {
        self.ragService = RAGService()
        self.embeddingService = EmbeddingService()
    }
    
    func performRetrieval(query: String) async {
        isRetrieving = true
        
        // Generate query embedding
        let queryEmbedding = await embeddingService.generateEmbedding(for: query)
        
        // Retrieve relevant documents
        let documents = await ragService.retrieveDocuments(queryEmbedding: queryEmbedding, topK: 5)
        
        await MainActor.run {
            self.retrievedDocuments = documents
            self.isRetrieving = false
        }
    }
}
