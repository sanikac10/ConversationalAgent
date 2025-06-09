//
//  RAGDocument.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation

struct RAGDocument: Identifiable, Codable {
    let id: UUID
    let content: String
    let embedding: [Float]
    let source: String
    let relevanceScore: Float
    let timestamp: Date
    
    init(content: String, embedding: [Float], source: String, relevanceScore: Float = 0.0) {
        self.id = UUID()
        self.content = content
        self.embedding = embedding
        self.source = source
        self.relevanceScore = relevanceScore
        self.timestamp = Date()
    }
}
