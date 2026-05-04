import Foundation

// MARK: - 情绪标签
enum ContentMood: String, Codable, CaseIterable {
    case calm = "calm"
    case focus = "focus"
    case warm = "warm"
    case melancholy = "melancholy"
    case energetic = "energetic"
    case dreamy = "dreamy"
    case cozy = "cozy"

    var displayName: String {
        switch self {
        case .calm:        return "平静"
        case .focus:       return "专注"
        case .warm:        return "温暖"
        case .melancholy:  return "忧伤"
        case .energetic:   return "活力"
        case .dreamy:      return "梦幻"
        case .cozy:        return "舒适"
        }
    }
}

// MARK: - 内容状态
enum ContentStatus: String, Codable {
    case draft = "draft"
    case published = "published"
    case expired = "expired"
    case archived = "archived"
}

// MARK: - 每日内容
struct DailyContent: Codable, Identifiable {
    let id: String
    let title: String
    let mood: String
    let description: String?
    let imageUrl: String
    let thumbnailUrl: String?
    let audioUrl: String
    let audioDurationSeconds: Int
    let colorPalette: ColorPalette
    let glassParams: GlassParams?
    let publishDate: String?
    let expireAt: String
    let viewCount: Int

    enum CodingKeys: String, CodingKey {
        case id, title, mood, description
        case imageUrl = "image_url"
        case thumbnailUrl = "thumbnail_url"
        case audioUrl = "audio_url"
        case audioDurationSeconds = "audio_duration_seconds"
        case colorPalette = "color_palette"
        case glassParams = "glass_params"
        case publishDate = "publish_date"
        case expireAt = "expire_at"
        case viewCount = "view_count"
    }
}

// MARK: - 自适应色板
struct ColorPalette: Codable {
    let primary: String
    let secondary: String
    let accent: String
    let background: String
    let text: String
}

// MARK: - Liquid Glass 参数
struct GlassParams: Codable {
    let blur: Double
    let saturation: Double
    let tint: String
}
