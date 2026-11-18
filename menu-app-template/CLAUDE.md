# Menu-tree app template: guide for coding agents

Read this first, then `SPEC.md`. That's enough to work here.

## What this is

A reusable pattern for "pick a type, then read the key facts and process"
apps, on any subject, OS or device.

- **Content** is one JSON file, `content/tree.json`, of screens (`nodes`)
  linked by buttons (`choices`).
- **Renderers** draw that file. Three reference renderers are included; any
  platform can get a new one by following SPEC.md §3.

Origin: this generalizes the `Calc3Tutor/` watch app at the repo root, a real
instance. Its field names differ: `formula` → `highlight`, `warn` → `caution`.

## Map

```
content/example_tree.py   AUTHORING SOURCE (edit this). Builds + validates, writes tree.json and its copies
content/tree.json         GENERATED. The single data file renderers read. Don't hand-edit if a .py source exists
tools/menutree.py         library (Tree, validate, export_web) + CLI: validate | stats | export-web
schema/tree.schema.json   JSON Schema for tree.json (per-node shape; validator covers links/reachability)
SPEC.md                   format + rendering contract. The source of truth
renderers/web/            index.html: any browser (phone/tablet/desktop). Embeds JSON or fetches tree.json
renderers/cli/menu.py     any terminal with Python 3.8+
renderers/swiftui/        Apple: watchOS project MenuApp.xcodeproj; MenuApp/*.swift + bundled tree.json
tests/run_tests.py        run after ANY change (no deps; uses jsonschema if installed)
tests/web_smoke.js        browser test (needs Node + Playwright)
```

Copies of `tree.json` live in `renderers/web/` and `renderers/swiftui/MenuApp/`
because those renderers bundle their data. The authoring script writes all
copies; tests fail if they drift.

## Invariants (don't break these)

1. Node keys are exactly: `id, title, tag, highlight, body, steps, caution, choices`.
2. Ids are `^[a-z0-9_]+$`, unique; every `next` exists; every node is reachable from `root`.
3. Text is plain (no Markdown or HTML); `\n` is a line break.
4. Render order: title → highlight → body → steps → caution → choices (or Home).
5. A format change updates SPEC.md, the schema, `NODE_KEYS` in menutree.py and every renderer together.

## Recipes

**New subject or app**
1. `cp content/example_tree.py content/<subject>_tree.py`, then replace the `Tree(...)` name, subject and nodes.
2. Keep `t.write(OUT, copies=COPIES, profile="<watch|phone|desktop>")` at the end.
3. `python3 content/<subject>_tree.py && python3 tests/run_tests.py`

**Typical shape** (what worked for the Calc 3 instance)
- `root`: a list of problem or task types (choices only).
- Each type: `highlight` = every formula or command, `steps` = 2–4 short lines, `caution` = the classic mistake, optional `choices` to sub-screens (tables, examples).
- A separate "★ Tips & rules" branch for cross-cutting shortcuts.
- Keep it high level: users want the facts, not a lecture.

**Add or edit a screen:** add `t.node(...)` in the authoring script and link to it from some `choices`. Rebuild.

**Port to a new platform** (Android/Compose, Flutter, React Native, Wear OS, Qt, TUI…)
1. Create `renderers/<platform>/`.
2. Load `tree.json` (bundle it as an asset and add the path to `COPIES` in the authoring script).
3. Map the node fields to UI per SPEC.md §3: a navigation stack of node ids, Back, Home.
4. Use `renderers/swiftui/MenuApp/NodeView.swift` or `renderers/web/index.html` as the model; both are ~150 lines.
5. Add a smoke test, and add a CI step if the platform can build headless.

**Ship the web version as one file:** `python3 tools/menutree.py export-web content/tree.json app.html`, which works from `file://`.

**Rename the Apple app:** change `INFOPLIST_KEY_CFBundleDisplayName` and `PRODUCT_BUNDLE_IDENTIFIER` in `renderers/swiftui/MenuApp.xcodeproj/project.pbxproj`. For iPhone instead of Watch, set `SDKROOT = iphoneos`, `TARGETED_DEVICE_FAMILY = 1`, remove `INFOPLIST_KEY_WKWatchOnly`, and set `IPHONEOS_DEPLOYMENT_TARGET = 17.0`. The Swift files are shared, but the iOS build hasn't been tried.

## Commands

```sh
python3 content/example_tree.py                                 # build + validate + write copies
python3 tools/menutree.py validate content/tree.json --profile watch
python3 tools/menutree.py stats content/tree.json
python3 tests/run_tests.py                                      # always
node tests/web_smoke.js                                         # if Playwright is available
python3 renderers/cli/menu.py content/tree.json                 # try it in a terminal
cd renderers/web && python3 -m http.server                      # try it in a browser
```

CI (`.github/workflows/build.yml` at the repo root) runs the tests and builds
the SwiftUI app for watchOS on macOS.
