import SwiftUI

struct NodeView: View {
    @EnvironmentObject private var store: TutorStore
    let nodeID: String

    var body: some View {
        let node = store.node(nodeID)
        ScrollView {
            VStack(alignment: .leading, spacing: 8) {
                Text(node.title)
                    .font(.headline)
                    .fixedSize(horizontal: false, vertical: true)

                if let body = node.body {
                    Text(body)
                        .font(.footnote)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if let formula = node.formula {
                    Text(formula)
                        .font(.footnote.weight(.semibold))
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(6)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.blue.opacity(0.25), in: RoundedRectangle(cornerRadius: 8))
                }

                if let warn = node.warn {
                    Label {
                        Text(warn).fixedSize(horizontal: false, vertical: true)
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
                    .accessibilityLabel("Start over")
                }
            }
        }
    }

    @ViewBuilder
    private func actions(for node: TutorNode) -> some View {
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
        } else if let next = node.next {
            NavigationLink(value: next) {
                Label(node.nextLabel ?? "Next", systemImage: "arrow.right.circle.fill")
                    .frame(maxWidth: .infinity)
            }
            .tint(.green)
        } else {
            Button { store.goHome() } label: {
                Label("Start over", systemImage: "arrow.counterclockwise")
                    .frame(maxWidth: .infinity)
            }
        }
    }
}
