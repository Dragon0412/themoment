import SwiftUI

/// 每日一境 — 核心体验视图
struct DailyContentView: View {
    @StateObject private var viewModel = DailyContentViewModel()
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // ── 背景图层：异步加载的 AI 视觉图 ──
                if let imageUrl = viewModel.content?.imageUrl,
                   let url = URL(string: imageUrl) {
                    AsyncImage(url: url) { phase in
                        switch phase {
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: geometry.size.width, height: geometry.size.height)
                                .clipped()
                        case .failure:
                            moodGradient
                        case .empty:
                            moodGradient
                        @unknown default:
                            moodGradient
                        }
                    }
                } else {
                    moodGradient
                }

                // ── Liquid Glass 叠加层 ──
                if let content = viewModel.content {
                    LiquidGlassOverlay(
                        palette: content.colorPalette,
                        glassParams: content.glassParams
                    )
                }

                // ── 内容层 ──
                VStack(spacing: 0) {
                    Spacer()

                    // 标题 + 情绪标签
                    contentInfoCard

                    Spacer().frame(height: 140)
                }
                .padding(.horizontal, 24)

                // ── 底部播放控制 ──
                VStack {
                    Spacer()
                    audioControlBar
                }
            }
        }
        .ignoresSafeArea()
        .task {
            await viewModel.fetchTodayContent()
        }
        .overlay(alignment: .topTrailing) {
            // 登录按钮
            if !AuthService.shared.isLoggedIn {
                NavigationLink(destination: LoginView()) {
                    Text("登录")
                        .font(.system(size: 15, weight: .medium))
                        .foregroundColor(.white.opacity(0.8))
                        .padding(.horizontal, 20)
                        .padding(.vertical, 10)
                        .background(.ultraThinMaterial)
                        .clipShape(Capsule())
                }
                .padding(.top, 60)
                .padding(.trailing, 20)
            }
        }
    }

    // MARK: - 情绪渐变（加载中/无内容兜底）
    private var moodGradient: some View {
        LinearGradient(
            colors: [
                Color(hex: viewModel.content?.colorPalette.primary ?? "#4A5568"),
                Color(hex: viewModel.content?.colorPalette.background ?? "#EDF2F7")
            ],
            startPoint: .top,
            endPoint: .bottom
        )
    }

    // MARK: - 内容信息卡片
    private var contentInfoCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            if let content = viewModel.content {
                // 情绪标签
                HStack(spacing: 6) {
                    Image(systemName: moodIcon(content.mood))
                        .font(.system(size: 13))
                    Text(moodDisplayName(content.mood))
                        .font(.system(size: 13, weight: .medium))
                }
                .foregroundColor(Color(hex: content.colorPalette.primary))
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    Color(hex: content.colorPalette.primary).opacity(0.12)
                )
                .clipShape(Capsule())

                // 标题
                Text(content.title)
                    .font(.system(size: 28, weight: .semibold, design: .serif))
                    .foregroundColor(Color(hex: content.colorPalette.text))

                // 描述
                if let desc = content.description {
                    Text(desc)
                        .font(.system(size: 15))
                        .foregroundColor(Color(hex: content.colorPalette.text).opacity(0.6))
                        .lineLimit(2)
                }
            } else if viewModel.isLoading {
                ProgressView()
                    .tint(.white)
            } else {
                Text("今日内容尚未发布\n明天再来看看")
                    .font(.system(size: 17, design: .serif))
                    .foregroundColor(.white.opacity(0.6))
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .liquidGlass()
    }

    // MARK: - 底部音频控制条
    private var audioControlBar: some View {
        HStack(spacing: 16) {
            // 播放/暂停
            Button(action: {
                if AudioService.shared.isPlaying {
                    AudioService.shared.pause()
                } else {
                    if let content = viewModel.content,
                       let url = URL(string: content.audioUrl) {
                        AudioService.shared.play(url: url, title: content.title)
                    }
                }
            }) {
                Image(systemName: AudioService.shared.isPlaying ? "pause.fill" : "play.fill")
                    .font(.system(size: 22))
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(.ultraThinMaterial)
                    .clipShape(Circle())
            }

            // 音频信息
            VStack(alignment: .leading, spacing: 2) {
                Text(viewModel.content?.title ?? "此刻")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(.white)
                Text("\(viewModel.content?.audioDurationSeconds ?? 180 / 60) 分钟 · 氛围音乐")
                    .font(.system(size: 12))
                    .foregroundColor(.white.opacity(0.5))
            }

            Spacer()

            // 过期倒计时
            if let expireStr = viewModel.content?.expireAt {
                Text(viewModel.remainingTime(from: expireStr))
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.5))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(.ultraThinMaterial)
                    .clipShape(Capsule())
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
        .padding(.bottom, 36)
        .background(
            LinearGradient(
                colors: [.clear, .black.opacity(0.3)],
                startPoint: .top,
                endPoint: .bottom
            )
        )
    }

    // MARK: - Helpers

    private func moodIcon(_ mood: String) -> String {
        switch mood {
        case "calm":        return "wind"
        case "focus":       return "target"
        case "warm":        return "sun.max"
        case "melancholy":  return "cloud.rain"
        case "energetic":   return "flame"
        case "dreamy":      return "sparkles"
        case "cozy":        return "house"
        default:            return "circle"
        }
    }

    private func moodDisplayName(_ mood: String) -> String {
        ContentMood(rawValue: mood)?.displayName ?? mood
    }
}

// MARK: - ViewModel

@MainActor
class DailyContentViewModel: ObservableObject {
    @Published var content: DailyContent?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let client = APIClient.shared

    func fetchTodayContent() async {
        isLoading = true
        defer { isLoading = false }

        do {
            content = try await client.get("/content/today")
        } catch {
            // 无内容不算错误
            if case APIError.httpError(404) = error {
                content = nil
                return
            }
            errorMessage = error.localizedDescription
        }
    }

    func remainingTime(from isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let expireDate = formatter.date(from: isoString) else {
            return "--:--"
        }
        let remaining = expireDate.timeIntervalSinceNow
        guard remaining > 0 else { return "已过期" }

        let hours = Int(remaining) / 3600
        let minutes = (Int(remaining) % 3600) / 60
        return String(format: "%02d:%02d", hours, minutes)
    }
}
