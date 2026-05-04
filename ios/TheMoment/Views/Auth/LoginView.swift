import SwiftUI
import AuthenticationServices

/// 登录页 — Apple ID 登录 + 游客模式
struct LoginView: View {
    @StateObject private var auth = AuthService.shared
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            // 背景
            LinearGradient(
                colors: [Color(hex: "#1A1A2E"), Color(hex: "#16213E"), Color(hex: "#0F3460")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 32) {
                Spacer()

                // Logo
                VStack(spacing: 12) {
                    Text("此刻")
                        .font(.system(size: 48, weight: .medium, design: .serif))
                        .foregroundColor(.white)

                    Text("你的数字精神避难所")
                        .font(.system(size: 16))
                        .foregroundColor(.white.opacity(0.5))
                }

                Spacer()

                // 登录按钮
                VStack(spacing: 14) {
                    // Apple ID 登录
                    SignInWithAppleButton(.signIn) { request in
                        request.requestedScopes = [.fullName, .email]
                    } onCompletion: { result in
                        handleAppleSignIn(result)
                    }
                    .signInWithAppleButtonStyle(.white)
                    .frame(height: 50)
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))

                    // 游客登录
                    Button(action: {
                        Task {
                            let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
                            await auth.signInAsGuest(deviceId: deviceId)
                        }
                    }) {
                        HStack(spacing: 8) {
                            Image(systemName: "eye")
                            Text("先看看")
                        }
                        .font(.system(size: 17, weight: .medium))
                        .foregroundColor(.white.opacity(0.7))
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(.ultraThinMaterial)
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                }
                .padding(.horizontal, 40)

                // 错误信息
                if let error = auth.errorMessage {
                    Text(error)
                        .font(.system(size: 13))
                        .foregroundColor(.red.opacity(0.8))
                        .padding(.top, 8)
                }

                // Loading
                if auth.isLoading {
                    ProgressView()
                        .tint(.white)
                        .padding(.top, 8)
                }

                Spacer()

                // 底部文案
                Text("登录即表示同意《用户协议》和《隐私政策》")
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.3))
                    .padding(.bottom, 40)
            }
        }
        .onChange(of: auth.isLoggedIn) { _, loggedIn in
            if loggedIn {
                dismiss()
            }
        }
    }

    private func handleAppleSignIn(_ result: Result<ASAuthorization, Error>) {
        switch result {
        case .success(let authorization):
            guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential,
                  let identityToken = credential.identityToken,
                  let tokenStr = String(data: identityToken, encoding: .utf8),
                  let authCode = credential.authorizationCode,
                  let codeStr = String(data: authCode, encoding: .utf8)
            else { return }

            Task {
                await AuthService.shared.signInWithApple(
                    identityToken: tokenStr,
                    authorizationCode: codeStr,
                    userIdentifier: credential.user
                )
            }

        case .failure(let error):
            AuthService.shared.errorMessage = error.localizedDescription
        }
    }
}
