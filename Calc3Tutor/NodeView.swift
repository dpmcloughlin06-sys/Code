import SwiftUI

/// One screen, as a native watch list:
/// header (topic chip + title) · Equations card · notes · Process · caution · buttons.
struct NodeView: View {
    @EnvironmentObject private var store: TutorStore
    let nodeID: String

    @ScaledMetric(relativeTo: .body) private var textSize: CGFloat = 16
    @ScaledMetric(relativeTo: .body) private var formulaSize: CGFloat = 16

    var body: some View {
        let node = store.node(nodeID)
        let isRoot = nodeID == store.rootID
        let tint = Theme.tint(for: node.tag)

        List {
            if !node.isMenu {
                Section {
                    Header(tag: node.tag, title: node.title, tint: tint)
                        .listRowBackground(Color.clear)
                        .listRowInsets(EdgeInsets(top: 0, leading: 6, bottom: 2, trailing: 6))
                }
            }

            if let formula = node.formula {
                Section {
                    FormulaCard(text: formula, size: formulaSize)
                        .listRowBackground(
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .fill(tint.opacity(0.16))
                        )
                } header: {
                    SectionLabel("Equations", tint: tint)
                }
            }

            if let body = node.body {
                Section {
                    MathText.render(body, size: textSize)
                        .lineSpacing(3)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.vertical, 2)
                }
            }

            if let steps = node.steps {
                Section {
                    ForEach(steps.indices, id: \.self) { i in
                        StepRow(number: i + 1, text: steps[i], size: textSize, tint: tint)
                    }
                } header: {
                    SectionLabel("Process", tint: tint)
                }
            }

            if let warn = node.warn {
                Section {
                    HStack(alignment: .top, spacing: 8) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .font(.footnote)
                            .foregroundStyle(.orange)
                            .padding(.top, 1)
                        MathText.render(warn, size: textSize - 2, weight: .medium)
                            .foregroundStyle(Color(red: 1.0, green: 0.78, blue: 0.5))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(.vertical, 2)
                    .listRowBackground(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(Color.orange.opacity(0.16))
                    )
                }
            }

            if let choices = node.choices, !choices.isEmpty {
                Section {
                    ForEach(choices, id: \.self) { choice in
                        NavigationLink(value: choice.next) {
                            ChoiceRow(label: choice.label, target: store.node(choice.next))
                        }
                    }
                } header: {
                    if !node.isMenu { SectionLabel("More", tint: tint) }
                }
            } else if !isRoot {
                Section {
                    Button { store.goHome() } label: {
                        Label("All topics", systemImage: "square.grid.2x2.fill")
                            .font(.body.weight(.semibold))
                            .frame(maxWidth: .infinity)
                    }
                    .listRowBackground(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(tint.opacity(0.22))
                    )
                    .foregroundStyle(tint)
                }
            }
        }
        .listSectionSpacing(.compact)
        .navigationTitle(node.isMenu ? node.title : "")
        .tint(tint)
        .toolbar {
            if !isRoot {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { store.goHome() } label: {
                        Image(systemName: "house.fill")
                    }
                    .accessibilityLabel("All topics")
                }
            }
        }
    }
}

/// Topic chip ("15.3") above a bold title.
private struct Header: View {
    let tag: String?
    let title: String
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            if let tag, !tag.isEmpty {
                Text(tag)
                    .font(.caption2.weight(.bold))
                    .monospacedDigit()
                    .foregroundStyle(tint)
                    .padding(.horizontal, 7)
                    .padding(.vertical, 2)
                    .background(Capsule().fill(tint.opacity(0.2)))
            }
            Text(title)
                .font(.title3.weight(.bold))
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

/// Small tinted uppercase label above a card.
private struct SectionLabel: View {
    let text: String
    let tint: Color
    init(_ text: String, tint: Color) {
        self.text = text
        self.tint = tint
    }

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .foregroundStyle(tint)
    }
}

/// Equations one per line, typeset, with hairline separators between them.
/// Lines that start with spaces continue the line above: no separator, indented.
private struct FormulaCard: View {
    let text: String
    let size: CGFloat

    var body: some View {
        let lines = text.components(separatedBy: "\n")
        VStack(alignment: .leading, spacing: 0) {
            ForEach(lines.indices, id: \.self) { i in
                let line = lines[i]
                let trimmed = line.trimmingCharacters(in: .whitespaces)
                let isContinuation = line.hasPrefix(" ") && !trimmed.isEmpty
                if i > 0 && !isContinuation {
                    Rectangle()
                        .fill(Color.white.opacity(0.12))
                        .frame(height: 1)
                        .padding(.vertical, 6)
                }
                MathText.render(trimmed, size: size, weight: .semibold)
                    .foregroundStyle(isContinuation ? Color.white.opacity(0.75) : Color.white)
                    .padding(.leading, isContinuation ? 12 : 0)
                    .padding(.top, isContinuation ? 2 : 0)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(.vertical, 6)
    }
}

/// Tinted number badge + step text.
private struct StepRow: View {
    let number: Int
    let text: String
    let size: CGFloat
    let tint: Color

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text("\(number)")
                .font(.system(size: 12, weight: .heavy, design: .rounded))
                .foregroundStyle(.black)
                .frame(width: 20, height: 20)
                .background(Circle().fill(tint))
            MathText.render(text, size: size)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, 3)
    }
}

/// Icon badge in the destination's colour, label, and its section number.
private struct ChoiceRow: View {
    let label: String
    let target: TutorNode

    var body: some View {
        let tint = Theme.tint(for: target.tag)
        HStack(spacing: 10) {
            Image(systemName: target.icon ?? (target.isMenu ? "list.bullet" : "doc.text"))
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(tint)
                .frame(width: 30, height: 30)
                .background(Circle().fill(tint.opacity(0.22)))
            VStack(alignment: .leading, spacing: 1) {
                MathText.render(label, size: 16, weight: .medium)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                if let tag = target.tag, !tag.isEmpty {
                    Text(tag)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}
