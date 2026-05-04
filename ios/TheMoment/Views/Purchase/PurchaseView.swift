import SwiftUI

/// 购买页 — ¥5 买断
struct PurchaseView: View {
    @State private var isPurchasing = false
    @State private var purchaseMessage: String?
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(hex: "#0F2027"), Color(hex: "#203A43"), Color(hex: "#2C5364")],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            VStack(spacing: 28) {
                Spacer()

                // 图标
                Image(systemName: "infinity")
                    .font(.system(size: 48, weight: .thin))
                    .foregroundColor(.white)

                // 文案
                VStack(spacing: 8) {
                    Text("解锁 此刻")
                        .font(.system(size: 28, weight: .medium, design: .serif))
                        .foregroundColor(.white)

                    Text("一次购买，永久拥有\n每日AI生成的视听体验")
                        .font(.system(size: 15))
                        .foregroundColor(.white.opacity(0.5))
                        .multilineTextAlignment(.center)
                }

                Spacer()

                // 价格卡片
                VStack(spacing: 4) {
                    Text("¥5")
                        .font(.system(size: 48, weight: .light, design: .monospaced))
                    Text("永久买断 · 无需订阅")
                        .font(.system(size: 13))
                        .foregroundColor(.secondary)
                }
                .foregroundColor(.white)
                .padding(.vertical, 24)
                .padding(.horizontal, 40)
                .background(.ultraThinMaterial)
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))

                // 购买按钮
                Button(action: {
                    // StoreKit 购买逻辑
                    isPurchasing = true
                    // 模拟购买
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                        isPurchasing = false
                        purchaseMessage = "购买成功！欢迎来到此刻"
                    }
                }) {
                    HStack {
                        if isPurchasing {
                            ProgressView()
                                .tint(.black)
                        }
                        Text(isPurchasing ? "处理中..." : "立即解锁 — ¥5")
                    }
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .frame(height: 52)
                    .background(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                }
                .disabled(isPurchasing)
                .padding(.horizontal, 40)

                // 恢复购买
                Button("恢复购买") {
                    // StoreKit restore
                }
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.4))
                .padding(.top, 8)

                // 状态消息
                if let msg = purchaseMessage {
                    Text(msg)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.green)
                        .padding(.top, 4)
                }

                Spacer()

                // 权益说明
                VStack(spacing: 10) {
                    featureRow(icon: "photo.artframe", text: "每日AI生成视觉作品")
                    featureRow(icon: "music.note", text: "氛围音频 · 后台播放")
                    featureRow(icon: "paintpalette", text: "自适应配色 · Liquid Glass")
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 50)
            }
        }
        .onChange(of: purchaseMessage) { _, msg in
            if msg != nil {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                    dismiss()
                }
            }
        }
    }

    private func featureRow(icon: String, text: String) -> some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 15))
                .foregroundColor(.white.opacity(0.6))
                .frame(width: 24)
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.5))
            Spacer()
        }
    }
}
