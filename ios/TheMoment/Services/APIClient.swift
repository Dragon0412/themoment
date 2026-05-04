import Foundation

/// 通用 API 客户端
actor APIClient {
    static let shared = APIClient()
    private let session: URLSession
    private let decoder: JSONDecoder

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        self.session = URLSession(configuration: config)
        self.decoder = JSONDecoder()
    }

    /// 获取存储的 token
    private var authToken: String? {
        UserDefaults.standard.string(forKey: APIConfig.tokenKey)
    }

    // MARK: - GET

    func get<T: Decodable>(_ path: String) async throws -> T {
        let url = URL(string: "\(APIConfig.baseURL)\(path)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return try await perform(request)
    }

    // MARK: - POST

    func post<T: Decodable>(_ path: String, body: Encodable) async throws -> T {
        let url = URL(string: "\(APIConfig.baseURL)\(path)")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.httpBody = try JSONEncoder().encode(AnyEncodable(body))
        return try await perform(request)
    }

    // MARK: - Core

    private func perform<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            if let errorResp = try? decoder.decode(ErrorResponse.self, from: data) {
                throw APIError.serverError(httpResponse.statusCode, errorResp.detail)
            }
            throw APIError.httpError(httpResponse.statusCode)
        }

        // 处理空响应（如 204 No Content）
        if data.isEmpty, T.self == EmptyResponse.self {
            return EmptyResponse() as! T
        }

        return try decoder.decode(T.self, from: data)
    }
}

// MARK: - Helpers

struct AnyEncodable: Encodable {
    let value: Encodable
    init(_ value: Encodable) { self.value = value }
    func encode(to encoder: Encoder) throws {
        try value.encode(to: encoder)
    }
}

struct EmptyResponse: Codable {}

struct ErrorResponse: Codable {
    let detail: String
}

enum APIError: LocalizedError {
    case invalidResponse
    case httpError(Int)
    case serverError(Int, String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:          return "无效的服务器响应"
        case .httpError(let code):      return "HTTP 错误 (\(code))"
        case .serverError(_, let msg):  return msg
        }
    }
}
