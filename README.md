# Conversational Agent with RAG - iOS App

A sophisticated multi-turn conversational AI agent built with SwiftUI that leverages the Retrieval-Augmented Generation (RAG) for enhanced responses.

## Features

- **SwiftUI Native Interface**: Modern, responsive chat interface
- **RAG Integration**: Real-time knowledge retrieval and context enhancement
- **Local Memory**: Persistent conversation history and context management
- **Web Knowledge Retrieval**: Dynamic information fetching from multiple sources
- **Vector Search**: Semantic similarity matching for relevant context
- **Multi-turn Conversations**: Maintains context across conversation turns

## Architecture

- **iOS App**: SwiftUI frontend with MVVM architecture
- **RAG System**: Production-ready retrieval system with vector storage
- **API Layer**: RESTful API connecting iOS to RAG backend
- **Knowledge Base**: Persistent document storage with embedding indexing

## Quick Start

1. **Setup Environment**:
   ```bash
   ./setup_environment.sh
Start RAG API Server:

./Scripts/run_api_server.sh
Open iOS App:

Open iOS_App/ConversationalAgent.xcodeproj in Xcode
Update server URL in Services/AIService.swift
Build and run on simulator or device
Test the System:

python Scripts/demo_script.py
Status
✅ iOS SwiftUI Application - Complete
✅ RAG System - Production Ready
✅ API Integration - Functional
⏳ Fine-tuned Model - Training on ASU Sol Supercomputer
The system is fully functional with intelligent context retrieval. The fine-tuned Llama 3 model will enhance response quality once training completes.

Documentation
Setup Guide 
API Documentation 
iOS Integration 
Demo Instructions 
