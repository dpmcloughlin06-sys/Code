#!/usr/bin/env python3
"""Template self-test. Run from anywhere:  python3 tests/run_tests.py
Checks: content is built and copies match, validator accepts good / rejects bad trees,
schema agrees (if `jsonschema` is installed), CLI renderer navigates, web export embeds safely.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import menutree  # noqa: E402

TREE = os.path.join(ROOT, "content", "tree.json")
COPIES = [os.path.join(ROOT, "renderers", "web", "tree.json"),
          os.path.join(ROOT, "renderers", "swiftui", "MenuApp", "tree.json")]
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


data = load(TREE)

# 1. built content is current and every renderer copy is identical
for p in COPIES:
    with open(p, encoding="utf-8") as a, open(TREE, encoding="utf-8") as b:
        check(f"copy matches: {os.path.relpath(p, ROOT)}", a.read() == b.read())

# 2. validator: good tree passes, each broken variant fails with the expected message
errs, _ = menutree.validate(data, "watch")
check("example tree valid", not errs, errs)


def broken(mutate, expect):
    d = copy.deepcopy(data)
    mutate(d)
    e, _ = menutree.validate(d)
    check(f"rejects: {expect}", any(expect in x for x in e), e)


broken(lambda d: d["nodes"][0]["choices"].append({"label": "x", "next": "nope"}), "missing node")
broken(lambda d: d["nodes"].append({"id": "orphan", "title": "O", "body": "b"}), "unreachable")
broken(lambda d: d["nodes"].append(copy.deepcopy(d["nodes"][1])), "duplicate id")
broken(lambda d: d["nodes"].append({"id": "Bad-Id", "title": "x", "body": "b"}), "id must match")
broken(lambda d: d["nodes"][1].update({"colour": "red"}), "unknown keys")
broken(lambda d: d.update({"root": "nowhere"}), "root")
broken(lambda d: d["nodes"][-1].pop("highlight", None) or d["nodes"][-1].pop("body", None), "empty screen")
broken(lambda d: d["nodes"][1].update({"steps": []}), "steps must be")

# 3. JSON Schema agrees with the validator (optional dependency)
try:
    import jsonschema
    schema = load(os.path.join(ROOT, "schema", "tree.schema.json"))
    jsonschema.validate(data, schema)
    check("schema accepts example", True)
    bad = copy.deepcopy(data)
    bad["nodes"][1]["colour"] = "red"
    try:
        jsonschema.validate(bad, schema)
        check("schema rejects unknown key", False, "accepted")
    except jsonschema.ValidationError:
        check("schema rejects unknown key", True)
except ImportError:
    print("SKIP schema checks (pip install jsonschema)")

# 4. CLI renderer: go into the first choice, back, into it again, home, quit
cli = os.path.join(ROOT, "renderers", "cli", "menu.py")
out = subprocess.run([sys.executable, cli, TREE], input="1\nb\n1\nh\nq\n",
                     capture_output=True, text=True, timeout=20).stdout
first = data["nodes"][0]["choices"][0]
first_title = next(n["title"] for n in data["nodes"] if n["id"] == first["next"])
root_title = data["nodes"][0]["title"]
check("cli shows root", root_title in out)
check("cli opens first choice", first_title in out)
check("cli back/home return to root", out.count(root_title) == 3, f"count={out.count(root_title)}")

# 5. web export embeds the tree and can't break out of its <script> tag
with tempfile.TemporaryDirectory() as tmp:
    d = copy.deepcopy(data)
    d["nodes"][1]["body"] = (d["nodes"][1].get("body") or "") + " </script><b>x</b>"
    src = os.path.join(tmp, "t.json")
    with open(src, "w", encoding="utf-8") as f:
        json.dump(d, f)
    outp = os.path.join(tmp, "app.html")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "menutree.py"), "export-web", src, outp],
                       capture_output=True, text=True)
    html = open(outp, encoding="utf-8").read() if r.returncode == 0 else ""
    check("export-web writes file", r.returncode == 0, r.stdout + r.stderr)
    check("export-web escapes </script>", html.count("</script>") == 2, f"count={html.count('</script>')}")

print(f"\n{'ALL PASSED' if not failures else str(len(failures)) + ' FAILED'}")
sys.exit(1 if failures else 0)
