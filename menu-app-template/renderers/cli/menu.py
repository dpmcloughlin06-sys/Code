#!/usr/bin/env python3
"""Terminal renderer for a menu-tree app (see ../../SPEC.md). Any OS with Python 3.8+.

    python3 renderers/cli/menu.py content/tree.json

Type a choice number, b = back, h = home, q = quit. Reads stdin, so it can be scripted:
    printf '1\nb\nq\n' | python3 renderers/cli/menu.py content/tree.json
"""
import json
import shutil
import sys
import textwrap


def wrap(text, width, indent=""):
    out = []
    for line in text.split("\n"):
        out.extend(textwrap.wrap(line, width, initial_indent=indent, subsequent_indent=indent) or [indent])
    return "\n".join(out)


def render(node, tree, is_root, width):
    rule = "─" * min(width, 60)
    lines = [rule]
    tag = node.get("tag") or (tree["app"]["name"] if is_root else "")
    if tag:
        lines.append(tag.upper())
    lines.append(node["title"])
    lines.append(rule)
    # Rendering order fixed by SPEC.md: title, highlight, body, steps, caution, choices.
    if node.get("highlight"):
        lines.append(wrap(node["highlight"], width - 2, "│ "))
    if node.get("body"):
        lines.append(wrap(node["body"], width))
    for i, step in enumerate(node.get("steps") or [], 1):
        first, *rest = wrap(step, width - 4).split("\n")
        lines.append(f"{i:>2}. {first}")
        lines.extend("    " + r for r in rest)
    if node.get("caution"):
        lines.append(wrap("⚠ " + node["caution"], width))
    choices = node.get("choices") or []
    for i, c in enumerate(choices, 1):
        lines.append(f"  [{i}] {c['label']}")
    keys = (["number"] if choices else []) + ([] if is_root else ["b back", "h home"]) + ["q quit"]
    lines.append("> " + ", ".join(keys))
    return "\n".join(lines)


def main(path):
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)
    by_id = {n["id"]: n for n in tree["nodes"]}
    stack = [tree["root"]]
    width = max(40, min(shutil.get_terminal_size((80, 24)).columns, 100))
    while True:
        node = by_id[stack[-1]]
        print(render(node, tree, len(stack) == 1, width))
        line = sys.stdin.readline()
        if not line:  # EOF
            return 0
        cmd = line.strip().lower()
        choices = node.get("choices") or []
        if cmd == "q":
            return 0
        if cmd == "b" and len(stack) > 1:
            stack.pop()
        elif cmd == "h":
            del stack[1:]
        elif cmd.isdigit() and 1 <= int(cmd) <= len(choices):
            stack.append(choices[int(cmd) - 1]["next"])
        else:
            print("? not a valid choice")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
