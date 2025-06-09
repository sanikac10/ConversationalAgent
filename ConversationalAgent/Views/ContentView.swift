//
//  ContentView.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var chatViewModel: ChatViewModel
    
    var body: some View {
        NavigationView {
            ChatView()
                .navigationTitle("AI Assistant")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button(action: {
                            chatViewModel.clearConversation()
                        }) {
                            Image(systemName: "trash")
                        }
                    }
                }
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}
