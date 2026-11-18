import SwiftUI

/// Colours by topic so each area of the course is recognisable at a glance.
enum Theme {
    static func tint(for tag: String?) -> Color {
        guard let tag else { return .blue }
        if tag.hasPrefix("15") { return Color(red: 0.25, green: 0.56, blue: 1.0) }   // integration: blue
        if tag.hasPrefix("16") { return Color(red: 0.69, green: 0.45, blue: 1.0) }   // vector calculus: purple
        switch tag {
        case "Tricks": return Color(red: 1.0, green: 0.62, blue: 0.2)                // orange
        case "Mass": return Color(red: 0.2, green: 0.8, blue: 0.75)                  // teal
        case "Exam 3": return Color(red: 0.3, green: 0.82, blue: 0.45)               // green
        default: return Color(red: 0.25, green: 0.56, blue: 1.0)
        }
    }
}
