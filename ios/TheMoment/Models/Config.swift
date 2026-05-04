import Foundation

/// API 配置 — 修改为你的服务器地址
enum APIConfig {
    /// 后端 API 地址
    static let baseURL = "http://localhost:8000/api/v1"

    /// UserDefaults 存储 key
    static let tokenKey = "auth_token"
    static let userIdKey = "user_id"
    static let isPremiumKey = "is_premium"
}
