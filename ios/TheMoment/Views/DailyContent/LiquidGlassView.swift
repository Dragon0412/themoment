import SwiftUI

/// Liquid Glass 叠加层 — 内容之上的毛玻璃效果
struct LiquidGlassOverlay: View {
    let palette: ColorPalette
    let glassParams: GlassParams?

    var body: some View {
        ZStack {
            // 底层：模糊 + 饱和度的毛玻璃
            Rectangle()
                .fill(.ultraThinMaterial)
                .saturation(saturationValue)

            // 中层：色板染色
            Rectangle()
                .fill(tintColor)
                .blendMode(.overlay)
                .opacity(0.3)

            // 顶层：微妙的渐变光晕
            Rectangle()
                .fill(
                    LinearGradient(
                        colors: [
                            Color(hex: palette.primary).opacity(0.15),
                            Color(hex: palette.accent).opacity(0.05),
                            .clear
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
        }
        .ignoresSafeArea()
    }

    private var saturationValue: Double {
        glassParams?.saturation ?? 1.1
    }

    private var tintColor: Color {
        if let tint = glassParams?.tint {
            return Color(hex: tint)
        }
        return Color(hex: palette.primary)
    }
}
