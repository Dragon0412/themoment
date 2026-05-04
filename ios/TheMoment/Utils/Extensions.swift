import SwiftUI

// MARK: - Hex 颜色扩展
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r, g, b: UInt64
        switch hex.count {
        case 6:
            (r, g, b) = ((int >> 16) & 0xFF, (int >> 8) & 0xFF, int & 0xFF)
        default:
            (r, g, b) = (255, 255, 255)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: 1
        )
    }
}

extension View {
    /// Liquid Glass 毛玻璃效果
    func liquidGlass(
        blur: CGFloat = 25,
        saturation: CGFloat = 1.1,
        tint: Color = .white.opacity(0.05)
    ) -> some View {
        self
            .background(
                .ultraThinMaterial
                    .environment(\.colorScheme, .dark)
            )
            .overlay(
                tint
                    .blendMode(.overlay)
            )
            .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
            .shadow(
                color: .black.opacity(0.15),
                radius: 20,
                x: 0,
                y: 10
            )
    }
}

/// 渐隐遮罩 — 底部文字渐隐
struct FadeMask: View {
    let edge: Edge

    var body: some View {
        LinearGradient(
            gradient: Gradient(colors: [.clear, .black]),
            startPoint: edge == .bottom ? .top : .bottom,
            endPoint: edge == .bottom ? .bottom : .top
        )
    }
}
