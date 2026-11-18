# Calc3 Tutor (Apple Watch)

A watch-only SwiftUI app that walks you through MATH 2630 Exam 3 problems
(15.1–15.3, 15.5–15.8, 16.2–16.5). It asks short questions to narrow down the
problem type, then gives the exact setup: bounds, Jacobian, formula, steps,
the common mistake to avoid, and a worked example. You do the arithmetic.

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

- `Calc3Tutor/tutor.json` is the decision tree (121 screens). Each screen has a
  title, body, optional formula, optional warning, and either choices
  (narrowing questions), a Next button, or a finish screen.
- The house button returns to the start; the back chevron retraces your path.
- Root menu: **Solve a problem** (guided), **Jump to a topic**, **Formula
  sheet**, **Integration toolkit**, **Final answer check**.

## Editing content

Don't edit `tutor.json` by hand. Edit `tools/build_tree.py`, then:

```sh
python3 tools/build_tree.py        # rebuilds tutor.json; fails on broken links / unreachable screens
python3 tools/verify_examples.py   # checks every worked example with SymPy (pip install sympy)
```
