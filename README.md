# Calc3 Tutor (Apple Watch)

A watch-only SwiftUI quick reference for MATH 2630 Exam 3 (15.1–15.3,
15.5–15.8, 16.2–16.5). Pick a problem type, get every equation for it plus a
short process. A separate **Tricks & rules** menu holds shortcuts.

## Run it

1. On a Mac with Xcode 16 or newer, open `Calc3Tutor.xcodeproj`.
2. Select the **Calc3Tutor** target → *Signing & Capabilities* → pick your Team.
   Change the bundle ID if Xcode says it's taken.
3. Choose an Apple Watch simulator (or your paired watch) and press Run.

Requires watchOS 10+. If the project file won't open, create a new
*watchOS → App* project (watch-only), delete its `ContentView.swift` and app
file, and drag in the contents of `Calc3Tutor/`, making sure `tutor.json` is
checked for the target.

## How it works

- Opens on **Problem type**: 15 types, then **★ Tricks & rules** and a
  **Practice exam Q1–40** map at the bottom.
- Each type screen: equations (blue box), a 2–4 line process, the one
  mistake to avoid, and submenus (bounds tables, conversions, examples).
- Tricks & rules: symmetry, choosing/swapping order, known areas & volumes,
  trig identities & values, u-sub patterns, by parts, line integral rules,
  sanity checks.
- The house button returns to Problem type.

`Calc3Tutor/tutor.json` holds the 41 screens.

## Editing content

Don't edit `tutor.json` by hand. Edit `tools/build_tree.py`, then:

```sh
python3 tools/build_tree.py        # rebuilds tutor.json; fails on broken links / unreachable screens
python3 tools/verify_examples.py   # checks examples and formulas with SymPy (pip install sympy)
```

## Reusable template

`menu-app-template/` generalizes this app's structure to any subject, OS and
device: one `tree.json` data file, a spec, a validator, and web, terminal and
SwiftUI renderers. Start with `menu-app-template/CLAUDE.md`.
