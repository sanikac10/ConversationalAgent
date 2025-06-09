//
//  ConversationalAgentApp.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//


import SwiftUI

@main
struct ConversationalAgentApp: App {
    @StateObject private var chatViewModel = ChatViewModel()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(chatViewModel)
        }
    }
}