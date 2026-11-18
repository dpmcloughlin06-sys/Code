import SwiftUI

@main
struct MenuApp: App {
    @StateObject private var store = MenuStore()

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
