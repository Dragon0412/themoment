import Foundation

// MARK: - 用户角色
enum UserRole: String, Codable {
    case guest = "guest"
    case user = "user"
    case admin = "admin"
}

// MARK: - 认证令牌
struct TokenResponse: Codable {
    let accessToken: String
    let tokenType: String
    let userId: String
    let isPremium: Bool
    let isGuest: Bool

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case userId = "user_id"
        case isPremium = "is_premium"
        case isGuest = "is_guest"
    }
}

// MARK: - 用户信息
struct UserInfo: Codable {
    let userId: String
    let role: String
    let isPremium: Bool
    let isGuest: Bool

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case role
        case isPremium = "is_premium"
        case isGuest = "is_guest"
    }
}

// MARK: - 购买验证
struct PurchaseVerifyResponse: Codable {
    let success: Bool
    let message: String
    let isPremium: Bool

    enum CodingKeys: String, CodingKey {
        case success, message
        case isPremium = "is_premium"
    }
}
