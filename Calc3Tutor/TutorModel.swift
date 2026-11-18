import Foundation
import SwiftUI

struct TutorChoice: Codable, Hashable {
    let label: String
    let next: String
}

/// One watch screen in the decision tree (see tools/build_tree.py).
struct TutorNode: Codable, Identifiable {
    let id: String
    let title: String
    let tag: String?
    let body: String?
    let formula: String?
    let warn: String?
    let choices: [TutorChoice]?
    let next: String?
    let nextLabel: String?
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
    }

    func node(_ id: String) -> TutorNode {
        nodes[id] ?? TutorNode(
            id: id, title: "Missing screen", tag: nil,
            body: "Couldn't load '\(id)'. Make sure tutor.json is in the app target.",
            formula: nil, warn: nil, choices: nil, next: nil, nextLabel: nil)
    }

    func goHome() { path.removeAll() }
}
