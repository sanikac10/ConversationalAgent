//
//  Constants.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation

struct Constants {
    static let maxMessageLength = 1000
    static let maxConversationHistory = 50
    static let ragTopK = 5
    static let embeddingCacheSize = 100
    
    struct API {
        static let searchAPIKey = "YOUR_SEARCH_API_KEY"
        static let searchEng
