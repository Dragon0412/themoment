import Foundation
import AuthenticationServices

/// 认证服务 — Apple ID 登录 + 游客登录 + Token 管理
@MainActor
class AuthService: ObservableObject {
    static let shared = AuthService()

    @Published var isLoggedIn: Bool = false
    @Published var isPremium: Bool = false
    @Published var isGuest: Bool = false
    @Published var userId: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private let client = APIClient.shared

    private init() {
        // 从本地恢复登录状态
        if let token = UserDefaults.standard.string(forKey: APIConfig.tokenKey),
           !token.isEmpty {
            isLoggedIn = true
            isPremium = UserDefaults.standard.bool(forKey: APIConfig.isPremiumKey)
            userId = UserDefaults.standard.string(forKey: APIConfig.userIdKey) ?? ""
        }
    }

    // MARK: - Apple ID 登录

    func signInWithApple(identityToken: String, authorizationCode: String, userIdentifier: String?) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let body = AppleSignInBody(
            identityToken: identityToken,
            authorizationCode: authorizationCode,
            userIdentifier: userIdentifier
        )

        do {
            let response: TokenResponse = try await client.post("/auth/apple", body: body)
            saveToken(response)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    // MARK: - 游客登录

    func signInAsGuest(deviceId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let body = GuestLoginBody(deviceId: deviceId)

        do {
            let response: TokenResponse = try await client.post("/auth/guest", body: body)
            saveToken(response)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    // MARK: - 登出

    func signOut() {
        UserDefaults.standard.removeObject(forKey: APIConfig.tokenKey)
        UserDefaults.standard.removeObject(forKey: APIConfig.userIdKey)
        UserDefaults.standard.removeObject(forKey: APIConfig.isPremiumKey)
        isLoggedIn = false
        isPremium = false
        isGuest = false
        userId = ""
    }

    // MARK: - Private

    private func saveToken(_ response: TokenResponse) {
        UserDefaults.standard.set(response.accessToken, forKey: APIConfig.tokenKey)
        UserDefaults.standard.set(response.userId, forKey: APIConfig.userIdKey)
        UserDefaults.standard.set(response.isPremium, forKey: APIConfig.isPremiumKey)

        isLoggedIn = true
        isPremium = response.isPremium
        isGuest = response.isGuest
        userId = response.userId
    }
}

// MARK: - Request Bodies

private struct AppleSignInBody: Encodable {
    let identityToken: String
    let authorizationCode: String
    let userIdentifier: String?

    enum CodingKeys: String, CodingKey {
        case identityToken = "identity_token"
        case authorizationCode = "authorization_code"
        case userIdentifier = "user_identifier"
    }
}

private struct GuestLoginBody: Encodable {
    let deviceId: String

    enum CodingKeys: String, CodingKey {
        case deviceId = "device_id"
    }
}
