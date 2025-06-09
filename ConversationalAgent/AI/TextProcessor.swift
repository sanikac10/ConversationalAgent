//
//  TextProcessor.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import Foundation
import NaturalLanguage

class TextProcessor {
    private let maxTokens = 512
    
    func processInput(userMessage: String, context: String) -> String {
        // Combine user message with context
        let fullInput = """
        <context>
        $context)
        </context>
        
        <user_message>
        $userMessage)
        </user_message>
        
        <assistant_response>
        """
        
        // Truncate if necessary
        return truncateToTokenLimit(fullInput)
    }
    
    private func truncateToTokenLimit(_ text: String) -> String {
        let tokenizer = NLTokenizer(unit: .word)
        tokenizer.string = text
        
        var tokenCount = 0
        var truncatedEndIndex = text.endIndex
        
        tokenizer.enumerateTokens(in: text.startIndex..<text.endIndex) { tokenRange, _ in
            tokenCount += 1
            if tokenCount > maxTokens {
                truncatedEndIndex = tokenRange.lowerBound
                return false
            }
            return true
        }
        
        return String(text[..<truncatedEndIndex])
    }
}
