//
//  AIService.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation
import CoreML

struct AIResponse {
    let content: String
    let sources: [String]
}

class AIService {
    private let modelInference: ModelInference
    private let textProcessor: TextProcessor
    
    init() {
        self.modelInference = ModelInference()
        self.textProcessor = TextProcessor()
    }
    
    func generateResponse(userMessage: String, conversationHistory: [Message], retrievedContext: [RAGDocument]) async -> AIResponse {
        // Prepare context
        let contextString = prepareContext(conversationHistory: conversationHistory, retrievedContext: retrievedContext)
        
        // Process input
        let processedInput = textProcessor.processInput(
            userMessage: userMessage,
            context: contextString
        )
        
        // Generate response using the model
        let generatedText = await modelInference.generate(input: processedInput)
        
        // Extract sources
        let sources = retrievedContext.map { \$0.source }
        
        return AIResponse(content: generatedText, sources: sources)
    }
    
    private func prepareContext(conversationHistory: [Message], retrievedContext: [RAGDocument]) -> String {
        var context = "Conversation History:\n"
        
        // Add recent conversation history
        let recentMessages = conversationHistory.suffix(5)
        for message in recentMessages {
            let role = message.isUser ? "User" : "Assistant"
            context += "$role): $message.content)\n"
        }
        
        // Add retrieved context
        if !retrievedContext.isEmpty {
            context += "\nRelevant Information:\n"
            for (index, doc) in retrievedContext.enumerated() {
                context += "[$index + 1)] $doc.content)\n"
            }
        }
        
        return context
    }
}
