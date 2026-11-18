#!/usr/bin/env python3
"""menutree: author, validate and export menu-tree apps. Standard library only.

The format is defined in ../SPEC.md. Summary:
  tree.json = {"schemaVersion": 1, "app": {...}, "root": "<id>", "nodes": [node, ...]}
  node      = {"id", "title", optional "tag", "highlight", "body", "steps", "caution", "choices"}

Library use (from an authoring script):
    from menutree import Tree
    t = Tree(name="My App", subject="anything")
    t.node("root", "Home", choices=[("First topic", "topic1")])
    t.node("topic1", "First topic", highlight="key fact", steps=["do this", "then this"])
    t.write("content/tree.json", copies=["renderers/web/tree.json"])

Command line:
    python3 tools/menutree.py validate content/tree.json [--profile watch|phone|desktop]
    python3 tools/menutree.py stats content/tree.json
    python3 tools/menutree.py export-web content/tree.json out.html
"""
import argparse
import json
import os
import re
import sys
import textwrap

SCHEMA_VERSION = 1
ID_RE = re.compile(r"^[a-z0-9_]+$")
NODE_KEYS = {"id", "title", "tag", "highlight", "body", "steps", "caution", "choices"}
TEXT_FIELDS = ("highlight", "body", "caution")
CONTENT_FIELDS = ("highlight", "body", "steps", "choices")

# Soft length limits per device class. Exceeding one is a warning, not an error.
PROFILES = {
    "watch":   {"title": 40, "label": 45, "text": 600, "step": 200, "choices": 20},
    "phone":   {"title": 60, "label": 80, "text": 1500, "step": 400, "choices": 40},
    "desktop": {"title": 120, "label": 160, "text": 6000, "step": 1000, "choices": 100},
}

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_TEMPLATE = os.path.join(HERE, "..", "renderers", "web", "index.html")
DATA_TAG_RE = re.compile(r'(<script id="tree-data" type="application/json">)(.*?)(</script>)', re.S)


def _clean(text):
    """Dedent a multi-line string and trim blank edges, so authors can indent freely."""
    return textwrap.dedent(text).strip("\n") if isinstance(text, str) else text


