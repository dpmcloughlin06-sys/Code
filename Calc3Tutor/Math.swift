import SwiftUI

// Textbook-style math for the watch. See tools/build_tree.py for the markup:
// words outside $...$, math inside: x^2, x_1, \frac{a}{b}, \sqrt{x}, ∫_a^b, \bar{x}, \bf{F}, \text{..}.

// MARK: - Parsed form

indirect enum MathNode {
    case run(String, MathRunStyle)
    case space
    case sub([MathNode])
    case sup([MathNode])
    case frac([MathNode], [MathNode])
    case sqrt([MathNode])
    case bigOp(String, lower: [MathNode]?, upper: [MathNode]?)
}

enum MathRunStyle { case prose, math, upright, bold }

enum MathParser {
    /// Splits a line into prose and $math$ segments and parses both.
    static func parse(_ line: String) -> [MathNode] {
        var nodes: [MathNode] = []
        let parts = line.components(separatedBy: "$")
        for (k, part) in parts.enumerated() {
            if k % 2 == 0 {
                nodes += prose(part)
            } else {
                var scanner = MathScanner(Array(part))
                nodes += scanner.sequence(untilBrace: false)
            }
        }
        return nodes
    }

    private static func prose(_ s: String) -> [MathNode] {
        var out: [MathNode] = []
        var word = ""
        for c in s {
            if c == " " {
                if !word.isEmpty { out.append(.run(word, .prose)); word = "" }
                out.append(.space)
            } else {
                word.append(c)
            }
        }
        if !word.isEmpty { out.append(.run(word, .prose)) }
        return out
    }
}

private struct MathScanner {
    let c: [Character]
    var i = 0
    init(_ c: [Character]) { self.c = c }

    static let bigOps: Set<Character> = ["∫", "∬", "∭", "∮"]

    mutating func sequence(untilBrace: Bool) -> [MathNode] {
        var out: [MathNode] = []
        var run = ""
        func flush() {
            if !run.isEmpty { out.append(.run(run, .math)); run = "" }
        }
        while i < c.count {
            let ch = c[i]
            if ch == "}" {
                i += 1
                if untilBrace { break }
                continue
            }
            if ch == " " {
                flush(); out.append(.space); i += 1
                while i < c.count, c[i] == " " { i += 1 }
                continue
            }
            if ch == "{" {
                flush(); i += 1
                out += sequence(untilBrace: true)
                continue
            }
            if ch == "^" || ch == "_" {
                flush(); i += 1
                let arg = argument()
                out.append(ch == "^" ? .sup(arg) : .sub(arg))
                continue
            }
            if MathScanner.bigOps.contains(ch) {
                flush(); i += 1
                var lower: [MathNode]?
                var upper: [MathNode]?
                for _ in 0..<2 where i < c.count {
                    if c[i] == "_" { i += 1; lower = argument() } else if c[i] == "^" { i += 1; upper = argument() }
                }
                out.append(.bigOp(String(ch), lower: lower, upper: upper))
                continue
            }
            if ch == "\\" {
                flush(); i += 1
                let name = commandName()
                switch name {
                case "frac":
                    let num = argument()
                    let den = argument()
                    out.append(.frac(num, den))
                case "sqrt":
                    out.append(.sqrt(argument()))
                case "text":
                    out.append(.run(rawArgument(), .upright))
                case "bf":
                    out += restyle(argument(), .bold)
                case "bar":
                    out += overbar(argument())
                case ",":
                    out.append(.run("\u{2009}", .upright))
                default:
                    run += name
                }
                continue
            }
            run.append(ch)
            i += 1
        }
        flush()
        return out
    }

    /// `{...}` group or a single character.
    mutating func argument() -> [MathNode] {
        guard i < c.count else { return [] }
        if c[i] == "{" {
            i += 1
            return sequence(untilBrace: true)
        }
        let ch = c[i]
        i += 1
        return [.run(String(ch), .math)]
    }

    mutating func rawArgument() -> String {
        guard i < c.count, c[i] == "{" else { return "" }
        i += 1
        var s = ""
        var depth = 1
        while i < c.count {
            if c[i] == "{" { depth += 1 }
            if c[i] == "}" { depth -= 1; if depth == 0 { i += 1; break } }
            s.append(c[i])
            i += 1
        }
        return s
    }

    mutating func commandName() -> String {
        guard i < c.count else { return "" }
        if !c[i].isLetter {
            let s = String(c[i])
            i += 1
            return s
        }
        var name = ""
        while i < c.count, c[i].isLetter { name.append(c[i]); i += 1 }
        return name
    }

