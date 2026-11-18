import SwiftUI

/// One screen. Order fixed by SPEC.md: title, highlight, body, steps, caution, choices.
/// A non-root screen without choices shows a Home button.
struct NodeView: View {
    @EnvironmentObject private var store: MenuStore
    let nodeID: String

    var body: some View {
        let node = store.node(nodeID)

        ScrollView {
            VStack(alignment: .leading, spacing: 8) {
                Text(node.title)
                    .font(.headline)
                    .fixedSize(horizontal: false, vertical: true)

                if let highlight = node.highlight {
                    Text(highlight)
                        .font(store.monospacedHighlight
                              ? .system(.footnote, design: .monospaced).weight(.semibold)
                              : .footnote.weight(.semibold))
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(6)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.blue.opacity(0.25), in: RoundedRectangle(cornerRadius: 8))
                }

                if let body = node.body {
                    Text(body)
                        .font(.footnote)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if let steps = node.steps {
                    VStack(alignment: .leading, spacing: 4) {
                        ForEach(steps.indices, id: \.self) { i in
                            HStack(alignment: .firstTextBaseline, spacing: 4) {
                                Text("\(i + 1).")
                                    .foregroundStyle(.green)
                                    .monospacedDigit()
                                Text(steps[i])
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            .font(.footnote)
                        }
                    }
                }

                if let caution = node.caution {
                    Label {
                        Text(caution).fixedSize(horizontal: false, vertical: true)
                    } icon: {
                        Image(systemName: "exclamationmark.triangle.fill")
                    }
                    .font(.caption2)
                    .foregroundStyle(.orange)
                }

                actions(for: node)
                    .padding(.top, 4)
            }
            .padding(.horizontal, 2)
        }
        .navigationTitle(node.tag ?? "")
        .toolbar {
            if nodeID != store.rootID {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { store.goHome() } label: {
                        Image(systemName: "house.fill")
                    }
                    .accessibilityLabel("Home")
                }
            }
        }
    }

    @ViewBuilder
    private func actions(for node: MenuNode) -> some View {
        if let choices = node.choices, !choices.isEmpty {
            VStack(spacing: 6) {
                ForEach(choices, id: \.self) { choice in
                    NavigationLink(value: choice.next) {
                        Text(choice.label)
                            .font(.footnote)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        } else if nodeID != store.rootID {
            Button { store.goHome() } label: {
                Label("Home", systemImage: "house")
                    .frame(maxWidth: .infinity)
            }
        }
    }
}