class Tree:
    """Builds a tree.json document node by node, in the order nodes are added."""

    def __init__(self, name, subject, root="root", description="", highlight_font="default"):
        self.app = {"name": name, "subject": subject, "highlightFont": highlight_font}
        if description:
            self.app["description"] = description
        self.root = root
        self.nodes = {}

    def node(self, id, title, tag=None, highlight=None, body=None, steps=None,
             caution=None, choices=None):
        if id in self.nodes:
            raise ValueError(f"duplicate node id: {id}")
        n = {"id": id, "title": title}
        if tag:
            n["tag"] = tag
        if highlight:
            n["highlight"] = _clean(highlight)
        if body:
            n["body"] = _clean(body)
        if steps:
            n["steps"] = [_clean(s) for s in steps]
        if caution:
            n["caution"] = _clean(caution)
        if choices:
            n["choices"] = [{"label": label, "next": nxt} for label, nxt in choices]
        self.nodes[id] = n
        return n

    def to_dict(self):
        return {"schemaVersion": SCHEMA_VERSION, "app": self.app, "root": self.root,
                "nodes": list(self.nodes.values())}

    def write(self, path, copies=(), profile=None):
        """Validate, then write tree.json to `path` and identical copies. Exits on errors."""
        data = self.to_dict()
        errors, warnings = validate(data, profile)
        for w in warnings:
            print("warning:", w, file=sys.stderr)
        if errors:
            for e in errors:
                print("error:", e, file=sys.stderr)
            sys.exit(1)
        text = dumps(data)
        for p in (path, *copies):
            os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
        print(f"OK: {len(data['nodes'])} screens → {path}" + (f" (+{len(copies)} copies)" if copies else ""))


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def validate(data, profile=None):
    """Return (errors, warnings). Errors break the contract in SPEC.md; warnings are style."""
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ["top level must be an object"], []
    if data.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}")
    app = data.get("app")
    if not isinstance(app, dict) or not isinstance(app.get("name"), str) or not app["name"]:
        errors.append("app.name must be a non-empty string")
    elif app.get("highlightFont", "default") not in ("default", "monospaced"):
        errors.append("app.highlightFont must be 'default' or 'monospaced'")
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return errors + ["nodes must be a non-empty array"], warnings

    ids = {}
    for i, n in enumerate(nodes):
        where = f"nodes[{i}]"
        if not isinstance(n, dict):
            errors.append(f"{where}: must be an object")
            continue
        nid = n.get("id")
        if not isinstance(nid, str) or not ID_RE.match(nid):
            errors.append(f"{where}: id must match {ID_RE.pattern}")
            continue
        where = nid
        if nid in ids:
            errors.append(f"{nid}: duplicate id")
        ids[nid] = n
        extra = set(n) - NODE_KEYS
        if extra:
            errors.append(f"{nid}: unknown keys {sorted(extra)}")
        if not isinstance(n.get("title"), str) or not n["title"].strip():
            errors.append(f"{nid}: title must be a non-empty string")
        for k in ("tag",) + TEXT_FIELDS:
            if k in n and (not isinstance(n[k], str) or not n[k].strip()):
                errors.append(f"{nid}: {k} must be a non-empty string when present")
        if "steps" in n and (not isinstance(n["steps"], list) or not n["steps"]
                             or not all(isinstance(s, str) and s.strip() for s in n["steps"])):
            errors.append(f"{nid}: steps must be a non-empty array of non-empty strings")
        if "choices" in n:
            ch = n["choices"]
            if not isinstance(ch, list) or not ch:
                errors.append(f"{nid}: choices must be a non-empty array")
            else:
                for c in ch:
                    if not (isinstance(c, dict) and set(c) == {"label", "next"}
                            and isinstance(c["label"], str) and c["label"].strip()
                            and isinstance(c["next"], str)):
                        errors.append(f"{nid}: each choice needs exactly a non-empty label and a next")
        if not any(n.get(k) for k in CONTENT_FIELDS):
            errors.append(f"{nid}: empty screen (needs highlight, body, steps or choices)")

    root = data.get("root")
    if root not in ids:
        errors.append(f"root '{root}' is not a node id")
    for nid, n in ids.items():
        for c in n.get("choices") or []:
            if isinstance(c, dict) and c.get("next") not in ids:
                errors.append(f"{nid}: choice '{c.get('label')}' links to missing node '{c.get('next')}'")

    if root in ids:
        seen, stack = set(), [root]
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in ids:
                continue
            seen.add(cur)
            stack += [c.get("next") for c in ids[cur].get("choices") or [] if isinstance(c, dict)]
        for nid in ids:
            if nid not in seen:
                errors.append(f"{nid}: unreachable from root")

    if profile:
        lim = PROFILES[profile]
        for nid, n in ids.items():
            if len(n.get("title", "")) > lim["title"]:
                warnings.append(f"{nid}: title longer than {lim['title']} chars for {profile}")
            for k in TEXT_FIELDS:
                if len(n.get(k) or "") > lim["text"]:
                    warnings.append(f"{nid}: {k} longer than {lim['text']} chars for {profile}")
            for s in n.get("steps") or []:
                if isinstance(s, str) and len(s) > lim["step"]:
                    warnings.append(f"{nid}: a step is longer than {lim['step']} chars for {profile}")
            ch = n.get("choices") or []
            if len(ch) > lim["choices"]:
                warnings.append(f"{nid}: {len(ch)} choices; {profile} suggests ≤ {lim['choices']}")
            for c in ch:
                if isinstance(c, dict) and len(c.get("label", "")) > lim["label"]:
                    warnings.append(f"{nid}: choice label longer than {lim['label']} chars for {profile}")
    return errors, warnings


def export_web(data, out_path, template_path=WEB_TEMPLATE):
    """Write a single self-contained HTML file with the tree embedded (works from file://)."""
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html, count = DATA_TAG_RE.subn(lambda m: m.group(1) + payload + m.group(3), html, count=1)
    if count != 1:
        raise SystemExit("web template is missing <script id=\"tree-data\" type=\"application/json\">")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check a tree.json against SPEC.md")
    v.add_argument("file")
    v.add_argument("--profile", choices=sorted(PROFILES))
    s = sub.add_parser("stats", help="count screens, steps, choices")
    s.add_argument("file")
    w = sub.add_parser("export-web", help="write a standalone HTML app")
    w.add_argument("file")
    w.add_argument("out")
    a = ap.parse_args(argv)

    data = _load(a.file)
    if a.cmd == "validate":
        errors, warnings = validate(data, a.profile)
        for w_ in warnings:
            print("warning:", w_)
        for e in errors:
            print("error:", e)
        print("OK" if not errors else f"{len(errors)} error(s)")
        return 1 if errors else 0
    if a.cmd == "stats":
        nodes = data["nodes"]
        print(f"screens: {len(nodes)}")
        print(f"menus (have choices): {sum(1 for n in nodes if n.get('choices'))}")
        print(f"end screens: {sum(1 for n in nodes if not n.get('choices'))}")
        print(f"screens with steps: {sum(1 for n in nodes if n.get('steps'))}")
        return 0
    if a.cmd == "export-web":
        errors, _ = validate(data)
        if errors:
            print("\n".join("error: " + e for e in errors))
            return 1
        export_web(data, a.out)
        print(f"wrote {a.out}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