    private func restyle(_ nodes: [MathNode], _ style: MathRunStyle) -> [MathNode] {
        nodes.map { node in
            if case let .run(s, _) = node { return .run(s, style) }
            return node
        }
    }

    private func overbar(_ nodes: [MathNode]) -> [MathNode] {
        nodes.map { node in
            if case let .run(s, style) = node {
                return .run(s.map { "\($0)\u{0304}" }.joined(), style)
            }
            return node
        }
    }
}

// MARK: - Inline text (runs, subscripts, superscripts)

struct MathFonts {
    let size: CGFloat
    let weight: Font.Weight

    func prose(_ s: CGFloat) -> Font { .system(size: s, weight: weight, design: .rounded) }
    func upright(_ s: CGFloat) -> Font { .system(size: s, weight: weight, design: .serif) }
    func italic(_ s: CGFloat) -> Font { .system(size: s, weight: weight, design: .serif).italic() }
    func bold(_ s: CGFloat) -> Font { .system(size: s, weight: .bold, design: .serif) }
}

enum MathInline {
    static let functions: Set<String> = ["sin", "cos", "tan", "sec", "csc", "cot", "arcsin", "arccos",
                                         "arctan", "ln", "log", "exp", "div", "curl", "grad"]

    /// Builds one Text, placing every leaf at an absolute baseline offset.
    static func text(_ nodes: [MathNode], fonts: MathFonts, size: CGFloat, offset: CGFloat) -> Text {
        var result = Text("")
        for node in nodes {
            switch node {
            case let .run(s, style):
                result = result + run(s, style: style, fonts: fonts, size: size, offset: offset)
            case .space:
                result = result + Text(" ").font(fonts.upright(size))
            case let .sub(children):
                result = result + text(children, fonts: fonts, size: (size * 0.7).rounded(),
                                       offset: offset - size * 0.2)
            case let .sup(children):
                let small = (size * 0.7).rounded()
                result = result + Text("\u{200A}").font(fonts.upright(small))
                    + text(children, fonts: fonts, size: small, offset: offset + size * 0.42)
            case let .frac(num, den):
                // Inside a script there's no room to stack; write it inline.
                result = result + text(num, fonts: fonts, size: size, offset: offset)
                    + Text("/").font(fonts.upright(size)).baselineOffset(offset)
                    + text(den, fonts: fonts, size: size, offset: offset)
            case let .sqrt(children):
                result = result + Text("√").font(fonts.upright(size)).baselineOffset(offset)
                    + text(children, fonts: fonts, size: size, offset: offset)
            case let .bigOp(symbol, _, _):
                result = result + Text(symbol).font(fonts.upright(size)).baselineOffset(offset)
            }
        }
        return result
    }

    private static func run(_ s: String, style: MathRunStyle, fonts: MathFonts, size: CGFloat,
                            offset: CGFloat) -> Text {
        switch style {
        case .prose:
            return Text(s).font(fonts.prose(size)).baselineOffset(offset)
        case .upright:
            return Text(s).font(fonts.upright(size)).baselineOffset(offset)
        case .bold:
            return Text(s).font(fonts.bold(size)).baselineOffset(offset)
        case .math:
            // Letters italic, except function names; digits and symbols upright.
            var result = Text("")
            let chars = Array(s)
            var k = 0
            while k < chars.count {
                if chars[k].isASCII && chars[k].isLetter {
                    var word = ""
                    while k < chars.count, chars[k].isASCII, chars[k].isLetter { word.append(chars[k]); k += 1 }
                    if functions.contains(word) {
                        result = result + Text(word).font(fonts.upright(size)).baselineOffset(offset)
                    } else {
                        result = result + Text(word).font(fonts.italic(size)).baselineOffset(offset)
                    }
                } else if chars[k].isLetter {
                    result = result + Text(String(chars[k])).font(fonts.italic(size)).baselineOffset(offset)
                    k += 1
                } else {
                    result = result + Text(String(chars[k])).font(fonts.upright(size)).baselineOffset(offset)
                    k += 1
                }
            }
            return result
        }
    }
}

// MARK: - Atoms: the unbreakable pieces a line is built from

/// Where a line may wrap before an atom: 0 = glued to the previous atom, 1 = a space
/// (wrap only if a term is too long), 2 = a natural break (between words, next to =, +, −),
/// 3 = the best break (after a comma).
struct MathAtom: Identifiable {
    let id: Int
    let level: Int
    let view: AnyView
}

