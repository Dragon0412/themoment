import SwiftUI

/// App 入口 — 路由导航 + 充电检测
@main
struct TheMomentApp: App {
    @StateObject private var auth = AuthService.shared
    @State private var isCharging = false
    @State private var showStandBy = false

    var body: some Scene {
        WindowGroup {
            NavigationStack {
                ZStack {
                    if !auth.isLoggedIn {
                        // 未登录 → 每日一境 + 登录入口
                        DailyContentView()
                    } else {
                        // 已登录 → 主界面
                        TabView {
                            DailyContentView()
                                .tabItem {
                                    Image(systemName: "sparkles")
                                    Text("此刻")
                                }

                            if !auth.isPremium {
                                PurchaseView()
                                    .tabItem {
                                        Image(systemName: "infinity")
                                        Text("解锁")
                                    }
                            }

                            StandByView(palette: nil)
                                .tabItem {
                                    Image(systemName: "clock")
                                    Text("StandBy")
                                }
                        }
                    }
                }
            }
            .onReceive(
                NotificationCenter.default.publisher(for: UIDevice.batteryStateDidChangeNotification)
            ) { _ in
                UIDevice.current.isBatteryMonitoringEnabled = true
                isCharging = UIDevice.current.batteryState == .charging ||
                             UIDevice.current.batteryState == .full

                // 充电 + 横屏 → 自动进入 StandBy（后续版本）
                if isCharging {
                    showStandBy = true
                }
            }
            .onReceive(
                NotificationCenter.default.publisher(for: UIDevice.orientationDidChangeNotification)
            ) { _ in
                // 横竖屏切换监听
            }
        }
    }
}
