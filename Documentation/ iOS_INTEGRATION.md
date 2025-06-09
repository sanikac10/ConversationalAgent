# iOS Integration Guide

## Overview

This guide explains how to integrate the Conversational Agent with RAG system into your iOS application using SwiftUI.

## Architecture

iOS App (SwiftUI) ↔ RAG API Server ↔ RAG System ↔ Vector Store/Web


## Setup Instructions

### 1. Xcode Project Setup

1. **Create New Project:**
   - Select "App" template
   - Choose "SwiftUI" interface
   - Language: Swift

2. **Add Network Permissions:**
   ```xml
   <!-- Info.plist -->
   <key>NSAppTransportSecurity</key>
   <dict>
       <key>NSAllowsArbitraryLoads</key>
       <true/>
   </dict>
2. Project Structure
ConversationalAgent/
├── Models/
│   ├── Message.swift
│   ├── ConversationState.swift
│   └── RAGDocument.swift
├── Views/
│   ├── ContentView.swift
│   ├── ChatView.swift
│   └── MessageRow.swift
├── ViewModels/
│   ├── ChatViewModel.swift
│   └── RAGViewModel.swift
├── Services/
│   ├── AIService.swift
│   ├── RAGService.swift
│   └── LocalStorageService.swift
└── Utils/
    ├── Constants.swift
    └── Extensions.swift
3. API Integration
AIService Configuration
Update the server URL in AIService.swift:

private let ragBaseURL = "http://your-server-ip:5000/api"
Request Format
let payload: [String: Any] = [
    "query": userMessage,
    "conversation_history": conversationHistory,
    "top_k": 5
]
Response Handling
struct RAGResponse: Codable {
    let query: String
    let context: String
    let sources: [String]
    let retrieved_documents: [RetrievedDocument]
}
4. SwiftUI Implementation
Chat Interface
struct ChatView: View {
    @EnvironmentObject var chatViewModel: ChatViewModel
    @State private var inputText = ""
    
    var body: some View {
        VStack {
            ScrollView {
                LazyVStack {
                    ForEach(chatViewModel.messages) { message in
                        MessageRow(message: message)
                    }
                }
            }
            
            HStack {
                TextField("Type message...", text: \$inputText)
                Button("Send") {
                    Task {
                        await chatViewModel.sendMessage(inputText)
                        inputText = ""
                    }
                }
            }
        }
    }
}
Message Model
struct Message: Identifiable, Codable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
    let sources: [String]?
    
    init(content: String, isUser: Bool, sources: [String]? = nil) {
        self.id = UUID()
        self.content = content
        self.isUser = isUser
        self.timestamp = Date()
        self.sources = sources
    }
}
5. Local Storage
Conversation Persistence
class LocalStorageService {
    func saveConversation(_ state: ConversationState) async {
        do {
            let data = try JSONEncoder().encode(state)
            UserDefaults.standard.set(data, forKey: "conversation_state")
        } catch {
            print("Error saving: $error)")
        }
    }
    
    func loadConversation() async -> ConversationState? {
        guard let data = UserDefaults.standard.data(forKey: "conversation_state") else {
            return nil
        }
        
        return try? JSONDecoder().decode(ConversationState.self, from: data)
    }
}
6. Error Handling
Network Errors
enum NetworkError: Error {
    case invalidResponse
    case httpError(Int)
    case decodingError(Error)
    
    var localizedDescription: String {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .httpError(let code):
            return "HTTP error: $code)"
        case .decodingError(let error):
            return "Decoding error: $error.localizedDescription)"
        }
    }
}
Fallback Responses
private func createFallbackResponse(for query: String) -> AIResponse {
    let fallbackContent = """
    I'm having trouble connecting to the knowledge base right now. 
    However, I can still help with basic questions about iOS development and Swift programming.
    """
    
    return AIResponse(
        content: fallbackContent,
        sources: ["Local Fallback"]
    )
}
7. Performance Optimization
Async/Await Usage
func sendMessage(_ content: String) async {
    await MainActor.run {
        // Update UI on main thread
        messages.append(userMessage)
    }
    
    // Network call on background
    let response = await aiService.generateResponse(content)
    
    await MainActor.run {
        // Update UI with response
        messages.append(aiMessage)
    }
}
Memory Management
class ChatViewModel: ObservableObject {
    private func trimConversationHistory() {
        if messages.count > Constants.maxConversationHistory {
            messages = Array(messages.suffix(Constants.maxConversationHistory))
        }
    }
}
8. Testing
Unit Tests
func testMessageCreation() {
    let message = Message(content: "Test", isUser: true)
    XCTAssertEqual(message.content, "Test")
    XCTAssertTrue(message.isUser)
}

func testAIServiceResponse() async {
    let response = await aiService.generateResponse("Test query")
    XCTAssertFalse(response.content.isEmpty)
}
UI Tests
func testChatInterface() throws {
    let app = XCUIApplication()
    app.launch()
    
    let textField = app.textFields["messageInput"]
    textField.tap()
    textField.typeText("Hello")
    
    app.buttons["Send"].tap()
    
    // Verify message appears
    XCTAssertTrue(app.staticTexts["Hello"].exists)
}
9. Deployment
Build Configuration
// Constants.swift
struct Constants {
    #if DEBUG
    static let apiBaseURL = "http://localhost:5000/api"
    #else
    static let apiBaseURL = "https://your-production-server.com/api"
    #endif
}
App Store Considerations
Privacy Policy: Required for network usage
App Transport Security: Configure for production
Background App Refresh: Handle gracefully
Offline Mode: Implement fallback behavior
10. Troubleshooting
Common Issues
Server Connection Failed:

// Check server status
curl http://localhost:5000/api/health
JSON Decoding Errors:

// Enable detailed logging
let decoder = JSONDecoder()
decoder.dateDecodingStrategy = .iso8601
Memory Issues:

// Implement message cleanup
private func cleanupOldMessages() {
    if messages.count > 100 {
        messages = Array(messages.suffix(50))
    }
}
Best Practices
Use @MainActor for UI updates
Handle network errors gracefully
Implement offline fallbacks
Cache frequently used data
Follow Apple's HIG guidelines
Test on multiple device sizes
Optimize for accessibility
Next Steps
Integrate Core ML for on-device inference
Add voice input/output capabilities
Implement push notifications
Add user authentication
Create widget extensions