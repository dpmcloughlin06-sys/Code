import Foundation
import SwiftUI

struct TutorChoice: Codable, Hashable {
    let label: String
    let next: String
}

/// One watch screen (see tools/build_tree.py).
struct TutorNode: Codable, Identifiable {
    let id: String
    let title: String
    let tag: String?
    let formula: String?
    let body: String?
    let steps: [String]?
    let warn: String?
    let choices: [TutorChoice]?

    /// A screen that is only a list of buttons (no content above them).
    var isMenu: Bool { formula == nil && body == nil && steps == nil && warn == nil }
}

struct TutorGraph: Codable {
    let root: String
    let nodes: [TutorNode]
}

@MainActor
final class TutorStore: ObservableObject {
    @Published var path: [String] = []
    let rootID: String
    private let nodes: [String: TutorNode]

    init() {
        if let url = Bundle.main.url(forResource: "tutor", withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let graph = try? JSONDecoder().decode(TutorGraph.self, from: data) {
            rootID = graph.root
            nodes = Dictionary(graph.nodes.map { ($0.id, $0) }, uniquingKeysWith: { first, _ in first })
        } else {
            rootID = "missing"
            nodes = [:]
        }
        // Launch argument `-startNode <id>` opens a screen directly (used for screenshots).
        if let start = UserDefaults.standard.string(forKey: "startNode"), nodes[start] != nil, start != rootID {
            path = [start]
        }
    }

    func node(_ id: String) -> TutorNode {
        nodes[id] ?? TutorNode(
            id: id, title: "Missing screen", tag: nil, formula: nil,
            body: "Couldn't load '\(id)'. Make sure tutor.json is in the app target.",
            steps: nil, warn: nil, choices: nil)
    }

    func goHome() { path.removeAll() }
}
