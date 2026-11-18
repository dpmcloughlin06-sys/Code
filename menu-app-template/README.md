# Menu-tree app template

Build a "pick a type → key facts → process" reference app for **any subject**
on **any device**. All content lives in one JSON file; small renderers display
it on a watch, phone, desktop browser or terminal.

| Renderer | Runs on | Start it |
|---|---|---|
| `renderers/web/index.html` | any browser (iOS, Android, Windows, macOS, Linux) | `python3 tools/menutree.py export-web content/tree.json app.html`, then open `app.html` |
| `renderers/cli/menu.py` | any terminal | `python3 renderers/cli/menu.py content/tree.json` |
| `renderers/swiftui/` | Apple Watch (Swift files fit iOS 17+ too) | open `MenuApp.xcodeproj` in Xcode 16+, pick your Team, Run |

## Make your own

1. Copy `content/example_tree.py` and replace the example (a Git quick
   reference) with your subject. Each `t.node(...)` call is one screen.
2. Run it: `python3 content/your_tree.py`. It checks every link and writes
   `content/tree.json`.
3. Run `python3 tests/run_tests.py`.

Screen fields: `title`, `tag`, `highlight` (formulas or commands), `body`,
`steps`, `caution`, `choices`. The full format is in [SPEC.md](SPEC.md);
coding agents should start with [CLAUDE.md](CLAUDE.md).
