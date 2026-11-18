import SwiftUI
import WatchKit

struct NodeView: View {
    @EnvironmentObject private var store: TutorStore
    let nodeID: String

    /// How many steps are visible. Steps appear one at a time as you finish them on paper.
    @State private var revealed = 1

    var body: some View {
        let node = store.node(nodeID)
        let steps = node.steps ?? []
        let finished = steps.isEmpty || revealed >= steps.count

        ScrollViewReader { proxy in
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
                        FormulaBox(text: formula)
                    }

                    if !steps.isEmpty {
                        ForEach(0..<min(revealed, steps.count), id: \.self) { i in
                            StepRow(number: i + 1, total: steps.count, text: steps[i],
                                    isCurrent: i == revealed - 1)
                                .id("step\(i)")
                        }
                        if !finished {
                            Button {
                                WKInterfaceDevice.current().play(.click)
                                withAnimation { revealed += 1 }
                            } label: {
                                Label("Done, step \(revealed + 1)", systemImage: "checkmark")
                                    .frame(maxWidth: .infinity)
                            }
                            .tint(.green)
                            .buttonStyle(.borderedProminent)

                            Button("Show all steps") {
                                withAnimation { revealed = steps.count }
                            }
                            .font(.caption2)
                            .buttonStyle(.plain)
                            .foregroundStyle(.secondary)
                            .frame(maxWidth: .infinity)
                        }
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

                    if finished {
                        if let outro = node.outro {
                            Text(outro)
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                                .id("outro")
                        }
                        actions(for: node)
                            .padding(.top, 4)
                            .id("actions")
                    }
                }
                .padding(.horizontal, 2)
            }
            .onChange(of: revealed) { _, newValue in
                withAnimation {
                    proxy.scrollTo("step\(min(newValue, steps.count) - 1)", anchor: .top)
                }
            }
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

private struct FormulaBox: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.footnote.weight(.semibold))
            .fixedSize(horizontal: false, vertical: true)
            .padding(6)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.blue.opacity(0.25), in: RoundedRectangle(cornerRadius: 8))
    }
}

/// The current step is large and bright; finished steps shrink and get a check mark.
private struct StepRow: View {
    let number: Int
    let total: Int
    let text: String
    let isCurrent: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 4) {
                Image(systemName: isCurrent ? "pencil.circle.fill" : "checkmark.circle.fill")
                    .foregroundStyle(isCurrent ? .yellow : .green)
                Text("Step \(number) of \(total)")
            }
            .font(.caption2.weight(.semibold))

            Text(text)
                .font(isCurrent ? .body : .caption)
                .foregroundStyle(isCurrent ? .primary : .secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(6)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(isCurrent ? Color.yellow.opacity(0.15) : Color.clear)
        )
    }
}
