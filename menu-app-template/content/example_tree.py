#!/usr/bin/env python3
"""Example content: a Git quick reference. Copy this file to start a new subject.

Run from the template root:
    python3 content/example_tree.py
It validates the tree and writes content/tree.json plus a copy for each renderer
that bundles its data (see COPIES).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from menutree import Tree  # noqa: E402

OUT = os.path.join(ROOT, "content", "tree.json")
COPIES = [
    os.path.join(ROOT, "renderers", "web", "tree.json"),
    os.path.join(ROOT, "renderers", "swiftui", "MenuApp", "tree.json"),
]

t = Tree(
    name="Git Quick Ref",
    subject="Git version control",
    description="Commands and processes for everyday Git work.",
    highlight_font="monospaced",  # commands read better in monospace; use "default" for math/prose
)

# ---------------------------------------------------------------- home: pick a task type
t.node("root", "What are you doing?", tag="Git",
       choices=[
           ("Start a repository", "start"),
           ("Save work (commit)", "commit"),
           ("Branches", "branches"),
           ("Sync with a remote", "remote"),
           ("Undo something", "undo"),
           ("★ Tips & rules", "tips"),
       ])

# ---------------------------------------------------------------- task screens
t.node("start", "Start a repository", tag="Setup",
       highlight="""
           git init
           git clone <url>
           git config --global user.name "Name"
           git config --global user.email "you@example.com"
       """,
       steps=["New project: git init in its folder.",
              "Existing project online: git clone <url>.",
              "Set name and email once per machine."])

t.node("commit", "Save work", tag="Commit",
       highlight="""
           git status
           git add <file>    (-A = all)
           git commit -m "message"
           git log --oneline
       """,
       steps=["Check what changed: git status.",
              "Stage what belongs together.",
              "Commit with a message that says why."],
       caution="Commit small, related changes. One idea per commit.")

t.node("branches", "Branches", tag="Branch",
       highlight="""
           git switch -c <name>    new + switch
           git switch <name>       switch
           git merge <name>        into current
           git branch -d <name>    delete merged
       """,
       steps=["Branch before starting a change.",
              "Commit on the branch.",
              "Switch to the target branch, then merge."],
       choices=[("Merge conflict?", "conflict")])

t.node("conflict", "Merge conflict", tag="Branch",
       steps=["Open each file git status lists as conflicted.",
              "Keep the right lines between <<<<<<< and >>>>>>>, delete the markers.",
              "git add <file> for each, then git commit."],
       caution="git merge --abort returns to before the merge.")

t.node("remote", "Sync with a remote", tag="Remote",
       highlight="""
           git remote -v
           git fetch
           git pull
           git push -u origin <branch>
       """,
       body="fetch downloads without changing your files; pull = fetch + merge.",
       caution="Pull before you push to avoid a rejected push.")

# ---------------------------------------------------------------- submenu with end screens
t.node("undo", "Undo what?", tag="Undo",
       choices=[
           ("Unstage a file", "undo_unstage"),
           ("Discard edits to a file", "undo_discard"),
           ("Fix the last commit", "undo_amend"),
           ("Undo a pushed commit", "undo_revert"),
       ])
t.node("undo_unstage", "Unstage a file", tag="Undo",
       highlight="git restore --staged <file>",
       body="The edits stay in the file; only the staging is undone.")
t.node("undo_discard", "Discard edits", tag="Undo",
       highlight="git restore <file>",
       caution="Uncommitted edits are lost for good.")
t.node("undo_amend", "Fix the last commit", tag="Undo",
       highlight='git commit --amend -m "new message"',
       body="Stage forgotten files first; they join the last commit.",
       caution="Only before pushing: amending rewrites history.")
t.node("undo_revert", "Undo a pushed commit", tag="Undo",
       highlight="git revert <sha>",
       body="Makes a new commit that reverses the old one. Safe on shared branches.")

# ---------------------------------------------------------------- tips menu (separate from tasks)
t.node("tips", "Tips & rules", tag="Tips",
       choices=[("Habits", "tips_habits"), ("Reading history", "tips_history")])
t.node("tips_habits", "Habits", tag="Tips",
       body="""
           Run git status before and after anything.
           Never commit secrets; list them in .gitignore.
           Don't rewrite history others have pulled.
       """)
t.node("tips_history", "Reading history", tag="Tips",
       highlight="""
           git log --oneline --graph
           git show <sha>
           git diff            unstaged
           git diff --staged   staged
       """)

if __name__ == "__main__":
    t.write(OUT, copies=COPIES, profile="watch")
