//
//  ConversationState.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation

struct ConversationState: Codable {
    var messages: [Message]
    var context: String
    var sessionId: UUID
    var lastUpdated: Date
    
    init() {
        self.messages = []
        self.context = ""
        self.sessionId = UUID()
        self.lastUpdated = Date()
    }
}