enum MathAtoms {
    /// Natural places to wrap, as when writing by hand: after a comma or "=",
    /// or before "+", "−" and relations, so a new line starts with the operator.
    static let breakAfter: Set<Character> = [",", ";", ":", "=", "→", "⟺", "≈", "✓"]
    static let breakBefore: Set<Character> = ["+", "−", "-", "=", "→", "⟺", "≤", "≥", "<", ">", "·", "×", "±"]

    static func build(_ nodes: [MathNode], fonts: MathFonts, size: CGFloat) -> [MathAtom] {
        var atoms: [MathAtom] = []
        var pending: Text?
        var pendingLevel = 0
        var spaced = false          // a space came before the next atom
        var lastChar: Character?    // last character drawn, to judge break points
        var lastWasProse = false

        func level(startsWith first: Character?, prose: Bool, opLike: Bool) -> Int {
            guard spaced, !(atoms.isEmpty && pending == nil) else { return 0 }
            if let c = lastChar, c == "," || c == ";" { return 3 }
            if prose || lastWasProse || opLike { return 2 }
            if let c = lastChar, breakAfter.contains(c) { return 2 }
            if let f = first, breakBefore.contains(f) { return 2 }
            return 1
        }
        func emit(_ view: AnyView, level: Int) {
            atoms.append(MathAtom(id: atoms.count, level: level, view: view))
        }
        func flush() {
            if let t = pending {
                emit(AnyView(t.fixedSize()), level: pendingLevel)
                pending = nil
            }
        }

        for node in nodes {
            switch node {
            case .space:
                flush()
                spaced = true
            case .run, .sub, .sup:
                var first: Character?
                var prose = false
                if case let .run(s, style) = node {
                    first = s.first
                    prose = style == .prose
                }
                if pending == nil {
                    pendingLevel = level(startsWith: first, prose: prose, opLike: false)
                    spaced = false
                }
                pending = (pending ?? Text("")) + MathInline.text([node], fonts: fonts, size: size, offset: 0)
                if case let .run(s, style) = node {
                    lastChar = s.last
                    lastWasProse = style == .prose
                } else {
                    lastWasProse = false
                }
            case let .frac(num, den):
                flush()
                emit(AnyView(FractionView(num: num, den: den, fonts: fonts, size: size)),
                     level: level(startsWith: nil, prose: false, opLike: false))
                spaced = false; lastChar = "x"; lastWasProse = false
            case let .sqrt(children):
                flush()
                emit(AnyView(RootView(content: children, fonts: fonts, size: size)),
                     level: level(startsWith: nil, prose: false, opLike: false))
                spaced = false; lastChar = "x"; lastWasProse = false
            case let .bigOp(symbol, lower, upper):
                flush()
                emit(AnyView(BigOpView(symbol: symbol, lower: lower, upper: upper, fonts: fonts, size: size)),
                     level: level(startsWith: nil, prose: false, opLike: true))
                spaced = false; lastChar = nil; lastWasProse = false
            }
        }
        flush()
        return atoms
    }
}

// MARK: - Views

/// One line of mixed words and math. Wraps between terms like handwriting would.
struct MathLine: View {
    let text: String
    var size: CGFloat = 16
    var weight: Font.Weight = .regular

    var body: some View {
        let fonts = MathFonts(size: size, weight: weight)
        let atoms = MathAtoms.build(MathParser.parse(text), fonts: fonts, size: size)
        MathFlow(wrap: true, gap: size * 0.28, lineGap: size * 0.3) {
            ForEach(atoms) { atom in
                atom.view.layoutValue(key: BreakLevel.self, value: atom.level)
            }
        }
    }
}

/// A row of math that never wraps (used inside fractions, roots and limits).
struct MathRow: View {
    let nodes: [MathNode]
    let fonts: MathFonts
    let size: CGFloat

    var body: some View {
        let atoms = MathAtoms.build(nodes, fonts: fonts, size: size)
        MathFlow(wrap: false, gap: size * 0.25, lineGap: 0) {
            ForEach(atoms) { atom in
                atom.view.layoutValue(key: BreakLevel.self, value: atom.level)
            }
        }
    }
}

struct FractionView: View {
    let num: [MathNode]
    let den: [MathNode]
    let fonts: MathFonts
    let size: CGFloat

    var body: some View {
        let inner = (size * 0.82).rounded()
        FractionLayout(axis: size * 0.3, gap: 1.5) {
            MathRow(nodes: num, fonts: fonts, size: inner)
            Rectangle().frame(height: max(1, size * 0.07))
            MathRow(nodes: den, fonts: fonts, size: inner)
        }
        .padding(.horizontal, 1)
    }
}

