//
//  LocalStorageService.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation

class LocalStorageService {
    private let conversationKey = "conversation_state"
    private let documentsKey = "cached_documents"
    
    func saveConversation(_ state: ConversationState) async {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(state)
            UserDefaults.standard.set(data, forKey: conversationKey)
        } catch {
            print("Error saving conversation: $error)")
        }
    }
    
    func loadConversation() async -> ConversationState? {
        guard let data = UserDefaults.standard.data(forKey: conversationKey) else { return nil }
        
        do {
            let decoder = JSONDecoder()
            return try decoder.decode(ConversationState.self, from: data)
        } catch {
            print("Error loading conversation: $error)")
            return nil
        }
    }
    
    func clearConversation() async {
        UserDefaults.standard.removeObject(forKey: conversationKey)
    }
    
    func saveCachedDocuments(_ documents: [RAGDocument]) async {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(documents)
            UserDefaults.standard.set(data, forKey: documentsKey)
        } catch {
            print("Error saving documents: $error)")
        }
    }
    
    func loadCachedDocuments() async -> [RAGDocument]? {
        guard let data = UserDefaults.standard.data(forKey: documentsKey) else { return nil }
        
        do {
            let decoder = JSONDecoder()
            return try decoder.decode([RAGDocument].self, from: data)
        } catch {
            print("Error loading documents: $error)")
            return nil
        }
    }
}
