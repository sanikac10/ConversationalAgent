//
//  Embeddings.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation
import NaturalLanguage
import Accelerate

class EmbeddingService {
    private let embeddingDimension = 384 // Small embedding size for mobile
    
    func generateEmbedding(for text: String) async -> [Float] {
        // In production, use a real embedding model
        // For demo, generate pseudo-embeddings based on text features
        
        let tokenizer = NLTokenizer(unit: .word)
        tokenizer.string = text.lowercased()
        
        var embedding = [Float](repeating: 0.0, count: embeddingDimension)
        var wordCount = 0
        
        tokenizer.enumerateTokens(in: text.startIndex..<text.endIndex) { tokenRange, _ in
            let word = String(text[tokenRange])
            let hash = word.hash
            
            // Generate deterministic pseudo-embedding
            for i in 0..<embeddingDimension {
                let value = Float(hash &+ i) / Float(Int.max)
                embedding[i] += value
            }
            wordCount += 1
            return true
        }
        
        // Normalize
        if wordCount > 0 {
            let norm = 1.0 / Float(wordCount)
            vDSP_vsmul(embedding, 1, &norm, &embedding, 1, vDSP_Length(embeddingDimension))
        }
        
        return embedding
    }
}
