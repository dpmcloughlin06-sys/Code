# Menu-tree app specification (schemaVersion 1)

A menu-tree app is a set of screens joined by buttons. Every screen and every
button lives in **one data file, `tree.json`**. A *renderer* draws that file on
some device. The subject, operating system, device and UI toolkit are all
open: content authors only touch the data, and renderer authors only follow
§3.

## 1. File format

```jsonc
{
  "schemaVersion": 1,
  "app": {
    "name": "Git Quick Ref",            // required: display name
    "subject": "Git version control",   // optional, informational
    "description": "One sentence.",     // optional, informational
    "highlightFont": "monospaced"       // optional: "default" (math/prose) | "monospaced" (code/commands)
  },
  "root": "root",                       // id of the home screen
  "nodes": [ /* screens, any order; authoring order is kept */ ]
}
```

### Node (one screen)

| key | type | required | meaning |
|---|---|---|---|
| `id` | string `^[a-z0-9_]+$` | yes | unique id; the target of `choices[].next` |
| `title` | text | yes | screen heading |
| `tag` | text | no | short section label (nav bar, breadcrumb) |
| `highlight` | text | no | key facts block: equations, commands, values. Emphasized |
| `body` | text | no | explanatory text |
| `steps` | text[] | no | ordered process, shown as a numbered list |
| `caution` | text | no | the one mistake to avoid, shown as a warning |
| `choices` | `{label, next}[]` | no | buttons to other screens, in order |

A node must have at least one of `highlight`, `body`, `steps`, `choices`. No
other keys are allowed.

**Text** is plain Unicode: no Markdown, no HTML, no escapes for display. `\n`
is a line break, and renderers keep line breaks and leading spaces (alignment
in `highlight` matters). Use Unicode for math (∫ ∬ √ π θ ² ≤ →).

## 2. Structural rules (checked by `tools/menutree.py validate`)

1. Ids are unique; `root` is an id.
2. Every `choices[].next` is an id.
3. Every node is reachable from `root`.
4. No empty screens (see above).
5. Cycles are allowed (e.g. "Back to menu"), but usually unnecessary because §3
   gives Back and Home.

Soft limits per device class (`--profile watch|phone|desktop`) produce
**warnings** only: title, choice label, text and step length, and number of
choices. They are listed in `PROFILES` in `tools/menutree.py`.

## 3. Rendering contract (every renderer must do this)

**Screen layout, top to bottom, skipping absent fields:**

1. `title`
2. `highlight`: visually distinct block (tint, border or box). Monospaced if
   `app.highlightFont == "monospaced"`. Keep whitespace.
3. `body`
4. `steps`: numbered 1..n
5. `caution`: warning style (icon or colour)
6. `choices`: one tappable or selectable control per choice, in order, showing
   `label`
7. If there are no `choices` and this is not the root: a **Home** control

`tag` goes in the chrome (nav bar or header), not the content. On the root,
renderers may show `app.name` there instead.

**Navigation:**

- Choosing a choice pushes `next` onto a stack.
- **Back** pops one level. On the root there is no Back.
- **Home** clears the stack to `root`, from any screen.
- Screens hold no state. Rendering a node depends only on the node and `app`.

**Robustness:**

- An unknown `next` at runtime shows a "missing screen" message instead of
  crashing. The validator prevents this, but it's cheap insurance.
- Insert text as text, never as markup (e.g. `textContent`, not `innerHTML`).

## 4. Versioning

Change `schemaVersion` only for breaking changes. Optional new keys need a
spec update, a schema update, a validator update (`NODE_KEYS`) and a renderer
update, all in one change.
