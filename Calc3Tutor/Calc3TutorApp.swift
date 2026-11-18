import SwiftUI

@main
struct Calc3TutorApp: App {
    @StateObject private var store = TutorStore()

    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $store.path) {
                NodeView(nodeID: store.rootID)
                    .navigationDestination(for: String.self) { id in
                        NodeView(nodeID: id)
                    }
            }
            .environmentObject(store)
        }
    }
}
