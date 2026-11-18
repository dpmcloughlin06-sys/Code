import Foundation
import SwiftUI

// Mirrors tree.json (see SPEC.md). Field names must match the JSON keys exactly.

struct MenuChoice: Codable, Hashable {
    let label: String
    let next: String
}

struct MenuNode: Codable, Identifiable {
    let id: String
    let title: String
    let tag: String?
    let highlight: String?
    let body: String?
    let steps: [String]?
    let caution: String?
    let choices: [MenuChoice]?
}

struct MenuAppInfo: Codable {
    let name: String
    let subject: String?
    let description: String?
    let highlightFont: String?
}

struct MenuTree: Codable {
    let schemaVersion: Int
    let app: MenuAppInfo
    let root: String
    let nodes: [MenuNode]
}

@MainActor
final class MenuStore: ObservableObject {
    @Published var path: [String] = []
    let rootID: String
    let app: MenuAppInfo
    private let nodes: [String: MenuNode]

    /// Loads tree.json from the app bundle. The file must be a member of the app target.
    init(resource: String = "tree") {
        if let url = Bundle.main.url(forResource: resource, withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let tree = try? JSONDecoder().decode(MenuTree.self, from: data) {
            rootID = tree.root
            app = tree.app
            nodes = Dictionary(tree.nodes.map { ($0.id, $0) }, uniquingKeysWith: { first, _ in first })
        } else {
            rootID = "missing"
            app = MenuAppInfo(name: "Menu App", subject: nil, description: nil, highlightFont: nil)
            nodes = [:]
        }
    }

    var monospacedHighlight: Bool { app.highlightFont == "monospaced" }

    func node(_ id: String) -> MenuNode {
        nodes[id] ?? MenuNode(
            id: id, title: "Missing screen", tag: nil, highlight: nil,
            body: "Couldn't load '\(id)'. Make sure tree.json is in the app target.",
            steps: nil, caution: nil, choices: nil)
    }

    func goHome() { path.removeAll() }
}
