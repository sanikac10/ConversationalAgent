//
//  LoadingView.swift
//  ConversationalAgent
//
//  Created by Sanika Chavan on 07/03/25.
//

import SwiftUI

struct LoadingView: View {
    @State private var dots = 0
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { index in
                Circle()
                    .fill(Color.gray)
                    .frame(width: 8, height: 8)
                    .scaleEffect(dots == index ? 1.2 : 0.8)
                    .animation(.easeInOut(duration: 0.6).repeatForever().delay(Double(index) * 0.2), value: dots)
            }
        }
        .onAppear {
            dots = 0
            withAnimation {
                dots = 2
            }
        }
        .padding()
    }
}
