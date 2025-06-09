//
//  RAGService.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation

class RAGService {
    private let networkService: NetworkService
    private let embeddingService: EmbeddingService
    private var documentCache: [RAGDocument] = []
    
    init() {
        self.networkService = NetworkService()
        self.embeddingService = EmbeddingService()
    }
    
    func retrieveRelevantDocuments(for query: String, conversationContext: String) async -> [RAGDocument] {
        // Generate query embedding
        let queryEmbedding = await embeddingService.generateEmbedding(for: query)
        
        // Retrieve from internet (simulated with a search API)
        let searchResults = await networkService.searchDocuments(query: query)
        
        // Generate embeddings for retrieved documents
        var documents: [RAGDocument] = []
        for result in searchResults {
            let embedding = await embeddingService.generateEmbedding(for: result.content)
            let relevanceScore = calculateSimilarity(queryEmbedding: queryEmbedding, docEmbedding: embedding)
            
            let document = RAGDocument(
                content: result.content,
                embedding: embedding,
                source: result.source,
                relevanceScore: relevanceScore
            )
            documents.append(document)
        }
        
        // Sort by relevance and return top K
        let sortedDocuments = documents.sorted { \$0.relevanceScore > \$1.relevanceScore }
        let topDocuments = Array(sortedDocuments.prefix(3))
        
        // Cache documents
        documentCache.append(contentsOf: topDocuments)
        
        return topDocuments
    }
    
    func retrieveDocuments(queryEmbedding: [Float], topK: Int) async -> [RAGDocument] {
        // Calculate similarities with cached documents
        let scoredDocuments = documentCache.map { doc in
            var mutableDoc = doc
            mutableDoc.relevanceScore = calculateSimilarity(
                queryEmbedding: queryEmbedding,
                docEmbedding: doc.embedding
            )
            return mutableDoc
        }
        
        // Sort and return top K
        let sortedDocuments = scoredDocuments.sorted { \$0.relevanceScore > \$1.relevanceScore }
        return Array(sortedDocuments.prefix(topK))
    }
    
    private func calculateSimilarity(queryEmbedding: [Float], docEmbedding: [Float]) -> Float {
        guard queryEmbedding.count == docEmbedding.count else { return 0.0 }
        
        // Cosine similarity
        var dotProduct: Float = 0.0
        var queryMagnitude: Float = 0.0
        var docMagnitude: Float = 0.0
        
        for i in 0..<queryEmbedding.count {
            dotProduct += queryEmbedding[i] * docEmbedding[i]
            queryMagnitude += queryEmbedding[i] * queryEmbedding[i]
            docMagnitude += docEmbedding[i] * docEmbedding[i]
        }
        
        queryMagnitude = sqrt(queryMagnitude)
        docMagnitude = sqrt(docMagnitude)
        
        guard queryMagnitude > 0 && docMagnitude > 0 else { return 0.0 }
        
        return dotProduct / (queryMagnitude * docMagnitude)
    }
}