struct RootView: View {
    let content: [MathNode]
    let fonts: MathFonts
    let size: CGFloat

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 0) {
            Text("√").font(fonts.upright(size * 1.05))
            MathRow(nodes: content, fonts: fonts, size: size)
                .padding(.top, size * 0.12)
                .padding(.trailing, 1)
                .overlay(alignment: .top) {
                    Rectangle().frame(height: max(1, size * 0.07))
                }
        }
    }
}

struct BigOpView: View {
    let symbol: String
    let lower: [MathNode]?
    let upper: [MathNode]?
    let fonts: MathFonts
    let size: CGFloat

    var body: some View {
        let limit = (size * 0.62).rounded()
        BigOpLayout(overlap: size * 0.2, drop: size * 0.12) {
            if let upper {
                MathRow(nodes: upper, fonts: fonts, size: limit)
            } else {
                Color.clear.frame(width: 0, height: 0)
            }
            Text(symbol).font(.system(size: size * 1.45, weight: .light, design: .serif))
            if let lower {
                MathRow(nodes: lower, fonts: fonts, size: limit)
            } else {
                Color.clear.frame(width: 0, height: 0)
            }
        }
    }
}

// MARK: - Layouts

struct BreakLevel: LayoutValueKey {
    static let defaultValue = 2
}

/// Places atoms left to right on shared baselines. Wraps at natural break points
/// (level 2) first; a term too wide for a line is split at plain spaces (level 1).
/// Glued atoms (level 0) always stay together.
struct MathFlow: Layout {
    var wrap: Bool
    var gap: CGFloat
    var lineGap: CGFloat

    private struct Item { let index: Int; let x: CGFloat; let baseline: CGFloat }
    private struct Row { var items: [Item] = []; var width: CGFloat = 0; var ascent: CGFloat = 0; var descent: CGFloat = 0 }
    private struct Measured { let size: CGSize; let baseline: CGFloat; let level: Int }

    private func rows(maxWidth: CGFloat, subviews: Subviews) -> [Row] {
        let m: [Measured] = subviews.map { view in
            Measured(size: view.sizeThatFits(.unspecified),
                     baseline: view.dimensions(in: .unspecified)[VerticalAlignment.firstTextBaseline],
                     level: view[BreakLevel.self])
        }
        var rows = [Row()]

        func spacing(_ i: Int, startOfRow: Bool) -> CGFloat {
            startOfRow || m[i].level == 0 ? 0 : gap
        }
        func width(_ range: Range<Int>) -> CGFloat {
            range.reduce(0) { $0 + spacing($1, startOfRow: $1 == range.lowerBound) + m[$1].size.width }
        }
        func append(_ range: Range<Int>) {
            for i in range {
                let startOfRow = rows[rows.count - 1].items.isEmpty
                let x = rows[rows.count - 1].width + spacing(i, startOfRow: startOfRow)
                rows[rows.count - 1].items.append(Item(index: i, x: x, baseline: m[i].baseline))
                rows[rows.count - 1].width = x + m[i].size.width
                rows[rows.count - 1].ascent = max(rows[rows.count - 1].ascent, m[i].baseline)
                rows[rows.count - 1].descent = max(rows[rows.count - 1].descent, m[i].size.height - m[i].baseline)
            }
        }
        func groups(_ range: Range<Int>, minLevel: Int) -> [Range<Int>] {
            var out: [Range<Int>] = []
            var start = range.lowerBound
            for i in range where i > range.lowerBound && m[i].level >= minLevel {
                out.append(start..<i)
                start = i
            }
            if start < range.upperBound { out.append(start..<range.upperBound) }
            return out
        }
        func place(_ group: Range<Int>, splitLevel: Int) {
            let row = rows[rows.count - 1]
            let lead = row.items.isEmpty ? 0 : spacing(group.lowerBound, startOfRow: false)
            if !wrap || row.width + lead + width(group) <= maxWidth {
                append(group)
                return
            }
            if !row.items.isEmpty {
                rows.append(Row())
                if width(group) <= maxWidth { append(group); return }
            }
            if splitLevel > 0 {
                for piece in groups(group, minLevel: splitLevel) { place(piece, splitLevel: splitLevel - 1) }
            } else {
                append(group)
            }
        }

        for group in groups(0..<m.count, minLevel: 3) { place(group, splitLevel: 2) }
        return rows
    }

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let rs = rows(maxWidth: proposal.width ?? .infinity, subviews: subviews)
        let width = rs.map(\.width).max() ?? 0
        let height = rs.reduce(0) { $0 + $1.ascent + $1.descent } + lineGap * CGFloat(max(0, rs.count - 1))
        return CGSize(width: width, height: height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var y = bounds.minY
        for row in rows(maxWidth: proposal.width ?? bounds.width, subviews: subviews) {
            for item in row.items {
                subviews[item.index].place(at: CGPoint(x: bounds.minX + item.x, y: y + row.ascent - item.baseline),
                                           anchor: .topLeading, proposal: .unspecified)
            }
            y += row.ascent + row.descent + lineGap
        }
    }

