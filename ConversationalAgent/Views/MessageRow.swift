//
//  MessageRow.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import SwiftUI

struct MessageRow: View {
    let message: Message
    @State private var showContext = false
    
    var body: some View {
        VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
            HStack {
                if message.isUser {
                    Spacer(minLength: 60)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(message.content)
                        .padding(12)
                        .background(message.isUser ? Color.blue : Color(.systemGray5))
                        .foregroundColor(message.isUser ? .white : .primary)
                        .cornerRadius(16)
                    
                    if let context = message.retrievedContext, !context.isEmpty {
                        Button(action: { showContext.toggle() }) {
                            Label("Sources ($context.count))", systemImage: "doc.text")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        if showContext {
                            VStack(alignment: .leading, spacing: 4) {
                                ForEach(Array(context.enumerated()), id: \.offset) { index, source in
                                    Text("[$index + 1)] $source)")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                        .padding(8)
                                        .background(Color(.systemGray6))
                                        .cornerRadius(8)
                                }
                            }
                            .transition(.opacity)
                        }
                    }
                }
                
                if !message.isUser {
                    Spacer(minLength: 60)
                }
            }
            
            Text(message.timestamp, style: .time)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .animation(.easeInOut, value: showContext)
    }
}
