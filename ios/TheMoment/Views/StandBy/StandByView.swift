import SwiftUI

/// 横屏 StandBy 模式 — 充电时钟 + 氛围
struct StandByView: View {
    @State private var currentTime = Date()
    @State private var currentDate = Date()

    let palette: ColorPalette?

    private let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        GeometryReader { geometry in
            let isLandscape = geometry.size.width > geometry.size.height

            ZStack {
                // 背景色
                (palette.map { Color(hex: $0.background) } ?? Color.black)
                    .ignoresSafeArea()

                if isLandscape {
                    landscapeLayout
                } else {
                    portraitLayout
                }
            }
            .onReceive(timer) { _ in
                currentTime = Date()
                currentDate = Date()
            }
        }
    }

    // MARK: - 横屏布局（主模式）
    private var landscapeLayout: some View {
        HStack(spacing: 60) {
            // 左侧：时间
            VStack(alignment: .leading, spacing: 4) {
                Text(timeString)
                    .font(.system(size: 72, weight: .thin, design: .monospaced))
                    .foregroundColor(palette.map { Color(hex: $0.text) } ?? .white)

                Text(dateString)
                    .font(.system(size: 18, weight: .regular))
                    .foregroundColor((palette.map { Color(hex: $0.text) } ?? .white).opacity(0.5))
            }

            Spacer()

            // 右侧：今日一句
            VStack(alignment: .trailing, spacing: 8) {
                Text("此刻")
                    .font(.system(size: 28, weight: .medium, design: .serif))
                    .foregroundColor(palette.map { Color(hex: $0.primary) } ?? .white.opacity(0.6))

                Text("静下来\n感受这一秒")
                    .font(.system(size: 15))
                    .foregroundColor((palette.map { Color(hex: $0.text) } ?? .white).opacity(0.4))
                    .multilineTextAlignment(.trailing)
            }
        }
        .padding(60)
        .background(
            // 微妙玻璃效果
            Circle()
                .fill(palette.map { Color(hex: $0.accent).opacity(0.08) } ?? .white.opacity(0.03))
                .blur(radius: 80)
                .offset(x: -100, y: -50)
        )
    }

    // MARK: - 竖屏布局（fallback）
    private var portraitLayout: some View {
        VStack(spacing: 20) {
            Spacer()

            Text(timeString)
                .font(.system(size: 56, weight: .thin, design: .monospaced))
                .foregroundColor(palette.map { Color(hex: $0.text) } ?? .white)

            Text(dateString)
                .font(.system(size: 16))
                .foregroundColor((palette.map { Color(hex: $0.text) } ?? .white).opacity(0.4))

            Spacer()
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Formatters

    private var timeString: String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        return f.string(from: currentTime)
    }

    private var dateString: String {
        let f = DateFormatter()
        f.locale = Locale(identifier: "zh_CN")
        f.dateFormat = "M月d日 EEEE"
        return f.string(from: currentDate)
    }
}