    func explicitAlignment(of guide: VerticalAlignment, in bounds: CGRect, proposal: ProposedViewSize,
                           subviews: Subviews, cache: inout ()) -> CGFloat? {
        let rs = rows(maxWidth: proposal.width ?? bounds.width, subviews: subviews)
        guard let first = rs.first else { return nil }
        if guide == .firstTextBaseline { return bounds.minY + first.ascent }
        if guide == .lastTextBaseline {
            let above = rs.dropLast().reduce(0) { $0 + $1.ascent + $1.descent + lineGap }
            return bounds.minY + above + (rs.last?.ascent ?? 0)
        }
        return nil
    }
}

/// Numerator over a bar over denominator; the baseline sits just below the bar.
struct FractionLayout: Layout {
    var axis: CGFloat
    var gap: CGFloat

    private func measure(_ subviews: Subviews) -> (num: CGSize, bar: CGFloat, den: CGSize, width: CGFloat) {
        let num = subviews[0].sizeThatFits(.unspecified)
        let den = subviews[2].sizeThatFits(.unspecified)
        let bar = subviews[1].sizeThatFits(ProposedViewSize(width: 1, height: nil)).height
        return (num, bar, den, max(num.width, den.width) + 4)
    }

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let m = measure(subviews)
        return CGSize(width: m.width, height: m.num.height + gap + m.bar + gap + m.den.height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let m = measure(subviews)
        subviews[0].place(at: CGPoint(x: bounds.midX, y: bounds.minY), anchor: .top, proposal: .unspecified)
        subviews[1].place(at: CGPoint(x: bounds.minX, y: bounds.minY + m.num.height + gap), anchor: .topLeading,
                          proposal: ProposedViewSize(width: m.width, height: m.bar))
        subviews[2].place(at: CGPoint(x: bounds.midX, y: bounds.minY + m.num.height + gap + m.bar + gap),
                          anchor: .top, proposal: .unspecified)
    }

    func explicitAlignment(of guide: VerticalAlignment, in bounds: CGRect, proposal: ProposedViewSize,
                           subviews: Subviews, cache: inout ()) -> CGFloat? {
        guard guide == .firstTextBaseline || guide == .lastTextBaseline else { return nil }
        let m = measure(subviews)
        return bounds.minY + m.num.height + gap + m.bar / 2 + axis
    }
}

/// Upper limit, integral sign, lower limit stacked and centred.
struct BigOpLayout: Layout {
    var overlap: CGFloat
    var drop: CGFloat

    private func frames(_ subviews: Subviews) -> (upper: CGSize, sign: CGSize, lower: CGSize, width: CGFloat,
                                                  signY: CGFloat, lowerY: CGFloat, height: CGFloat) {
        let upper = subviews[0].sizeThatFits(.unspecified)
        let sign = subviews[1].sizeThatFits(.unspecified)
        let lower = subviews[2].sizeThatFits(.unspecified)
        let signY = upper.height > 0 ? upper.height - overlap : 0
        let lowerY = signY + sign.height - (lower.height > 0 ? overlap : 0)
        let height = max(signY + sign.height, lowerY + lower.height)
        return (upper, sign, lower, max(upper.width, sign.width, lower.width), signY, lowerY, height)
    }

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let f = frames(subviews)
        return CGSize(width: f.width, height: f.height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let f = frames(subviews)
        subviews[0].place(at: CGPoint(x: bounds.midX, y: bounds.minY), anchor: .top, proposal: .unspecified)
        subviews[1].place(at: CGPoint(x: bounds.midX, y: bounds.minY + f.signY), anchor: .top, proposal: .unspecified)
        subviews[2].place(at: CGPoint(x: bounds.midX, y: bounds.minY + f.lowerY), anchor: .top, proposal: .unspecified)
    }

    func explicitAlignment(of guide: VerticalAlignment, in bounds: CGRect, proposal: ProposedViewSize,
                           subviews: Subviews, cache: inout ()) -> CGFloat? {
        guard guide == .firstTextBaseline || guide == .lastTextBaseline else { return nil }
        let f = frames(subviews)
        let signBaseline = subviews[1].dimensions(in: .unspecified)[VerticalAlignment.firstTextBaseline]
        return bounds.minY + f.signY + signBaseline - drop
    }
}
