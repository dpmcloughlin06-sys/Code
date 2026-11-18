import SwiftUI

/// Typesets the plain-text math used in tutor.json into a single `Text`:
///   `Q_x`, `f_avg`       → subscripts (ASCII letters/digits after `_`)
///   `e^(x²)`, `ρ^n`      → superscripts (`^(…)` group or one character)
///   `∫0→1`, `∫α→β`       → integral limits: lower as subscript, upper as superscript
///   `∬D`, `∮C`, `∭E`     → region/curve letter as subscript
/// Everything else is drawn as-is. Wrapping still works because the result is one Text.
enum MathText {
    private static let integralSigns: Set<Character> = ["∫", "∬", "∭", "∮"]

    static func render(_ source: String, size: CGFloat, weight: Font.Weight = .regular,
                       design: Font.Design = .rounded) -> Text {
        let base = Font.system(size: size, weight: weight, design: design)
        let small = Font.system(size: (size * 0.66).rounded(), weight: weight, design: design)
        let chars = Array(source)
        var result = Text("")
        var plain = ""
        var i = 0

        func flush() {
            guard !plain.isEmpty else { return }
            result = result + Text(plain).font(base)
            plain = ""
        }
        func sub(_ s: String) {
            guard !s.isEmpty else { return }
            flush()
            result = result + Text(s).font(small).baselineOffset(-size * 0.2)
        }
        func sup(_ s: String) {
            guard !s.isEmpty else { return }
            flush()
            result = result + Text(s).font(small).baselineOffset(size * 0.42)
        }
        func isWordChar(_ c: Character) -> Bool { c.isASCII && (c.isLetter || c.isNumber) }

        while i < chars.count {
            let c = chars[i]

            // Integral signs: limits written as ∫lower→upper, or a region letter ∬D.
            if integralSigns.contains(c) {
                plain.append(c)
                var j = i + 1
                while j < chars.count, !chars[j].isWhitespace { j += 1 }
                let token = String(chars[(i + 1)..<j])
                if let arrow = token.firstIndex(of: "→") {
                    sub(String(token[..<arrow]))
                    sup(String(token[token.index(after: arrow)...]))
                    i = j
                    continue
                }
                if token.count == 1, let letter = token.first, letter.isUppercase {
                    sub(token)
                    i = j
                    continue
                }
                i += 1
                continue
            }

            // Subscript: x_y where the underscore follows a non-space character.
            if c == "_", i > 0, !chars[i - 1].isWhitespace, i + 1 < chars.count, isWordChar(chars[i + 1]) {
                var j = i + 1
                while j < chars.count, isWordChar(chars[j]) { j += 1 }
                sub(String(chars[(i + 1)..<j]))
                i = j
                continue
            }

            // Superscript: ^(group) or ^c.
            if c == "^", i + 1 < chars.count {
                if chars[i + 1] == "(", let close = closingParen(chars, from: i + 1) {
                    sup(String(chars[(i + 2)..<close]))
                    i = close + 1
                    continue
                }
                if !chars[i + 1].isWhitespace {
                    sup(String(chars[i + 1]))
                    i += 2
                    continue
                }
            }

            plain.append(c)
            i += 1
        }
        flush()
        return result
    }

    private static func closingParen(_ chars: [Character], from open: Int) -> Int? {
        var depth = 0
        var k = open
        while k < chars.count {
            if chars[k] == "(" { depth += 1 }
            if chars[k] == ")" {
                depth -= 1
                if depth == 0 { return k }
            }
            k += 1
        }
        return nil
    }
}
