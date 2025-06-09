//
//  ChatViewModel.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation
import Combine
import SwiftUI

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var conversationState: ConversationState
    
    private let aiService: AIService
    private let ragService: RAGService
    private let storageService: LocalStorageService
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        self.conversationState = ConversationState()
        self.aiService = AIService()
        self.ragService = RAGService()
        self.storageService = LocalStorageService()
        
        loadConversationHistory()
    }
    
    func sendMessage(_ content: String) async {
        // Add user message
        let userMessage = Message(content: content, isUser: true)
        messages.append(userMessage)
        conversationState.messages.append(userMessage)
        
        // Perform RAG retrieval
        let retrievedDocuments = await ragService.retrieveRelevantDocuments(for: content, conversationContext: conversationState.context)
        
        // Generate AI response
        let response = await aiService.generateResponse(
            userMessage: content,
            conversationHistory: messages,
            retrievedContext: retrievedDocuments
        )
        
        // Add AI message
        let aiMessage = Message(
            content: response.content,
            isUser: false,
            retrievedContext: response.sources
        )
        messages.append(aiMessage)
        conversationState.messages.append(aiMessage)
        
        // Update conversation state
        conversationState.context = updateContext(with: content, response: response.content)
        conversationState.lastUpdated = Date()
        
        // Save to local storage
        await storageService.saveConversation(conversationState)
    }
    
    func clearConversation() {
        messages.removeAll()
        conversationState = ConversationState()
        Task {
            await storageService.clearConversation()
        }
    }
    
    private func loadConversationHistory() {
        Task {
            if let savedState = await storageService.loadConversation() {
                self.conversationState = savedState
                self.messages = savedState.messages
            }
        }
    }
    
    private func updateContext(with userMessage: String, response: String) -> String {
        let contextWindow = 2000 // characters
        let newContext = "$conversationState.context)\nUser: $userMessage)\nAssistant: $response)"
        
        if newContext.count > contextWindow {
            return String(newContext.suffix(contextWindow))
        }
        return newContext
    }
}
