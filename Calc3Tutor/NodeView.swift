import SwiftUI

/// One screen, drawn as a native watch list so each part sits on its own card:
/// title · Equations · notes · Process · caution · buttons.
struct NodeView: View {
    @EnvironmentObject private var store: TutorStore
    let nodeID: String

    var body: some View {
        let node = store.node(nodeID)
        let isRoot = nodeID == store.rootID

        List {
            // Menu screens use the nav bar title instead, so the list starts at the top.
            if !node.isMenu {
                Section {
                    Text(node.title)
                        .font(.title3.weight(.bold))
                        .fixedSize(horizontal: false, vertical: true)
                        .listRowBackground(Color.clear)
                        .listRowInsets(EdgeInsets(top: 0, leading: 4, bottom: 0, trailing: 4))
                }
            }

            if let formula = node.formula {
                Section {
                    FormulaLines(text: formula)
                } header: {
                    SectionLabel("Equations")
                }
            }

            if let body = node.body {
                Section {
                    Text(body)
                        .font(.body)
                        .lineSpacing(2)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if let steps = node.steps {
                Section {
                    ForEach(steps.indices, id: \.self) { i in
                        StepRow(number: i + 1, text: steps[i])
                    }
                } header: {
                    SectionLabel("Process")
                }
            }

            if let warn = node.warn {
                Section {
                    Label {
                        Text(warn).fixedSize(horizontal: false, vertical: true)
                    } icon: {
                        Image(systemName: "exclamationmark.triangle.fill")
                    }
                    .font(.footnote.weight(.medium))
                    .foregroundStyle(.orange)
                    .listRowBackground(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(Color.orange.opacity(0.18))
                    )
                }
            }

            if let choices = node.choices, !choices.isEmpty {
                Section {
                    ForEach(choices, id: \.self) { choice in
                        NavigationLink(value: choice.next) {
                            Text(choice.label)
                                .font(.body)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                } header: {
                    if !node.isMenu { SectionLabel("More") }
                }
            } else if !isRoot {
                Section {
                    Button { store.goHome() } label: {
                        Label("Problem types", systemImage: "square.grid.2x2")
                            .frame(maxWidth: .infinity)
                    }
                    .foregroundStyle(.tint)
                }
            }
        }
        .listSectionSpacing(.compact)
        .navigationTitle(node.isMenu ? node.title : (node.tag ?? ""))
        .toolbar {
            if !isRoot {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { store.goHome() } label: {
                        Image(systemName: "house.fill")
                    }
                    .accessibilityLabel("Problem types")
                }
            }
        }
    }
}

/// Small uppercase label above a card.
private struct SectionLabel: View {
    let text: String
    init(_ text: String) { self.text = text }

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.semibold))
            .foregroundStyle(.secondary)
    }
}

/// Equations one per line with breathing room. Lines that start with spaces are
/// continuations of the line above and are indented.
private struct FormulaLines: View {
    let text: String

    var body: some View {
        let lines = text.components(separatedBy: "\n")
        VStack(alignment: .leading, spacing: 6) {
            ForEach(lines.indices, id: \.self) { i in
                let line = lines[i]
                let trimmed = line.trimmingCharacters(in: .whitespaces)
                let isContinuation = line.hasPrefix(" ") && !trimmed.isEmpty
                Text(trimmed)
                    .font(.system(.body, design: .rounded).weight(.semibold))
                    .foregroundStyle(isContinuation ? Color.secondary : Color.primary)
                    .padding(.leading, isContinuation ? 10 : 0)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(.vertical, 4)
    }
}

/// Numbered badge + step text.
private struct StepRow: View {
    let number: Int
    let text: String

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text("\(number)")
                .font(.caption2.weight(.bold))
                .monospacedDigit()
                .foregroundStyle(.black)
                .frame(width: 18, height: 18)
                .background(Circle().fill(Color.green))
            Text(text)
                .font(.body)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, 2)
    }
}
