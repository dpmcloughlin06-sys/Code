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

Work the problem on paper with the watch beside you.

1. Home has three buttons: **Practice exam question #** (pick a section, then
   your question), **Describe my problem** (a few narrowing questions), and
   **Reference** (formula sheet, integration toolkit, final check).
2. Procedures are step-by-step: one step shows in large text. Do it, tap
   **Done** (haptic click), and the next step appears. Earlier steps shrink with
   a check mark. "Show all steps" reveals the rest at once.
3. After the last step you get the worked example (if any) and the next choice.
4. The house button returns home; the back chevron retraces your path.

`Calc3Tutor/tutor.json` is the decision tree (139 screens, 24 step-by-step).

## Editing content

Don't edit `tutor.json` by hand. Edit `tools/build_tree.py`, then:

```sh
python3 tools/build_tree.py        # rebuilds tutor.json; fails on broken links / unreachable screens
python3 tools/verify_examples.py   # checks every worked example with SymPy (pip install sympy)
```
