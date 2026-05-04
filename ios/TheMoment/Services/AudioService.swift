import AVFoundation
import MediaPlayer

/// 音频播放服务 — 后台播放 + 锁屏控制
@MainActor
class AudioService: ObservableObject {
    static let shared = AudioService()

    @Published var isPlaying: Bool = false
    @Published var currentTitle: String?

    private var player: AVPlayer?
    private var timeObserver: Any?

    private init() {
        setupAudioSession()
        setupRemoteCommandCenter()
    }

    // MARK: - 播放

    func play(url: URL, title: String? = nil) {
        stop()

        currentTitle = title
        let playerItem = AVPlayerItem(url: url)
        player = AVPlayer(playerItem: playerItem)

        // 监听播放结束
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(itemDidFinishPlaying),
            name: .AVPlayerItemDidPlayToEndTime,
            object: playerItem
        )

        player?.play()
        isPlaying = true
        updateNowPlayingInfo()
    }

    func pause() {
        player?.pause()
        isPlaying = false
        updateNowPlayingInfo()
    }

    func resume() {
        player?.play()
        isPlaying = true
        updateNowPlayingInfo()
    }

    func stop() {
        player?.pause()
        player = nil
        isPlaying = false
        if let observer = timeObserver {
            player?.removeTimeObserver(observer)
            timeObserver = nil
        }
    }

    func toggle() {
        isPlaying ? pause() : resume()
    }

    // MARK: - Audio Session

    private func setupAudioSession() {
        do {
            try AVAudioSession.sharedInstance().setCategory(
                .playback,
                mode: .default,
                options: [.allowAirPlay, .allowBluetooth]
            )
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Audio session setup failed: \(error)")
        }
    }

    // MARK: - Remote Command Center (锁屏控制)

    private func setupRemoteCommandCenter() {
        let commandCenter = MPRemoteCommandCenter.shared()

        commandCenter.playCommand.addTarget { [weak self] _ in
            self?.resume()
            return .success
        }

        commandCenter.pauseCommand.addTarget { [weak self] _ in
            self?.pause()
            return .success
        }

        commandCenter.togglePlayPauseCommand.addTarget { [weak self] _ in
            self?.toggle()
            return .success
        }
    }

    private func updateNowPlayingInfo() {
        var info = [String: Any]()
        info[MPMediaItemPropertyTitle] = currentTitle ?? "此刻"
        info[MPMediaItemPropertyArtist] = "此刻 · The Moment"
        info[MPNowPlayingInfoPropertyPlaybackRate] = isPlaying ? 1.0 : 0.0

        MPNowPlayingInfoCenter.default().nowPlayingInfo = info
    }

    // MARK: - Notification

    @objc private func itemDidFinishPlaying() {
        isPlaying = false
        player?.seek(to: .zero)
    }
}
