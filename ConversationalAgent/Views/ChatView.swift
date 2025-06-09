//
//  ChatView.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import SwiftUI
import Combine

struct ChatView: View {
    @EnvironmentObject var chatViewModel: ChatViewModel
    @State private var inputText = ""
    @State private var isLoading = false
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Messages ScrollView
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(chatViewModel.messages) { message in
                            MessageRow(message: message)
                                .id(message.id)
                        }
                        
                        if isLoading {
                            LoadingView()
                                .id("loading")
                        }
                    }
                    .padding()
                }
                .onChange(of: chatViewModel.messages.count) { _ in
                    withAnimation {
                        proxy.scrollTo(chatViewModel.messages.last?.id ?? "loading", anchor: .bottom)
                    }
                }
            }
            
            Divider()
            
            // Input Area
            HStack(spacing: 12) {
                TextField("Type your message...", text: \$inputText, axis: .vertical)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .lineLimit(1...5)
                    .focused(\$isInputFocused)
                    .onSubmit {
                        sendMessage()
                    }
                
                Button(action: sendMessage) {
                    Image(systemName: "paperplane.fill")
                        .foregroundColor(.white)
                        .frame(width: 44, height: 44)
                        .background(Circle().fill(Color.blue))
                }
                .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)
            }
            .padding()
        }
        .background(Color(.systemBackground))
    }
    
    private func sendMessage() {
        let trimmedText = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedText.isEmpty else { return }
        
        Task {
            isLoading = true
            await chatViewModel.sendMessage(trimmedText)
            inputText = ""
            isLoading = false
        }
    }
}
