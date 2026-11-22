#!/usr/bin/env python3
"""Copilot Task Monitor. Copy this source to .github/skills/task/task.py.
Use an existing Python 3.9+ and Git 2.43+ from your project. Built-in transfers
use local files. All modules below are Python standard library modules.
"""
# MIT License

# Copyright (c) 2026 Copilot Task Monitor contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import date, datetime, timedelta, timezone
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from pathlib import Path, PurePosixPath
import argparse
import contextlib
import fnmatch
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import uuid

SCRIPT_REL = ".github/skills/task/task.py"
GUIDE_REL = ".github/skills/task/SKILL.md"
EDITION_DIGEST = "65b5b97d24bc3f19f98c881368dfc1dc9384a319432c45a24ac91a901e6ce270"

GUIDE_TEXT = r'''---
name: task
description: Maintain engineering task plans, handoffs, Git checkpoints, task switches, fresh-chat resumes, recovery and weekly outcome reports. Use for project coding, investigation, decisions, context changes and progress questions.
---

# Task Monitor

Use ordinary language in chat. This workflow applies in the existing engineering agent and the optional Task Monitor agent. The session that knows the work writes its own handoff. In the command examples below, RUN means the project's existing Python 3.9+ launcher followed by `.github/skills/task/task.py` from the repository root. Use `python`, `python3` or `py -3` as appropriate. Git 2.43+ is required. Terminal and workspace editing permissions apply.

## Starting and resuming

- For a coding task, identify the matching record in `.tasks/INDEX.md`. Create it if necessary. A read-only question can use the records that already exist without initializing anything.
- Create a task with `RUN new "TITLE" --request "original request" --criterion "observable success" --step "first step"`. Repeat --criterion and --step to capture the whole initial plan. Include required local inputs with `--need PATH "where to obtain or reproduce it"`. Derive values from the conversation. Ask only if an ambiguity changes the work.
- A first task on the clean common base normally activates immediately. Check the output. A second task is queued. On an unmanaged branch with existing edits, use `--base HEAD --adopt-current` only when the developer assigns those edits to this task. Resolve setup-only changes on the shared branch. Never assign unrelated work silently.
- On “continue,” run `RUN resume T-001` using the actual ID. Compare the active branch, code, staged state, inputs and check output. Give the original request, relevant plan changes and reasons, ruled-out approach, last applicable result or evidence gap, and one concrete next action. Switch before editing a different task.
- For “show my tasks,” run `RUN list`. Use `RUN list --verify` to check backup readability now. The index is generated. For a read-only request, read the existing index and handoffs directly. When requested, `RUN overview PROJECT1 PROJECT2` reads existing indexes across known projects.

## Plan and observations

- Record meaningful changes with `RUN plan T-001 --reason "why, evidence or decision" --step P1 done "completed step" --step P2 open "revised next step"`. Each --step takes an ID, a state (open, in-progress, done, blocked or superseded), and the full text. Use a new ID when adding a step. Keep the ID for a status update. Use a new ID for a materially different obligation and supersede the old one.
- For changed criteria, use the same command with `--criterion AC1 superseded "old criterion" --criterion AC2 active "new criterion"`. The original plan and criteria remain available. Revisions and reasons are logged. Keep at least one active criterion.
- Log a finding immediately with `RUN note T-001 "observation, supporting output and interpretation"`. Add --ruled-out for a dead end. Mark tentative explanations as hypotheses. Record changed denominators and the evidence for them.

## Checkpoints and switching

After a meaningful change, test result or blocker, checkpoint before the reply. Save editor buffers. Supply exactly five narrative fields in a UTF-8 JSON file outside the project and pass it to `RUN checkpoint T-001 --input FILE`, or pipe it with --input -. Remove the temporary file. Use the appropriate task ID. Do not include confidential data rows or credentials in handoffs or check output.

```json
{
  "done": "What changed, including affected plan IDs",
  "verification": null,
  "findings": "Observation, evidence and its meaning",
  "next_action": "One precise action with its expected outcome",
  "blockers": ""
}
```

For verification, null records an unrun check, a string records a reported claim, and an object such as `{"argv":["python","-B","-m","unittest","tests.test_parser"]}` runs a trusted local assertion with the matching launcher and actual test name. Prefer a check that writes no project files. Quote paths through normal shell argument handling. Report local checkpoint, validated result and verified backup separately. If a checkpoint succeeded but its backup failed, retry `RUN backup`. If a transaction was interrupted, use `RUN recover` before retrying.

When the developer changes editing tasks, register the incoming task if needed, then `RUN switch INCOMING_ID --input FILE` with the outgoing handoff. This command checkpoints the outgoing task, backs it up by default and switches the code and staging area. Use it in place of a duplicate outgoing checkpoint. From a clean unmanaged branch or completed task, omit the file. Next run resume for the incoming task. If switching stops, inspect the active task and reason before editing. An informational question about another task needs no code switch.

For completion, checkpoint final work, ensure the passing assertion actually covers the criterion, and run `RUN done T-001 --accept AC1=C03` with a mapping for every active criterion. Record which requirements remain when evidence is incomplete.

## Weekly results

A checkpoint refreshes a rolling seven-day Markdown report in `.tasks/reports/`. For “what changed this week,” run `RUN weekly` or `RUN weekly --ending YYYY-MM-DD`. The end date is inclusive, in UTC. If the user specifies a reporting window, use the requested end date. Use --save for a dated copy in the records store. A read-only request can read an existing report or use weekly without --save on initialized records.

Choose measures that fit the task and can be verified from local output. Record the source, unit, scope and measurement date. For rates, define what is counted and which items are included. Combine counts only across disjoint groups that use the same definition. Mark missing measurements as pending.

To report a rate from a passing check, emit one line starting with TASK_METRIC followed by a JSON object. The following is a fictional example for a text parser. Use values measured by the actual check in a project report.

```text
TASK_METRIC {"name":"Parser fixture coverage","scope":"text parser","denominator_definition":"input formats in the test manifest","as_of":"2000-01-01","numerator":3,"denominator":4}
```

The report compares the same task, metric name, scope and denominator definition across two consecutive seven-day windows. Check that the inputs and measurement periods are comparable. For other measures, such as elapsed time, record the value, unit and source in the findings. Lead with verified changes, then give outstanding issues and next actions. State which evidence is missing when a comparison is unavailable.

## Recovery

`RUN doctor` checks the pasted source in an existing project with a commit. `RUN doctor --verify` additionally reads back an existing backup. For a project with no Git commit, `RUN init` can create an empty local Git base. Source repositories with existing team instructions should keep the Task Monitor block alongside them. With a backup location chosen by the developer, `RUN init --backup-dir "PATH"` before the first task, or `RUN configure --backup-dir "PATH"` later, selects a dedicated folder outside the project. Task tracking uses local Git and a filesystem bundle. Never use push, Publish Branch, GitLab, or VS Code Sync Changes for task tracking. Pass only local checks that do not publish data. The chosen folder also contains a generated, browsable copy of the committed records under `progress/`. Open `progress/INDEX.md` for tasks and `progress/reports/` for weekly reports. Use one folder per project. To change locations, reconfigure to a new empty folder or the relocated, last verified copy. Report the bundle and the readable copy separately if the latter has pending changes. The default is on the same machine under `~/.copilot-task-monitor/backups/`. Use --local for a requested workspace-only operation.

To restore, use `RUN restore T-001/C03 --to NEW_DIRECTORY`. On another machine, run the pasted helper with `restore T-001/C03 --backup-dir "SAVED_FOLDER" --to NEW_DIRECTORY`. Add --run-check for a trusted local assertion. Report Git code/staging fidelity, required inputs and runnable validation as separate outcomes. Ordinary ignored files, empty directories, external data, secrets, unsaved buffers and running processes require separate recovery. Use --capture-need only when explicitly authorized to include a small ignored fixture. The helper has guards for unsupported repository states such as submodules or LFS-managed switching.
'''

PROJECT_GUIDES = {
    ".github/copilot-instructions.md": r'''## Task Monitor

Use the workflow in `.github/skills/task/SKILL.md` during substantive coding, debugging and investigation work. Treat plain-language requests as sufficient. The session doing the work owns its handoff.
- At the start of work, find the relevant task, resume it or create it. Keep its original request, subtasks, success criteria and decisions traceable.
- Record findings and dead ends as they occur. Before replying after meaningful progress, save a checkpoint and report any failed check or pending backup. Skip duplicate checkpoints when nothing changed.
- Before switching tasks, save outgoing work and load the incoming task using the skill. For a progress question, use the saved records and dated evidence.
- Use the existing project conventions and engineering agent. Respect read-only requests. If a tool or permission is unavailable, give the unsaved handoff in chat and state what is pending.
''',
    ".github/agents/task-monitor.agent.md": r'''---
name: Task Monitor
description: Review project tasks, resume handoffs, inspect checkpoint recovery, and prepare evidence-backed weekly updates.
---

Follow the project workflow in `.github/skills/task/SKILL.md`. Work from the task records and current workspace. Use the same helper and task IDs as the engineering session.

For “show my work,” list active, queued, paused and blocked tasks with next actions and the latest recoverable checkpoint. For “where did I stop,” show the original aim, material plan changes and reasons, ruled-out approaches, last applicable check, and next action. For “summarize this week,” report measured outcomes across activities, comparable changes, remaining gaps and next steps with evidence references.

Treat status and reporting requests as inspection. Switch code or restore a checkpoint only when the developer's request calls for it. Let the working session supply firsthand findings. If another chat's work was never saved, identify the gap.
''',
}

TASK_TEMPLATE = r'''## Handoff

{handoff}

## Original request

Recorded {created}

{request}

### Acceptance criteria

{criteria}

## Plan

{plan}

## Decisions

## Ruled out

## Open questions
'''


# Git and working tree

class Problem(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Problem(message)


def git(repo, *args, data=None, env=None, check=True):
    e = os.environ.copy()
    # A caller's Git environment must not redirect operations to another index/repo.
    for key in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX",
                "GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS",
                "GIT_ICASE_PATHSPECS"):
        e.pop(key, None)
    e.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    e.update(env or {})
    e["GIT_ALLOW_PROTOCOL"] = "file"
    cmd = ["git", "-c", "core.fsmonitor=false"]
    for scheme in ("http", "https", "ssh", "git", "ext"):
        cmd.extend(["-c", "protocol." + scheme + ".allow=never"])
    cmd.extend(["-C", str(repo), *args])
    r = subprocess.run(cmd, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e)
    if check and r.returncode:
        raise Problem(r.stderr.decode(errors="replace").strip() or
                      r.stdout.decode(errors="replace").strip() or f"git {args[0]} failed ({r.returncode})")
    return r


def val(repo, *args, **kwargs):
    return os.fsdecode(git(repo, *args, **kwargs).stdout).rstrip("\r\n")


def optional(repo, *args):
    r = git(repo, *args, check=False)
    return os.fsdecode(r.stdout).strip() if r.returncode == 0 else None


def internal_identity(repo):
    """Use neutral metadata for tool-created commits if no Git author is set."""
    name = optional(repo, "config", "--get", "user.name") or "Task Monitor"
    email = optional(repo, "config", "--get", "user.email") or "task-monitor@localhost"
    return {k: os.environ.get(k) or v for k, v in
            (("GIT_AUTHOR_NAME", name), ("GIT_AUTHOR_EMAIL", email),
             ("GIT_COMMITTER_NAME", name), ("GIT_COMMITTER_EMAIL", email))}


def items(raw):
    return [os.fsdecode(s) for s in raw.split(b"\0") if s]


def gitpath(repo, name):
    return Path(val(repo, "rev-parse", "--path-format=absolute", "--git-path", name))


def ref(repo, name):
    return optional(repo, "rev-parse", "--verify", "--end-of-options", name)


def branch(repo):
    name = optional(repo, "symbolic-ref", "-q", "HEAD")
    require(name and name.startswith("refs/heads/"), f"An attached local branch is required in {repo}.")
    return name


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def jsonbytes(obj):
    return (json.dumps(obj, ensure_ascii=True, indent=2) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_relative(name):
    require(isinstance(name, str) and name and not name.startswith(("/", "\\")) and
            not re.match(r"^[A-Za-z]:", name) and "\\" not in name and "\0" not in name and
            all(p not in ("", ".", "..") and p.casefold() != ".git" for p in name.split("/")),
            f"Expected a relative path inside the checkout: {name!r}")
    return name


def inside(root, name):
    """Disallow symlinks in the path for records, evidence and required-file reads."""
    safe_relative(name)
    p = root
    for part in name.split("/"):
        p = p / part
        require(not p.is_symlink(), f"Symlink in local record or required path: {name!r}")
    return p


@contextlib.contextmanager
def lock(control):
    control.mkdir(parents=True, exist_ok=True)
    with (control / "writer.lock").open("a+b") as f:
        if os.name == "nt":
            import msvcrt
            if f.tell() == 0:
                f.write(b"0")
                f.flush()
            f.seek(0)
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                raise Problem("Another task command is running.")
        else:
            import fcntl
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Problem("Another task command is running.")
        yield  # Closing this descriptor releases the lock, including on process exit.


@contextlib.contextmanager
def index(repo):
    with tempfile.TemporaryDirectory(prefix="task-index-", dir=gitpath(repo, ".")) as d:
        yield {"GIT_INDEX_FILE": str(Path(d) / "index")}


def check_repo(repo):
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge",
                   "rebase-apply", "sequencer", "BISECT_START", "index.lock"):
        require(not gitpath(repo, marker).exists(), f"Complete the current Git operation first ({marker}).")
    require(optional(repo, "config", "--bool", "core.sparseCheckout") != "true",
            "Use a full checkout for task snapshots.")
    require(not git(repo, "ls-files", "--unmerged", "-z").stdout, "Resolve the unmerged index first.")
    marked = items(git(repo, "ls-files", "-v", "-z").stdout)
    require(not any(s[0].islower() or s.startswith("S ") for s in marked),
            "Task snapshots need an index without assume-unchanged or skip-worktree entries.")
    diff = ("diff", "--cached", "--no-ext-diff", "--name-only", "--no-renames", "-z")
    require(git(repo, *diff, "--ita-visible-in-index").stdout ==
            git(repo, *diff, "--ita-invisible-in-index").stdout,
            "Stage or unstage intent-to-add entries before using a tree-based checkpoint.")


@lru_cache(maxsize=8192)
def secret_match(part):
    patterns = (".env", ".env.*", ".envrc", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks",
                "*.keytab", "id_rsa*", "id_ed25519*", ".netrc", ".npmrc", ".pypirc",
                "credentials", "credentials.*", "secrets", "secrets.*", ".ssh", ".aws")
    return any(fnmatch.fnmatchcase(part, pat) for pat in patterns)


def paths_allowed(paths):
    for name in paths:
        require(name.split("/")[0].casefold() != ".tasks",
                "The records directory appears in the code tree. Exclude /.tasks/ from the code repository.")
        require(not any(secret_match(part.casefold()) for part in name.split("/")),
                f"Secret-pattern path {name!r} would enter the snapshot. Move or ignore it if untracked.")


def index_tree(repo, alt):
    # Rebuild from the live entries so split indexes, stat caches and index writes
    # cannot affect the caller. Any staging-only blob remains reachable by its own ref.
    raw = git(repo, "ls-files", "--stage", "-z").stdout
    git(repo, "read-tree", "--empty", env=alt)
    git(repo, "update-index", "-z", "--index-info", data=raw, env=alt)
    return val(repo, "write-tree", env=alt)


def capture(repo, seed=None, base=None):
    """Return canonical worktree and index tree IDs without modifying the real index."""
    # During a switch the destination's committed files may differ from HEAD.
    tracked = tree_guard(repo, base or ref(repo, "HEAD"))
    with index(repo) as alt:
        if seed is None:
            staged = index_tree(repo, alt)
        else:
            git(repo, "read-tree", seed, env=alt)
            staged = seed
        paths = workspace_paths(repo, tracked | tree_guard(repo, staged))
        raw = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", *paths, env=alt).stdout
        candidates = set(items(raw))
        paths_allowed(candidates - tracked)
        max_size = int(optional(repo, "config", "--int", "taskmonitor.maxUntrackedBytes") or 5000000)
        require(max_size > 0, "taskmonitor.maxUntrackedBytes must be positive.")
        for name in candidates - tracked:
            p = repo / name
            if name.endswith("/") or (not p.is_symlink() and p.is_dir() and (p / ".git").exists()):
                raise Problem(f"Embedded repository {name!r} needs its own checkpoint.")
            try:
                size = p.lstat().st_size
            except (FileNotFoundError, NotADirectoryError):
                continue
            require(size <= max_size, f"New file {name!r} exceeds the {max_size}-byte limit.")
        # A forced stage can hold a large file even if the on-disk version is small.
        additions = [(path, oid) for path, oid in tree_blobs(repo, staged).items() if path not in tracked]
        if additions:
            oids = b"".join(oid + b"\n" for _, oid in additions)
            sizes = git(repo, "cat-file", "--batch-check=%(objectsize)", data=oids).stdout.splitlines()
            for (name, _), size in zip(additions, sizes):
                require(int(size) <= max_size, f"New staged file {name!r} exceeds the {max_size}-byte limit.")
        git(repo, "add", "-A", "--", *paths, env=alt)
        tree = val(repo, "write-tree", env=alt)
    return tree, staged


@lru_cache(maxsize=32)
def tree_blobs(repo, tree):
    raw = git(repo, "ls-tree", "-rz", tree).stdout.split(b"\0")
    blobs = {}
    for item in filter(None, raw):
        head, path = item.split(b"\t", 1)
        require(not head.startswith(b"160000 "), "Submodules require a separate recovery plan.")
        blobs[os.fsdecode(path)] = head.split()[2]
    paths_allowed(blobs)
    return blobs


@lru_cache(maxsize=32)
def tree_guard(repo, tree):
    return frozenset(tree_blobs(repo, tree))


@lru_cache(maxsize=16)
def lfs(repo, tree):
    r = git(repo, "grep", "-i", "-l", "-E", r"filter[[:space:]]*=[[:space:]]*lfs",
            tree, "--", ".gitattributes", ":(glob)**/.gitattributes", check=False)
    require(r.returncode in (0, 1), "Git could not inspect .gitattributes for LFS.")
    return r.returncode == 0


def changed(repo, old, new):
    # no-renames yields one path per row (also for binary files and odd filenames).
    raw = git(repo, "diff", "--no-ext-diff", "--no-renames", "--numstat", "-z", old, new, "--").stdout
    changes = []
    for line in raw.split(b"\0"):
        if line:
            add, remove, path = line.split(b"\t", 2)
            changes.append({"path": os.fsdecode(path), "added": add.decode(), "removed": remove.decode()})
    return changes


def protect_local_files(repo, source, target):
    """Git can replace an ignored path. Check files, symlink parents and directory/file collisions."""
    previous = tree_guard(repo, source)
    following = tree_guard(repo, target)
    source_dirs = {str(parent) for s in previous for parent in PurePosixPath(s).parents}
    def conflict(name):
        raise Problem(f"Task switch would overwrite local path {name!r}. Move it aside and retry.")
    for name in sorted(following - previous):
        current = repo
        parts = name.split("/")
        for part in parts[:-1]:
            current /= part
            if current.is_symlink() or (current.exists() and not current.is_dir()):
                if current.relative_to(repo).as_posix() not in previous:
                    conflict(current.relative_to(repo).as_posix())
                break  # The source owns this file; never descend through its symlink.
        else:
            leaf = repo / name
            if leaf.is_symlink() or (leaf.exists() and not leaf.is_dir()):
                conflict(name)
            if leaf.is_dir():
                if name not in source_dirs:
                    conflict(name)
                for parent, dirs, files in os.walk(leaf, followlinks=False):
                    for child in dirs + files:
                        p = Path(parent) / child
                        rel = p.relative_to(repo).as_posix()
                        if rel not in previous and rel not in source_dirs:
                            conflict(rel)


def apply_tree(repo, old, new):
    if old == new:
        return
    protect_local_files(repo, old, new)
    with index(repo) as alt:
        git(repo, "read-tree", old, env=alt)
        git(repo, "update-index", "--refresh", env=alt)
        git(repo, "read-tree", "-m", "-u", old, new, env=alt)


def removed_paths_absent(repo, old, new):
    # A removed force-staged ignored path can disappear from Git's view while
    # still existing on disk. Check it explicitly when completing a switch.
    before, after = tree_guard(repo, old), tree_guard(repo, new)
    directories = {str(p) for s in after for p in PurePosixPath(s).parents}
    for name in before - after:
        if name in directories or any(str(p) in after for p in PurePosixPath(name).parents):
            continue
        if os.path.lexists(repo / name):
            return False
    return True


def ensure_available(repo, name):
    lines = items(git(repo, "worktree", "list", "--porcelain", "-z").stdout)
    worktree = None
    for line in lines:
        if line.startswith("worktree "):
            worktree = Path(line[9:]).resolve()
        elif line == "branch " + name:
            require(worktree == repo, f"{name} is active in {worktree}.")


def check_checkout_hooks(repo):
    hook = gitpath(repo, "hooks/post-checkout")
    configured = git(repo, "config", "--get-regexp", r"^hook\..*\.event$", "^post-checkout$", check=False)
    require(configured.returncode in (0, 1), "Cannot inspect checkout hook configuration.")
    require(not (hook.is_file() and os.access(hook, os.X_OK)) and not configured.stdout,
            "This repository uses a post-checkout hook. The task switch uses Git plumbing. "
            "Use a separate checkout so the project's checkout workflow stays intact.")


# Task records

def textfile(path):
    return path.read_text(encoding="utf-8")


def file_hash(path):
    return sha(path.read_bytes()) if path.exists() else None


def cell(value):
    return " ".join(str(value or "—").split()).replace("|", r"\|") or "—"


def render_index(tasks):
    rows = ["# Tasks", "", "| Task | Title | Status | Next action or blocker | Latest | Last durable |",
            "| --- | --- | --- | --- | --- | --- |"]
    for _, (folder, meta, _) in sorted(tasks.items()):
        last = meta["last_checkpoint"]
        preview = meta["blockers"] if meta["status"] == "blocked" else meta["next_action"]
        rows.append(f'| [{meta["id"]}]({folder}/task.md) | {cell(meta["title"])} | {meta["status"]} | '
                    f'{cell(preview)} | {last + (" (verified backup)" if last == meta["last_durable"] else " (local)") if last else "—"} | {meta["last_durable"] or "—"} |')
    return "\n".join(rows) + "\n"


def split_doc(text):
    head, sep, body = text.partition("\n---\n")
    require(head.startswith("---\n") and sep, "Invalid task.md front matter.")
    meta = {}
    try:
        for line in head.splitlines()[1:]:
            key, sep, value = line.partition(": ")
            require(sep, "Use one JSON value per front-matter field. See SKILL.md for the needs format.")
            meta[key] = json.loads(value)
    except ValueError as err:
        raise Problem(f"Invalid front-matter value: {err}")
    for key in ("id", "title", "status", "branch", "created_base", "last_checkpoint", "last_durable",
                "needs", "next_action", "blockers", "updated"):
        require(key in meta, f"Missing task.md field {key!r}.")
    return meta, body


def document(meta, body):
    lines = [f"{key}: {json.dumps(value, ensure_ascii=True)}" for key, value in meta.items()]
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def section(body, name, content, append=False):
    match = re.search(rf"(?ms)^## {re.escape(name)}\n(.*?)(?=^## |\Z)", body)
    require(match, f"Missing task.md heading: {name}")
    old = match[1].strip() if append else ""
    new = "\n" + (old + "\n" if old else "") + content.strip() + "\n\n"
    return body[:match.start(1)] + new + body[match.end(1):]


class Store:
    def __init__(self, code, control):
        self.code = code
        self.root = code / ".tasks"
        self.control = control
        self.journal = control / "record-transaction.json"
        self.observed = {}

    def validate(self):
        require(not self.root.is_symlink() and (self.root / ".git").exists(),
                "Run the task script's init command to create the local records checkout.")
        require(Path(val(self.root, "rev-parse", "--show-toplevel")).resolve() == self.root,
                ".tasks must be its own Git checkout.")
        require(not val(self.code, "ls-files", "--", ".tasks") and
                git(self.code, "check-ignore", "-q", "--", ".tasks/", check=False).returncode == 0,
                "The code repository must exclude /.tasks/ and have no tracked records.")
        require(branch(self.root) != optional(self.code, "symbolic-ref", "-q", "HEAD") or
                gitpath(self.root, "objects").resolve() != gitpath(self.code, "objects").resolve(),
                "Use a separate records checkout or a dedicated records branch.")

    def init(self, base):
        require(not self.root.is_symlink(), ".tasks cannot be a symlink.")
        require(not val(self.code, "ls-files", "--", ".tasks") and
                not val(self.code, "ls-tree", "HEAD", "--", ".tasks"),
                "The code repository already tracks .tasks. Resolve that before initializing.")
        require(not self.root.exists() or (self.root / ".git").exists() or
                (self.root.is_dir() and not any(self.root.iterdir())),
                "An existing nonempty .tasks directory must be a separate Git checkout.")
        exclude = gitpath(self.code, "info/exclude")
        old = exclude.read_bytes() if exclude.exists() else b""
        if b"/.tasks/" not in old.splitlines():
            atomic(exclude, old.rstrip(b"\n") + b"\n/.tasks/\n")
        if not (self.root / ".git").exists():
            git(self.code, "init", "-q", "--object-format=" + val(self.code, "rev-parse", "--show-object-format"), "-b", "task-records", str(self.root))
        self.validate()
        if ref(self.root, "HEAD") is None:
            require(not val(self.root, "ls-files"), "Use an empty records index to initialize the store.")
        for key in ("user.name", "user.email"):
            if not optional(self.root, "config", "--get", key):
                value = optional(self.code, "config", "--get", key)
                value = value or ("Task Monitor" if key == "user.name" else "task-monitor@localhost")
                git(self.root, "config", "--local", key, value)
        prev = optional(self.code, "config", "--local", "taskmonitor.baseRef")
        existing_index = self.root / "INDEX.md"
        if not prev and existing_index.exists():
            require(textfile(existing_index).startswith("# Tasks\n\n| Task | Title | Status | Next action or blocker |"),
                    "An existing .tasks/INDEX.md belongs to another workflow. Preserve it before initialization.")
        base_ref = ("refs/heads/" + base) if base else (prev or branch(self.code))
        require(ref(self.code, base_ref), f"Local base branch {base_ref} is missing.")
        git(self.code, "config", "--local", "taskmonitor.baseRef", base_ref)
        self.recover()
        attrs = inside(self.root, ".gitattributes")
        present = attrs.read_bytes() if attrs.is_file() else b""
        rule = b"* -text -ident -filter -working-tree-encoding"
        if rule not in present.splitlines():
            present = present.rstrip(b"\r\n") + (b"\n" if present else b"") + rule + b"\n"
        self.commit("Initialize task records", {"INDEX.md": render_index(self.tasks()).encode(),
                                                ".gitattributes": present})
        return base_ref

    def tasks(self):
        tasks = {}
        for path in sorted([*self.root.glob("T-*/task.md"), *self.root.glob("archive/T-*/task.md")]):
            folder = path.parent.relative_to(self.root).as_posix()
            name = folder + "/task.md"
            raw = inside(self.root, name).read_bytes()
            self.observed.setdefault(name, sha(raw))
            meta, body = split_doc(raw.decode("utf-8").replace("\r\n", "\n"))
            tid = meta["id"]
            require(re.fullmatch(r"T-\d{3,}", tid) and path.parent.name.startswith(tid + "-"),
                    f"Task ID does not match its folder {folder!r}.")
            require(tid not in tasks, f"Duplicate task ID {tid}.")
            tasks[tid] = (folder, meta, body)
        return tasks

    def update(self, tasks, changes, outputs, message, refs=()):
        for folder, meta, body in changes:
            tasks[meta["id"]] = (folder, meta, body)
            outputs[folder + "/task.md"] = document(meta, body).encode()
        outputs["INDEX.md"] = render_index(tasks).encode()
        self.commit(message, outputs, refs)

    def append_log(self, folder, entry):
        name = folder + "/log.md"
        p = inside(self.root, name)
        old = p.read_bytes() if p.exists() else b""
        self.observed.setdefault(name, sha(old) if p.exists() else None)
        head = ref(self.root, "HEAD")
        if head:
            blob = ref(self.root, head + ":" + name)
            if blob:
                require(old.startswith(git(self.root, "cat-file", "blob", blob).stdout),
                        f"Restore the committed prefix of {name} before appending.")
        return {name: old + entry.encode()}

    def commit(self, message, outputs, refs=()):
        tx = self.prepare(message, outputs, refs)
        if tx:
            self.publish(tx)

    def publish(self, tx):
        atomic(self.journal, jsonbytes(tx))
        self.recover()

    def prepare(self, message, outputs, refs=()):
        """Build a new commit privately. Publish its pointer, then refresh only the affected files."""
        require(not self.journal.exists(), "Finish the outstanding record transaction first.")
        old = ref(self.root, "HEAD")
        target = branch(self.root)
        previous = {}
        with index(self.root) as alt:
            git(self.root, "read-tree", old or "--empty", env=alt)
            for name, data in outputs.items():
                path = inside(self.root, name)
                previous[name] = file_hash(path)
                require(self.observed.get(name, previous[name]) == previous[name],
                        f"{name!r} changed while preparing this record. Retry to incorporate that edit.")
                r = git(self.root, "--literal-pathspecs", "diff", "--cached", "--quiet", "--", name, check=False)
                require(r.returncode == 0, f"Finish the staged records edit to {name!r} before writing it.")
                if data is None:
                    git(self.root, "update-index", "--force-remove", "--", name, env=alt)
                    continue
                oid = val(self.root, "hash-object", "-w", "--stdin", data=data)
                git(self.root, "update-index", "--add", "--cacheinfo", "100644", oid, name, env=alt)
            tree = val(self.root, "write-tree", env=alt)
        if old and val(self.root, "rev-parse", old + "^{tree}") == tree and not refs:
            # Rebuild a deleted or manually modified generated index from the committed form.
            for name, data in outputs.items():
                if data is not None and previous[name] != sha(data):
                    atomic(inside(self.root, name), data)
            self.observed.clear()
            return
        args = ["commit-tree", tree]
        if old:
            args.extend(["-p", old])
        new = val(self.root, *args, "-m", message)
        return dict(target=target, before=old, after=new, refs=refs, previous=previous)

    def recover(self):
        if not self.journal.exists():
            return
        tx = json.loads(self.journal.read_bytes())
        old, new = tx["before"], tx["after"]
        require(branch(self.root) == tx["target"], "Return the records checkout to its transaction branch.")
        current = ref(self.root, tx["target"])
        require(current in (old, new), "Records HEAD moved during publication. Preserve it before recovering.")
        blobs = {}
        index_entries = []
        zero = "0" * len(new)
        for name, before_hash in tx["previous"].items():
            oid = ref(self.root, new + ":" + name)
            blob = git(self.root, "cat-file", "blob", oid).stdout if oid else None
            mode = "100644" if oid else "0"
            index_entries.append(f"{mode} {oid or zero}\t{name}\0".encode())
            require(file_hash(inside(self.root, name)) in (before_hash, sha(blob) if blob is not None else None),
                    f"Concurrent edit in {name!r}. Save a copy before completing the pending transaction.")
            staged = ref(self.root, ":" + name)
            before_blob = ref(self.root, old + ":" + name) if old else None
            require(staged in (before_blob, oid),
                    f"Concurrent staged edit in {name!r}. Preserve it before completing the pending transaction.")
            blobs[name] = blob
        for name, oid in tx["refs"]:
            present = ref(self.code, name)
            if present != oid:
                require(present is None, f"Local ref {name} already points to a different object.")
                git(self.code, "update-ref", name, oid, "0" * len(oid))
        if current != new:
            git(self.root, "update-ref", tx["target"], new, old or "0" * len(new))
        git(self.root, "update-index", "-z", "--index-info", data=b"".join(index_entries))
        for name, data in blobs.items():
            path = inside(self.root, name)
            if data is None:
                path.unlink(missing_ok=True)
            elif file_hash(path) != sha(data):
                atomic(path, data)
        self.journal.unlink()
        self.observed.clear()


# Tasks, evidence and switching


LOCKFILES = ("uv.lock", "poetry.lock", "Pipfile.lock", "requirements.txt", "environment.yml",
             "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pom.xml", "Cargo.lock", "go.sum")
EVIDENCE_LIMIT = 65536


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def wording(value, name):
    require(isinstance(value, str) and value.strip(), f"Provide a nonempty {name}.")
    return value.strip()


def task_by_id(tasks, tid):
    require(tid in tasks, f"Unknown task {tid!r}. Run list for the IDs.")
    return tasks[tid]


def active_task(tasks, code):
    current = branch(code).removeprefix("refs/heads/")
    return next((t for t in tasks.values() if t[1]["branch"] == current), None)


def payload(path):
    require(path, "Supply the outgoing handoff with --input FILE or --input - (JSON on stdin).")
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
    data = json.loads(raw.lstrip("\ufeff"))
    fields = {"done", "verification", "findings", "next_action", "blockers"}
    require(isinstance(data, dict) and data.keys() == fields, "Use the five JSON keys shown in SKILL.md.")
    for key in fields - {"verification"}:
        require(isinstance(data[key], str), f"{key} must be text.")
        data[key] = data[key].strip()
    wording(data["done"], "done field")
    wording(data["next_action"], "next action")
    verification = data["verification"]
    require(verification is None or isinstance(verification, str) or
            (isinstance(verification, dict) and set(verification) == {"argv"} and valid_argv(verification["argv"])),
            'verification must be null, a claim as text, or {"argv": ["executable", "argument"]}.')
    return data


def valid_argv(argv):
    return isinstance(argv, list) and bool(argv) and all(isinstance(s, str) and s and "\0" not in s for s in argv)


def file_digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def needs(code, configured):
    require(isinstance(configured, list), "needs must be a list of path/restore objects.")
    manifest = {}
    for entry in configured:
        require(isinstance(entry, dict) and {"path", "restore"} <= set(entry) <= {"path", "restore", "capture"} and isinstance(entry.get("capture", False), bool), "Each need requires path and restore.")
        name = safe_relative(entry["path"])
        wording(entry["restore"], "restore instruction")
        require(name.split("/")[0].casefold() != ".tasks" and name not in manifest,
                f"Invalid or repeated required file {name!r}.")
        path = inside(code, name)
        if entry.get("capture"):
            require("\n" not in name and "\r" not in name, "Captured fixture paths must fit on one Git exclude line.")
            paths_allowed([name])
            require(not val(code, "--literal-pathspecs", "ls-files", "--", name) and git(code, "check-ignore", "-q", "--", name, check=False).returncode == 0,
                    f"Explicit input capture is for ignored, untracked files: {name}")
            require(not path.is_file() or path.stat().st_size <= 5000000, "Captured inputs are limited to 5 MB each.")
        manifest[name] = {"restore": entry["restore"], "present": path.is_file()}
        if path.is_file():
            manifest[name].update(size=path.stat().st_size, sha256=file_digest(path))
            if entry.get("capture"):
                manifest[name]["captured"] = True
    return manifest


def run_saved(argv, cwd, seconds, limit):
    # Stream to an off-tree temporary file so a verbose test cannot exhaust RAM.
    with tempfile.TemporaryFile() as out:
        try:
            r = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out,
                               stderr=subprocess.STDOUT, timeout=seconds, shell=False)
            code, reason = r.returncode, ""
        except (OSError, subprocess.TimeoutExpired) as exc:
            code, reason = None, str(exc)
        length = out.tell()
        out.seek(0)
        kept = out.read(limit)
    return code, reason, kept, length


def environment(code):
    info = {"python": platform.python_version(), "system": platform.system(),
            "machine": platform.machine(), "git": val(code, "--version"), "dependency_files": {}}
    for name in LOCKFILES:
        p = code / name
        if p.is_file() and not p.is_symlink():
            info["dependency_files"][name] = file_digest(p)
    cmd = optional(code, "config", "--local", "taskmonitor.envCommand")
    if cmd:
        argv = json.loads(cmd)
        require(valid_argv(argv), "taskmonitor.envCommand must be a JSON argv array.")
        rc, reason, data, size = run_saved(argv, code, 60, 8 * 1024 * 1024)
        info["probe"] = {"argv": argv, "returncode": rc, "complete": rc == 0 and size == len(data),
                         "sha256": sha(data), "error": reason}
    return info


def need_gaps(before, after):
    gaps = []
    for path in sorted(before.keys() | after.keys()):
        a, b = before.get(path), after.get(path)
        if b is None:
            gaps.append(f"{path} removed from needs")
        elif not b["present"]:
            gaps.append(f'{path} missing — {b["restore"]}')
        elif a is None:
            gaps.append(f"{path} added to needs")
        elif a.get("sha256") != b["sha256"]:
            gaps.append(f"{path} changed")
    return gaps


def same_inputs(before, after):
    return before == after and all(v["present"] for v in after.values())


def env_ready(env):
    return env.get("probe", {}).get("complete", True)


def new_task(store, args):
    code, tasks = store.code, store.tasks()
    check_repo(code)
    branch(code)
    title = wording(args.title, "title")
    request = wording(args.request, "original request")
    criteria = [wording(s, "acceptance criterion") for s in args.criterion]
    steps = [wording(s, "plan step") for s in args.step]
    prefix = max((int(key[2:]) for key in tasks), default=0) + 1
    tid = f"T-{prefix:03d}"
    slug = re.sub("[^a-z0-9]+", "-", title.lower()).strip("-")[:48].rstrip("-") or "task"
    folder = tid + "-" + slug
    require(not (store.root / folder).exists(), f"Folder {folder} already exists.")
    name = "task/" + folder
    local_ref = "refs/heads/" + name
    require(ref(code, local_ref) is None, f"Branch {name} already exists.")
    base_ref = args.base or optional(code, "config", "--local", "taskmonitor.baseRef") or branch(code)
    base = ref(code, base_ref + "^{commit}")
    require(base, f"Cannot resolve task base {base_ref!r}.")
    tree_guard(code, base)
    next_action = args.next_action or steps[0]
    reqs = [{"path": path, "restore": restore} for path, restore in args.need]
    reqs.extend({"path": path, "restore": restore, "capture": True} for path, restore in args.capture_need)
    needs(code, reqs)
    if args.adopt_current:
        require(active_task(tasks, code) is None and ref(code, "HEAD") == base,
                "--adopt-current needs an unmanaged branch at the requested base. Pass --base HEAD if appropriate.")
        capture(code)
    meta = dict(id=tid, title=title, status="queued", branch=name, created_base=base, last_checkpoint=None,
                last_durable=None, updated=now(), needs=reqs, next_action=next_action, blockers="")
    body = TASK_TEMPLATE.format(handoff="Next action — " + next_action, request=request,
                created=meta["updated"],
                criteria="\n".join(f"- AC{i}. {s}" for i, s in enumerate(criteria, 1)),
                plan="\n".join(f"- P{i} [Open] {s}" for i, s in enumerate(steps, 1)))
    outputs = store.append_log(folder, f"# {tid} log\n\nCreated {meta['updated']}\n")
    store.update(tasks, [(folder, meta, body)], outputs, "Create " + tid, [(local_ref, base)])
    print(f"Created {tid} on {name} at {base[:12]}.")
    # Queue new tasks from an active task. The first task may start immediately
    # when already on the same clean base. A queued task never absorbs other edits.
    if args.adopt_current:
        git(code, "switch", "--no-overwrite-ignore", name)
        meta["status"] = "in-progress"
        store.update(tasks, [(folder, meta, body)], {}, "Adopt existing work for " + tid)
        print(f"Active {tid}. Existing work and staged changes stay in this task.")
    elif active_task(tasks, code) is None and ref(code, "HEAD") == base and not managed_status(code):
        try:
            switch(store, tid, None)
        except Problem as error:
            if store.journal.exists() or (store.control / "switch.json").exists():
                raise
            print(f"Queued. Automatic activation stopped: {error}")
    else:
        print(f"Queued. Use switch {tid} to start.")


def revise_plan(store, args):
    tasks = store.tasks()
    folder, meta, body = task_by_id(tasks, args.id)
    require(meta["status"] != "done", "This task is archived.")
    reason = wording(args.reason, "reason for changing the plan")
    require(args.step or args.criterion, "Supply --step or --criterion.")
    groups = (
        ("## Plan", "P", args.step, {"open", "in-progress", "done", "blocked", "superseded"}),
        ("### Acceptance criteria", "AC", args.criterion, {"active", "superseded"}),
    )
    originals, revisions, changes = [], {}, []
    for heading, prefix, edits, states in groups:
        match = re.search(r"(?ms)^" + re.escape(heading) + r"[ \t]*\n(.*?)(?=^## |\Z)", body)
        require(match, f"Missing {heading} in task record.")
        before = match.group(1).strip()
        originals.append(before)
        if not edits:
            continue
        rows = before.splitlines()
        positions = {}
        for i, row in enumerate(rows):
            entry = re.match(r"^- (?:Superseded )?(" + prefix + r"\d+)\b", row)
            if entry:
                require(entry[1] not in positions, f"Duplicate ID in record: {entry[1]}")
                positions[entry[1]] = i
        seen = set()
        for key, state, detail in edits:
            require(re.fullmatch(prefix + r"[1-9]\d*", key) and key not in seen, f"Invalid or repeated ID: {key}")
            require(state in states, f"Invalid state for {key}. Choose from {', '.join(sorted(states))}.")
            detail = wording(detail, "full text")
            require(len(detail.splitlines()) == 1, f"Use one line for {key}.")
            seen.add(key)
            if prefix == "P":
                row = f"- {key} [{state.capitalize()}] {detail}"
            else:
                row = ("- Superseded " if state == "superseded" else "- ") + f"{key}. {detail}"
            if key in positions:
                previous = rows[positions[key]]
                if row == previous:
                    continue
                rows[positions[key]] = row
            else:
                previous = "(new)"
                rows.append(row)
            changes.append(f"{previous} → {row}")
        if prefix == "AC":
            require(any(re.match(r"^- AC\d+\.", r) for r in rows), "Keep at least one active acceptance criterion.")
        revisions[heading] = "\n".join(rows)
    if not changes:
        print("Plan already reflects these updates.")
        return
    if "\n## Original plan and criteria\n" not in body:
        body = body.rstrip() + "\n\n## Original plan and criteria\n\n" + "\n\n".join(originals) + "\n"
    for heading, revised in revisions.items():
        pattern = r"(?ms)(^" + re.escape(heading) + r"[ \t]*\n).*?(?=^## |\Z)"
        body = re.sub(pattern, lambda m: m[1] + "\n" + revised + "\n\n", body, count=1)
    stamp = now()
    entry = f"- {stamp} · {reason}\n" + "\n".join("  " + line for line in changes)
    body = section(body, "Decisions", entry, append=True)
    meta["updated"] = stamp
    out = store.append_log(folder, f"\n## Plan revision · {stamp}\n\n{entry}\n")
    store.update(tasks, [(folder, meta, body)], out, f"Revise plan for {args.id}")
    print(f"Updated plan for {args.id}.")


def note(store, args):
    tasks = store.tasks()
    folder, meta, body = task_by_id(tasks, args.id)
    require(meta["status"] != "done", "This task is archived.")
    msg = wording(args.text, "note")
    stamp = now()
    kind = "Ruled out" if args.ruled_out else "Finding"
    line = f"- {stamp} · {kind} · {msg}\n"
    if args.ruled_out:
        body = section(body, "Ruled out", f"- {msg} ({stamp}, latest checkpoint {meta['last_checkpoint'] or 'none'})", True)
    meta["updated"] = stamp
    store.update(tasks, [(folder, meta, body)], store.append_log(folder, "\n" + line), f"{kind} for {args.id}")
    print(line.strip())


def list_tasks(store):
    tasks = store.tasks()
    table = render_index(tasks)
    store.commit("Refresh task index", {"INDEX.md": table.encode()})
    print(table)
    branch_name = branch(store.root).removeprefix("refs/heads/")
    print(f"Records: local commit {ref(store.root, 'HEAD')[:12]} ({branch_name}).")
    stashes = val(store.code, "stash", "list", "--format=%gd").splitlines()
    local = val(store.code, "for-each-ref", "--format=%(refname:short)%09%(upstream:track,nobracket)%09%(upstream)",
                "refs/heads/").splitlines()
    pending = []
    for row in local:
        name, tracking, upstream = (row.split("\t") + ["", ""])[:3]
        if not upstream or "ahead" in tracking or "gone" in tracking:
            pending.append(name + (" (" + tracking + ")" if tracking else " (no upstream)"))
    print(f"Stashes outside checkpoints: {len(stashes)}. Branches to review (cached refs): {', '.join(pending) or 'none'}.")
    dirty = git(store.root, "status", "--porcelain", "-z").stdout
    if dirty:
        print("Records also contain uncommitted edits.")


def cp_path(folder, cp):
    return f"{folder}/checkpoints/{cp}.json"


def load_cp(store, task, checkpoint=None):
    folder, meta, _ = task
    cp = checkpoint or meta["last_checkpoint"]
    if not cp:
        return None
    require(re.fullmatch(r"C[0-9]+", cp), "Invalid checkpoint identifier.")
    # Read immutable machine facts from the records commit, not pending worktree edits.
    raw = git(store.root, "show", "HEAD:" + cp_path(folder, cp)).stdout
    record = json.loads(raw)
    tid = meta["id"]
    require(record.get("id") == tid + "/" + cp and record.get("branch") == meta["branch"] and
            ref(store.code, f"refs/ckpt/{tid}/{cp}") == record["snapshot"] and
            ref(store.code, f"refs/ckpt-index/{tid}/{cp}") == record["index"] and
            ref(store.code, record["snapshot"] + "^{tree}") == record["tree"] and
            ref(store.code, record["snapshot"] + "^") == record["base"],
            f"Local objects for {tid}/{cp} are missing or inconsistent.")
    return record


def check_result(code, spec):
    if spec is None:
        return {"state": "pending", "result": "No command run."}, None
    if isinstance(spec, str):
        return {"state": "claimed", "result": wording(spec, "verification claim")}, None
    argv = spec["argv"]
    rc, reason, data, size = run_saved(argv, code, 300, EVIDENCE_LIMIT)
    result = {"state": "verified" if rc == 0 else ("failed" if rc is not None else "pending"),
              "argv": argv, "exit": rc, "result": reason or f"Exit {rc}.",
              "output_bytes": size, "retained_bytes": len(data)}
    if size > len(data):
        result["result"] += f" Output exceeded {EVIDENCE_LIMIT} bytes."
        if result["state"] == "verified":
            result["state"] = "claimed"
    header = json.dumps({"argv": argv, "exit": rc, "error": reason,
                         "output_bytes": size, "retained_bytes": len(data)}, ensure_ascii=True)
    return result, header.encode() + b"\n\n" + data


def verification_line(v):
    cmd = (" " + json.dumps(v["argv"], ensure_ascii=False)) if "argv" in v else ""
    proof = (" · " + v["evidence"]) if "evidence" in v else ""
    return f'{v["state"]}{cmd} · {v["result"]}{proof}'


def checkpoint(store, task, data):
    code = store.code
    tasks = store.tasks()
    folder, meta, body = task_by_id(tasks, task[1]["id"])
    tid = meta["id"]
    require(meta["status"] != "done", "This task is archived.")
    require(branch(code) == "refs/heads/" + meta["branch"], f"Switch to {meta['branch']} before checkpointing {tid}.")
    check_repo(code)
    base = ref(code, "HEAD")
    number = int(meta["last_checkpoint"][1:]) + 1 if meta["last_checkpoint"] else 1
    cp = f"C{number:02d}"
    stamp = now()
    tree, stage = capture(code)
    tree_guard(code, tree)
    cpname = tid + "/" + cp
    snap = val(code, "commit-tree", tree, "-p", base, "-m", cpname, env=internal_identity(code))
    before_needs, env = needs(code, meta["needs"]), environment(code)
    verification, evidence = check_result(code, data["verification"])
    inventory = needs(code, meta["needs"])
    after_env = environment(code) if isinstance(data["verification"], dict) else env
    require(ref(code, "HEAD") == base and branch(code) == "refs/heads/" + meta["branch"] and
            capture(code) == (tree, stage),
            "Code, branch or index changed during capture/check. Review the new state and retry the checkpoint.")
    if verification["state"] == "verified" and (not same_inputs(before_needs, inventory)
            or after_env != env or not env_ready(env)):
        verification.update(state="claimed", result="Command passed with missing or changed required inputs or environment.")
    verification.update(snapshot=snap, tree=tree)
    outputs = {}
    for path, item in inventory.items():
        if item.get("captured"):
            raw = inside(code, path).read_bytes()
            require(len(raw) <= 5000000 and sha(raw) == item["sha256"], f"Input {path} changed during capture.")
            outputs[f"{folder}/inputs/{cp}/{path}"] = raw
    if evidence is not None:
        proof = f"evidence/{cp}-check.txt"
        verification.update(evidence=proof, sha256=sha(evidence))
        outputs[folder + "/" + proof] = evidence
    previous = load_cp(store, (folder, meta, body))
    last_verified = (previous or {}).get("last_verified")
    superseded = (previous or {}).get("verification_issue")
    if verification["state"] == "verified":
        last_verified, superseded = cp, None
    elif last_verified and verification.get("argv"):
        passed = load_cp(store, (folder, meta, body), last_verified)
        if passed["tree"] == tree and passed["verification"].get("argv") == verification["argv"]:
            superseded = f'{cp} reported {verification["state"]} on the same check'
    files = changed(code, base, tree)
    record = dict(id=cpname, time=stamp, branch=meta["branch"], base=base, snapshot=snap, tree=tree,
                  index=stage, code_status="local", narrative={k: data[k] for k in ("done", "findings", "next_action", "blockers")}, changed=files, needs=inventory, environment=after_env,
                  verification=verification, last_verified=last_verified, verification_issue=superseded,
                  project_guides=sorted(pasted_project_guides(code)), lfs=lfs(code, tree))
    name = cp_path(folder, cp)
    require(not inside(store.root, name).exists(), f"Checkpoint file already exists: {name}")
    for name_ in outputs:
        require(not inside(store.root, name_).exists(), f"Evidence file already exists: {name_}")
    outputs[name] = jsonbytes(record)
    meta.update(last_checkpoint=cp, status="blocked" if data["blockers"] else "in-progress", updated=stamp,
                next_action=data["next_action"], blockers=data["blockers"])
    short = (f"{data['done']}\n\n- Check at {cp} — {verification_line(verification)}\n"
             f"- Last verified checkpoint — {last_verified or 'none'}\n- Next action — {data['next_action']}\n"
             f"- Blockers — {data['blockers'] or 'none'}")
    if data["findings"]:
        short += "\n- Finding — " + data["findings"]
    body = section(body, "Handoff", short)
    file_list = "\n".join(f'  - {json.dumps(x["path"], ensure_ascii=True)} (+{x["added"]}/−{x["removed"]})' for x in files)
    needed = ", ".join(f"{k} {'present' if v['present'] else 'missing'}" for k, v in inventory.items()) or "none"
    entry = (f"\n## {cpname} · {stamp}\n\n- Code — local\n- Branch — {meta['branch']}\n"
             f"- Base — {base}\n- Snapshot — {snap}\n- Tree — {tree}\n- Changed files — {len(files)}\n"
             f"{file_list}\n- Required files — {needed}\n- Environment SHA-256 — {sha(jsonbytes(after_env))}\n"
             f"- Done — {data['done']}\n- Verification — {verification_line(verification)}\n"
             f"- Findings — {data['findings'] or 'none'}\n- Next action — {data['next_action']}\n"
             f"- Blockers — {data['blockers'] or 'none'}\n- Machine details — {name.split('/', 1)[1]}\n")
    outputs.update(store.append_log(folder, entry))
    refs = [(f"refs/ckpt/{cpname}", snap), (f"refs/ckpt-index/{cpname}", stage)]
    store.update(tasks, [(folder, meta, body)], outputs, cpname, refs)
    refresh_checkpoint_report(store)
    print(f"{cpname} · local · tree {tree} · {verification_line(verification)}")
    if record["lfs"]:
        print("Git LFS pointers detected. Local snapshots omit LFS objects. Switching this tree is unavailable in a managed switch.")
    return record


def state_for(store, task):
    _, meta, _ = task
    cp = load_cp(store, task)
    base = cp["base"] if cp else meta["created_base"]
    name = "refs/heads/" + meta["branch"]
    current = ref(store.code, name)
    require(current == base, f"{meta['branch']} moved. Expected {base}, found {current}. Worktree was left in place.")
    base_tree = val(store.code, "rev-parse", base + "^{tree}")
    return dict(task=meta["id"], branch=name, base=base, tree=cp["tree"] if cp else base_tree,
                index=cp["index"] if cp else base_tree)


def switch(store, tid, input_path, before_switch=None):
    tasks, code = store.tasks(), store.code
    outgoing = active_task(tasks, code)
    incoming = task_by_id(tasks, tid)
    check_repo(code)
    require(incoming[1]["status"] != "done", "This task is archived. Use resume to inspect it.")
    if outgoing and outgoing[1]["id"] == tid:
        print(f"{tid} is already active.")
        return
    check_checkout_hooks(code)
    target = state_for(store, incoming)
    ensure_available(code, target["branch"])
    if outgoing and outgoing[1]["status"] == "done":
        source = state_for(store, outgoing)
        if before_switch:
            before_switch(store)
    elif outgoing:
        data = payload(input_path)
        # Check the incoming target before checkpointing or changing either working state.
        check_out, _ = capture(code)
        require(not lfs(code, check_out) and not lfs(code, target["tree"]), "LFS objects need a separate worktree for managed switching.")
        protect_local_files(code, check_out, target["tree"])
        checkpoint(store, outgoing, data)
        if before_switch:
            before_switch(store)
        source = state_for(store, store.tasks()[outgoing[1]["id"]])
    else:
        require(not managed_status(code),
                "The current unmanaged checkout has edits. Save them before switching into a task.")
        head = ref(code, "HEAD")
        t = val(code, "rev-parse", "HEAD^{tree}")
        source = dict(task=None, branch=branch(code), base=head, tree=t, index=t)
    for side in (source, target):
        tree_guard(code, side["base"])
        tree_guard(code, side["index"])
        require(not lfs(code, side["tree"]), "LFS objects need a separate worktree for managed switching.")
    require(capture(code) == (source["tree"], source["index"]), "Outgoing tree or index drifted. Retry.")
    for file in (SCRIPT_REL, GUIDE_REL, *PROJECT_GUIDES):
        if file in tree_guard(code, source["tree"]) and file not in tree_guard(code, target["tree"]):
            raise Problem(f"The incoming checkpoint would remove the tracked tool source {file!r}. "
                          "Use a separate checkout for that historical branch.")
    protect_local_files(code, source["tree"], target["tree"])
    journal = store.control / "switch.json"
    atomic(journal, jsonbytes({"from": source, "to": target, "phase": "prepared"}))
    finish_switch(store)


def finish_switch(store):
    code, journal = store.code, store.control / "switch.json"
    if not journal.exists():
        return
    tx = json.loads(journal.read_bytes())
    a, b = tx["from"], tx["to"]
    check_repo(code)
    check_checkout_hooks(code)
    for side in (a, b):
        require(ref(code, side["branch"]) == side["base"], f"Branch {side['branch']} moved during the switch.")
    ensure_available(code, b["branch"])
    require(branch(code) in (a["branch"], b["branch"]), "HEAD changed during the switch. Preserve your new work.")
    with index(code) as alt:
        real = index_tree(code, alt)
    require(real in (a["index"], b["index"]), "Index changed during the switch. Preserve your new work.")
    def matches_target():
        return (removed_paths_absent(code, a["tree"], b["tree"]) and
                capture(code, b["index"], b["base"])[0] == b["tree"])
    if tx["phase"] == "prepared" or (tx["phase"] == "applying" and not matches_target()):
        require(capture(code, a["index"], a["base"])[0] == a["tree"],
                "Files changed during the switch. Both task states remain. Preserve intervening edits before recover.")
        tx["phase"] = "applying"
        atomic(journal, jsonbytes(tx))
        apply_tree(code, a["tree"], b["tree"])
    require(matches_target(), "Incoming tree verification failed. Both task states remain.")
    if tx["phase"] != "applied":
        tx["phase"] = "applied"
        atomic(journal, jsonbytes(tx))
    if branch(code) != b["branch"]:
        git(code, "symbolic-ref", "-m", "task switch", "HEAD", b["branch"])
    if real != b["index"]:
        git(code, "read-tree", b["index"])
    require(ref(code, "HEAD") == b["base"] and capture(code) == (b["tree"], b["index"]),
            "Final branch, working tree or index mismatch. Both checkpoints remain.")
    tasks, updated = store.tasks(), []
    for side, status in ((a, "paused"), (b, "in-progress")):
        if side["task"]:
            task = task_by_id(tasks, side["task"])
            if task[1]["status"] == "done":
                continue
            desired = "blocked" if task[1]["blockers"] else status
            if task[1]["status"] != desired:
                task[1].update(status=desired, updated=now())
                updated.append(task)
    if updated:
        store.update(tasks, updated, {}, "Switch to " + b["task"])
    journal.unlink()
    print(f"Active {b['task']} · {b['branch'][11:]} · incoming tree and index match.")


def resume(store, tid):
    code = store.code
    task = task_by_id(store.tasks(), tid)
    folder, meta, body = task
    print(f"# {tid} · {meta['title']}\n\n{body.strip()}")
    log = textfile(inside(store.root, folder + "/log.md"))
    last = log.rfind("\n## " + tid + "/")
    print("\n## Latest log\n" + (log[last:] if last >= 0 else log).strip())
    actual_branch = optional(code, "symbolic-ref", "-q", "HEAD") or "(detached)"
    right_branch = actual_branch == "refs/heads/" + meta["branch"]
    print(f"\n## Workspace\nBranch: {actual_branch} (expected refs/heads/{meta['branch']}).")
    cp = load_cp(store, task)
    if not cp:
        print("No checkpoint yet. Code status: none. Validation pending.")
        for gap in need_gaps({}, needs(code, meta["needs"])):
            print("Required file: " + gap)
        return
    proof_path = store.control / "restore-proof.json"
    if proof_path.is_file():
        proof = json.loads(proof_path.read_bytes())
        if proof.get("checkpoint") == cp["id"] and proof.get("tree") == cp["tree"]:
            print(f"Restore-tested {proof['restored']} · backup {proof['backup'][:12]} · validation {proof['validation']}.")
    head = ref(code, "HEAD")
    print(f"Base {cp['base']} · current HEAD {head}.")
    if head != cp["base"]:
        print("Commits on either side (checkpoint base < | current >):")
        print(val(code, "log", "--left-right", "--oneline", "-12", cp["base"] + "..." + head) or "(same commit)")
    try:
        check_repo(code)
        live, staging = capture(code)
    except Problem as error:
        print(f"Code comparison unavailable: {error}\nValidation pending.")
        return
    matches = live == cp["tree"]
    print(f"Code tree: {'exact' if matches else 'drift'} · {live}. Index: {'exact' if staging == cp['index'] else 'drift'}.")
    if not matches:
        for row in changed(code, cp["tree"], live):
            print(f"  {json.dumps(row['path'], ensure_ascii=False)} (+{row['added']}/−{row['removed']})")
    inventory, env = needs(code, meta["needs"]), environment(code)
    gaps = need_gaps(cp["needs"], inventory)
    print("Required files: " + ("; ".join(gaps) if gaps else "match" if inventory else "none configured") + ".")
    print("Environment: " + ("probe unavailable" if not env_ready(env) else "matches" if cp["environment"] == env else "changed") + ".")
    print("Latest check: " + verification_line(cp["verification"]))
    if cp["last_verified"]:
        vcp = load_cp(store, task, cp["last_verified"])
        v = vcp["verification"]
        p = inside(store.root, folder + "/" + v["evidence"])
        if vcp["tree"] != live:
            state = "stale — code changed"
        elif not p.is_file() or file_digest(p) != v["sha256"]:
            state = "pending — saved evidence missing or changed"
        elif cp.get("verification_issue"):
            state = "pending — " + cp["verification_issue"]
        elif not right_branch or vcp["base"] != head or not same_inputs(vcp["needs"], inventory) or vcp["environment"] != env or not env_ready(env):
            state = "pending — branch, required inputs or environment differ"
        else:
            state = "verified for this tree (recorded run)"
        print(f"Last evidenced pass: {vcp['id']} · {state} · {v['evidence']} · {v['result']}")
    else:
        print("Last evidenced pass: none.")
    print(f"Next action: {meta['next_action']}")


# Local bundle backup

EXPORT = "refs/task-monitor/export"
VERIFIED = "refs/task-monitor/verified"
RECORDS = "refs/task-monitor/prepared-records"
INCOMING = "refs/task-monitor/incoming"
BUNDLE = "task-monitor.bundle"
DEFAULT_BRANCH = "task-monitor/backups"
CHECKPOINT = re.compile(r"T-\d{3,}/C\d+\Z")


def read_json(path):
    return json.loads(path.read_bytes()) if path.exists() else None


def identity(cfg):
    return sha(jsonbytes([cfg["kind"], cfg["location"], cfg["branch"]]))


def safe_destination(code, path):
    require(path and "://" not in str(path), "Choose a filesystem folder outside the project, not a URL.")
    path = Path(path).expanduser().resolve()
    require(path != code and code not in path.parents, "Choose a backup directory outside the project.")
    return path


def folder_settings(directory, project=None):
    require(directory and "://" not in str(directory), "Choose an existing filesystem location for the backup.")
    cfg = dict(kind="folder", location=str(Path(directory).expanduser().resolve()), branch=DEFAULT_BRANCH)
    if project:
        cfg["project"] = project
    return cfg


def config(store, directory=None):
    path = store.control / "backup.json"
    previous = read_json(path) or {}
    if previous and directory is None:
        require(previous.get("kind") == "folder",
                "A previous edition selected a Git remote. Choose a folder using configure --backup-dir PATH.")
        safe_destination(store.code, previous["location"])
        return previous
    project = previous.get("project") or str(uuid.uuid4())
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", store.code.name) or "project"
    home = Path(os.environ.get("TASKMONITOR_HOME") or Path.home() / ".copilot-task-monitor")
    dest = safe_destination(store.code, directory or home / "backups" / (name + "-" + project[:8]))
    cfg = folder_settings(dest, project)
    if previous != cfg and (dest / BUNDLE).exists():
        oid = advertised(store.code, cfg)
        receipt = read_json(store.control / "receipt.json") or {}
        require(oid == receipt.get("oid") and ref(store.code, VERIFIED) == oid
                and manifest(store.code, oid).get("project") == project,
                "This folder contains a different backup. Choose a new dedicated folder or the last verified copy.")
    dest.mkdir(parents=True, exist_ok=True)
    atomic(path, jsonbytes(cfg))
    return cfg


def location(cfg):
    require(cfg.get("kind") == "folder", "The copy-and-paste edition reads filesystem backups.")
    return str(Path(cfg["location"]) / BUNDLE)


def advertised(repo, cfg):
    bundle = Path(location(cfg))
    require(bundle.parent.is_dir(), f"Backup directory is unavailable: {bundle.parent}")
    if not bundle.exists():
        return None
    rows = val(repo, "bundle", "list-heads", str(bundle), EXPORT).splitlines()
    bits = rows[0].split() if len(rows) == 1 else []
    require(len(bits) == 2 and bits[1] == EXPORT and re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", bits[0]),
            "The existing file is not a Task Monitor backup.")
    return bits[0]


def manifest(repo, oid):
    raw = git(repo, "cat-file", "blob", oid + ":manifest.json").stdout
    data = json.loads(raw)
    require(data.get("format") == "copilot-task-monitor/1", "Unsupported backup format.")
    return data


def init_repo(parent, path, oid, bare=False):
    args = ["init", "-q", "--object-format=" + ("sha256" if len(oid) == 64 else "sha1")]
    git(parent, *args, *(["--bare"] if bare else ["-b", "task-recovery-bootstrap"]), str(path))


def receive(repo, cfg, expected):
    git(repo, "bundle", "verify", location(cfg))
    git(repo, "fetch", "-q", "--no-tags", "--no-write-fetch-head", "--no-recurse-submodules", "--",
        location(cfg), "+" + EXPORT + ":" + INCOMING)
    require(ref(repo, INCOMING) == expected, "Backup changed during read-back. Retry.")
    git(repo, "fsck", "--connectivity-only", "--no-reflogs", "--no-dangling", expected)
    return manifest(repo, expected)


def verify(repo, cfg, expected):
    require(advertised(repo, cfg) == expected, "The published backup reference failed read-back.")
    with tempfile.TemporaryDirectory(prefix="task-monitor-readback-") as d:
        target = Path(d) / "proof.git"
        init_repo(repo, target, expected, bare=True)
        return receive(target, cfg, expected)


def checkpoint_refs(repo, namespace):
    table = val(repo, "for-each-ref", "--format=%(refname:strip=2)%09%(objectname)", namespace)
    return dict(line.split("\t", 1) for line in table.splitlines())


def collect(store, earlier):
    code = store.code
    tasks = store.tasks()
    branches = {}
    base = val(code, "config", "--local", "taskmonitor.baseRef")
    checkpoints, blobs = {}, {}
    code_refs = checkpoint_refs(code, "refs/ckpt")
    staged_refs = checkpoint_refs(code, "refs/ckpt-index")
    # Compare immutable manifest blob IDs in one Git walk, including records
    # moved into archive. Old, already verified checkpoints require no Git calls.
    committed = {}
    for row in git(store.root, "ls-tree", "-rz", "HEAD").stdout.split(b"\0"):
        if row:
            header, path = row.split(b"\t", 1)
            committed[os.fsdecode(path)] = header.split()[2].decode()
    docs = {}
    for tid, (folder, meta, body) in sorted(tasks.items()):
        branchname = "refs/heads/" + meta["branch"]
        branches[branchname] = ref(code, branchname)
        for cp_file in sorted(inside(store.root, folder + "/checkpoints").glob("C*.json")):
            key = tid + "/" + cp_file.stem
            blob = committed.get(f"{folder}/checkpoints/{cp_file.name}")
            require(blob, f"Checkpoint manifest is uncommitted or missing: {key}")
            pair = [code_refs.get(key), staged_refs.get(key)]
            known = earlier.get("manifest_blobs", {}).get(key)
            if known:
                require(known == blob and earlier["checkpoints"].get(key) == pair,
                        f"Previously published checkpoint {key} was modified.")
            else:
                cp = load_cp(store, (folder, meta, body), cp_file.stem)
                require(pair == [cp["snapshot"], cp["index"]], f"Inconsistent checkpoint refs for {key}.")
            checkpoints[key], blobs[key] = pair, blob
        if meta["last_checkpoint"]:
            require(tid + "/" + meta["last_checkpoint"] in checkpoints, f"Latest manifest for {tid} is missing.")
        if meta["last_durable"] != meta["last_checkpoint"]:
            meta["last_durable"] = meta["last_checkpoint"]
            docs[folder + "/task.md"] = document(meta, body).encode()
    require(set(code_refs) == set(staged_refs) == set(checkpoints) and
            earlier.get("checkpoints", {}).keys() <= checkpoints.keys(),
            "Task records and checkpoint references disagree. Preserve the records and repair the missing reference or manifest.")
    branches[base] = ref(code, base)
    require(all(branches.values()), "A recorded task or default branch is missing.")
    for tip in set(branches.values()):
        tree_guard(code, tip)
    docs["INDEX.md"] = render_index(tasks).encode()
    # Unsaved narrative and manually supplied evidence deserve an explicit checkpoint.
    require(not git(store.root, "status", "--porcelain", "-z").stdout,
            "Records contain uncommitted edits. Checkpoint the handoff or commit the intended records before backup.")
    tx = store.prepare("Record verified checkpoint coverage", docs)
    records = tx["after"] if tx else ref(store.root, "HEAD")
    return dict(format="copilot-task-monitor/1", records=records, records_branch=branch(store.root),
                base=base, branches=branches, checkpoints=checkpoints, manifest_blobs=blobs), tx


def make_export(store, data, previous):
    code = store.code
    git(store.root, "update-ref", RECORDS, data["records"])
    git(code, "fetch", "-q", "--no-tags", "--no-write-fetch-head", "--no-recurse-submodules", "--",
        str(store.root), "+" + RECORDS + ":" + RECORDS)
    # Plain tree links keep separately staged blobs reachable through any Git transport.
    lines = [f"040000 tree {pair[1]}\t{key.replace('/', '-')}\n" for key, pair in data["checkpoints"].items()]
    stages = val(code, "mktree", data="".join(lines).encode())
    blob = val(code, "hash-object", "-w", "--stdin", data=jsonbytes(data))
    tree = val(code, "mktree", data=f"100644 blob {blob}\tmanifest.json\n040000 tree {stages}\tstaging\n".encode())
    already = manifest(code, previous)["checkpoints"] if previous else {}
    parents = [data["records"], *data["branches"].values()]
    parents.extend(pair[0] for key, pair in data["checkpoints"].items() if already.get(key) != pair)
    if previous:
        parents.insert(0, previous)
    # Write the commit body to stdin to support large initial imports on Windows.
    author = val(code, "var", "GIT_AUTHOR_IDENT", env=internal_identity(code))
    committer = val(code, "var", "GIT_COMMITTER_IDENT", env=internal_identity(code))
    head = [f"tree {tree}", *(f"parent {oid}" for oid in dict.fromkeys(parents)),
            "author " + author, "committer " + committer, "", "Task Monitor backup", ""]
    oid = val(code, "hash-object", "-t", "commit", "-w", "--stdin", data="\n".join(head).encode())
    git(code, "update-ref", EXPORT, oid)
    return oid


def transmit(repo, cfg, before, after):
    folder = Path(cfg["location"])
    with lock(folder / ".task-monitor-lock"):
        require(advertised(repo, cfg) == before, "Another writer changed the backup directory. Restore or reconcile first.")
        with tempfile.TemporaryDirectory(prefix=".task-publish-", dir=folder) as tmp:
            path = Path(tmp) / BUNDLE
            git(repo, "bundle", "create", str(path), EXPORT)
            git(repo, "bundle", "verify", str(path))
            require(val(repo, "bundle", "list-heads", str(path), EXPORT).split()[0] == after,
                    "Generated bundle does not contain the expected commit.")
            os.replace(path, folder / BUNDLE)


def accept(store, cfg, oid, data, tx=None):
    require(data["project"] == cfg["project"], "The backup belongs to a different project.")
    receipt = dict(destination=identity(cfg), oid=oid, records=data["records"], verified=now())
    git(store.code, "update-ref", VERIFIED, oid)
    atomic(store.control / "receipt.json", jsonbytes(receipt))
    if tx and ref(store.root, "HEAD") in (tx["before"], tx["after"]):
        store.publish(tx)


class ProgressViewPending(Problem):
    """The recovery bundle is verified but the browsable copy needs attention."""


def progress_git(path, *args):
    # This generated checkout has no remote and does not need checkout or fetch hooks.
    return git(path, "-c", "core.hooksPath=" + str(path / ".git" / "task-monitor-no-hooks"), *args)


def view_matches(view, project, revision=None):
    require(not view.is_symlink() and view.is_dir() and (view / ".git").is_dir()
            and not (view / ".git").is_symlink() and view.resolve() == view,
            f"Keep the existing progress path intact and choose a dedicated folder: {view}")
    require(optional(view, "config", "--local", "--get", "taskmonitor.progressProject") == project,
            f"The existing progress directory belongs to another workflow: {view}")
    require(not git(view, "status", "--porcelain", "-z", "--ignored", "--untracked-files=all").stdout,
            f"The readable progress copy has edits. Preserve or move it aside before refreshing: {view}")
    if revision:
        require(ref(view, "HEAD") == revision, "Readable progress is behind the verified records. Run backup to refresh it.")


def checkout_records(store, view, revision):
    # Transfer records only, using the local object store. No remote name or network URL is configured.
    if ref(view, "HEAD") != revision:
        progress_git(view, "fetch", "--no-tags", "--no-write-fetch-head", "--no-recurse-submodules",
                     "--no-auto-maintenance", "--", str(store.root), revision)
        if ref(view, "HEAD"):
            progress_git(view, "merge-base", "--is-ancestor", "HEAD", revision)
        progress_git(view, "switch", "--no-overwrite-ignore", "--detach", revision)
    require(ref(view, "HEAD") == revision, "Readable progress did not reach its verified records revision.")


def refresh_progress(store, cfg, oid, revision):
    folder = Path(cfg["location"])
    view = folder / "progress"
    try:
        with lock(folder / ".task-monitor-lock"):
            require(advertised(store.code, cfg) == oid, "A newer bundle was published. Retry from its writer.")
            if view.exists() or view.is_symlink():
                view_matches(view, cfg["project"])
                checkout_records(store, view, revision)
            else:
                with tempfile.TemporaryDirectory(prefix=".task-progress-", dir=folder) as tmp:
                    new = Path(tmp) / "progress"
                    init_repo(folder, new, revision)
                    progress_git(new, "config", "--local", "taskmonitor.progressProject", cfg["project"])
                    checkout_records(store, new, revision)
                    if os.name == "nt":
                        os.rename(new, view)
                    else:
                        view.mkdir()
                        try:
                            os.replace(new, view)
                        except BaseException:
                            view.rmdir()
                            raise
            view_matches(view, cfg["project"], revision)
    except (Problem, OSError) as error:
        raise ProgressViewPending(f"Recovery bundle verified at {location(cfg)}. Readable progress refresh is pending: "
                                  f"{error}. Retry with backup after resolving the folder issue.") from error


def backup(store):
    cfg = config(store)
    current = advertised(store.code, cfg)
    receipt = read_json(store.control / "receipt.json") or {}
    prev = receipt.get("oid") if receipt.get("destination") == identity(cfg) else None
    if current and not prev and current == receipt.get("oid") and ref(store.code, VERIFIED) == current:
        require(manifest(store.code, current).get("project") == cfg["project"], "Backup belongs to another project.")
        prev = current  # The same verified bundle can be relocated to a new filesystem path.
    pending_path = store.control / "backup-pending.json"
    pending = read_json(pending_path) or {}
    # A transfer may have completed before the client recorded its acknowledgement.
    if current and pending.get("oid") == current and pending.get("destination") == identity(cfg):
        accept(store, cfg, current, verify(store.code, cfg, current), pending.get("records_tx"))
        pending_path.unlink(missing_ok=True)
        prev = current
    require(current == prev, "Backup destination changed or belongs to another project. Use restore or choose an empty destination.")
    earlier = manifest(store.code, prev) if prev else {}
    data, tx = collect(store, earlier)
    data["project"] = cfg["project"]
    if prev:
        if all(earlier.get(k) == v for k, v in data.items()):
            accept(store, cfg, prev, verify(store.code, cfg, prev), tx)
            refresh_progress(store, cfg, prev, data["records"])
            print(f"Backup verified {prev[:12]} · {len(data['checkpoints'])} checkpoints.")
            return
    data["saved"] = now()
    oid = make_export(store, data, prev)
    atomic(pending_path, jsonbytes(dict(destination=identity(cfg), oid=oid, records_tx=tx)))
    transmit(store.code, cfg, prev, oid)
    readback = verify(store.code, cfg, oid)
    require(readback == data, "Backup manifest differs after publication.")
    accept(store, cfg, oid, data, tx)
    pending_path.unlink(missing_ok=True)
    refresh_progress(store, cfg, oid, data["records"])
    print(f"Backup verified {oid[:12]} · code, staged content and records · {len(data['checkpoints'])} checkpoints.")


def auto_backup(store, local=False):
    if local:
        return
    try:
        backup(store)
    except ProgressViewPending:
        raise
    except (Problem, OSError) as err:
        raise Problem(f"Local work is saved. Backup is pending: {err} Retry the pasted script with backup.")


def summary(store, live=False):
    cfg = read_json(store.control / "backup.json")
    if not cfg:
        require(not live, "No backup has been made. Run the pasted script with backup.")
        print("Backup: local records only. No backup folder has been selected yet.")
        return
    if cfg.get("kind") != "folder":
        require(not live, "Select a folder with configure --backup-dir PATH to verify backups in this edition.")
        print("Backup: an earlier edition selected a remote. Choose a folder for offline backup.")
        return
    receipt = read_json(store.control / "receipt.json") or {}
    dest = location(cfg)
    print("Backup destination: " + dest)
    print("Readable progress: " + str(Path(cfg["location"]) / "progress" / "INDEX.md"))
    current = receipt.get("oid") if receipt.get("destination") == identity(cfg) else None
    if not current:
        require(not live, "No verified backup on this destination. Run the pasted script with backup.")
        print("Backup: no read-back recorded for this destination.")
        return
    if live:
        saved = verify(store.code, cfg, current)
        view_matches(Path(cfg["location"]) / "progress", cfg["project"], saved["records"])
    label = "match" if receipt["records"] == ref(store.root, "HEAD") else "have newer local commits"
    print(f"Backup {current[:12]} verified {receipt['verified']}. Records {label}.")


# Completion and weekly reports

def done(store, args):
    tasks = store.tasks()
    folder, meta, body = task_by_id(tasks, args.id)
    if meta["status"] == "done":
        print(f"{args.id} is archived.")
        return
    require(not meta["blockers"], "Resolve the recorded blocker and checkpoint the updated handoff.")
    cp = load_cp(store, tasks[args.id])
    require(cp and branch(store.code) == "refs/heads/" + meta["branch"] and ref(store.code, "HEAD") == cp["base"]
            and capture(store.code) == (cp["tree"], cp["index"]), "Make a final checkpoint on the active task branch.")
    require(not git(store.root, "status", "--porcelain", "-z", "--", folder).stdout,
            "Checkpoint edits to this task before archiving.")
    match = re.search(r"(?ms)^### Acceptance criteria\s*\n(.*?)(?=^## |\Z)", body)
    require(match, "The task needs numbered acceptance criteria.")
    required = set(re.findall(r"(?m)^- (AC\d+)\.", match[1]))
    evidence = {}
    for link in args.accept or []:
        key, sep, ck = link.partition("=")
        require(sep and re.fullmatch(r"C\d+", ck) and key not in evidence, "Use one --accept AC1=C01 per criterion.")
        evidence[key] = ck
    require(required and set(evidence) == required, "Provide a verified checkpoint for each criterion: " + ", ".join(sorted(required)))
    actual_env, required_files = environment(store.code), needs(store.code, meta["needs"])
    proofs = []
    for criterion, cid in sorted(evidence.items()):
        v = load_cp(store, tasks[args.id], cid)
        verification = v["verification"]
        require(verification["state"] == "verified" and v["tree"] == cp["tree"] and v["base"] == cp["base"]
                and required_files == v["needs"] and actual_env == v["environment"] and env_ready(actual_env)
                and all(n["present"] for n in required_files.values()), f"{criterion} needs an applicable evidenced pass.")
        for newer in range(int(cid[1:]) + 1, int(meta["last_checkpoint"][1:]) + 1):
            r = load_cp(store, tasks[args.id], f"C{newer:02d}")
            if r["tree"] == v["tree"] and r["verification"].get("argv") == verification.get("argv"):
                require(r["verification"]["state"] == "verified",
                        f"{criterion} has a later unsuccessful check. Run the final assertion again.")
        proof = inside(store.root, folder + "/" + verification["evidence"])
        require(proof.is_file() and file_digest(proof) == verification["sha256"], f"{criterion} evidence differs.")
        proofs.append(f"- {criterion} · {cid} · {verification['evidence']}")
    archived = "archive/" + folder
    require(not inside(store.root, archived).exists(), "Archive folder already exists.")
    meta.update(status="done", updated=now(), next_action="Completed")
    body = body.rstrip() + "\n\n## Completion evidence\n\n" + "\n".join(proofs) + "\n"
    files = items(git(store.root, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", folder).stdout)
    outputs = {}
    for path in files:
        outputs["archive/" + path] = inside(store.root, path).read_bytes()
        outputs[path] = None
    outputs[archived + "/log.md"] += ("\n## Completed · " + meta["updated"] + "\n" + "\n".join(proofs) + "\n").encode()
    store.update(tasks, [(archived, meta, body)], outputs, "Archive " + args.id)
    refresh_checkpoint_report(store)
    print(f"Archived {args.id} with {len(proofs)} evidenced acceptance criteria.")


def metric_lines(raw):
    for line in raw.decode(errors="replace").splitlines():
        if not line.startswith("TASK_METRIC "):
            continue
        try:
            obj = json.loads(line[12:])
            fields = ("name", "scope", "denominator_definition", "as_of")
            valid = isinstance(obj, dict) and all(isinstance(obj.get(k), str) and obj[k].strip() for k in fields)
            if not valid:
                continue
            date.fromisoformat(obj["as_of"])
            n, d = obj["numerator"], obj["denominator"]
            if type(n) is int and type(d) is int and 0 <= n <= d and d > 0:
                yield obj
        except (ValueError, KeyError, TypeError):
            continue


def weekly(store, ending):
    end = date.fromisoformat(ending) if ending else datetime.now(timezone.utc).date()
    start = end - timedelta(days=6)
    print(f"# Weekly progress · {start} to {end} (UTC)\n")
    count = 0
    for tid, task in sorted(store.tasks().items()):
        folder, meta, _ = task
        rows, prior, metrics = [], {}, {}
        paths = sorted(inside(store.root, folder + "/checkpoints").glob("C*.json"), key=lambda p: int(p.stem[1:]))
        for p in paths:
            cp = load_cp(store, task, p.stem)
            day = datetime.fromisoformat(cp["time"]).astimezone(timezone.utc).date()
            if day > end or day < start - timedelta(days=7):
                continue
            if day >= start:
                rows.append(cp)
            v = cp["verification"]
            if v["state"] != "verified" or not v.get("evidence"):
                continue
            blob = git(store.root, "cat-file", "blob", f"HEAD:{folder}/{v['evidence']}").stdout
            if sha(blob) != v["sha256"]:
                continue
            for m in metric_lines(blob.split(b"\n\n", 1)[-1]):
                key = tuple(m[k] for k in ("name", "scope", "denominator_definition"))
                slot = metrics if day >= start else prior
                slot[key] = (m, cp["id"], v["evidence"])
        if not rows:
            continue
        count += 1
        last = rows[-1]
        narrative = last.get("narrative", {})
        print(f"## {tid} · {meta['title']}\n")
        for line in dict.fromkeys(c.get("narrative", {}).get("done") for c in rows):
            if line:
                print("- " + line)
        print(f"- Latest recorded check · {last['id']} · {verification_line(last['verification'])}")
        for line in dict.fromkeys(c.get("narrative", {}).get("findings") for c in rows):
            if line:
                print("- Recorded finding · " + line)
        print("- Blocker · " + (narrative.get("blockers") or "none recorded at this checkpoint"))
        print("- Next action · " + (narrative.get("next_action") or "see the checkpoint log") + "\n")
        if metrics:
            print("| Metric and scope | As of | Numerator / denominator | Rate | Previous week | Change | Evidence |")
            print("| --- | --- | ---: | ---: | ---: | ---: | --- |")
        for key, (m, ck, evidence) in sorted(metrics.items()):
            rate = 100 * m["numerator"] / m["denominator"]
            old = prior.get(key)
            baseline = delta = "—"
            if old:
                prev = old[0]
                old_rate = 100 * prev["numerator"] / prev["denominator"]
                baseline = f"{prev['numerator']}/{prev['denominator']} ({old_rate:.2f}%, {prev['as_of']}, {old[1]})"
                delta = f"{rate - old_rate:+.2f} pp"
            print(f"| {cell(' · '.join(key))} | {m['as_of']} | {m['numerator']}/{m['denominator']} | {rate:.2f}% | "
                  f"{baseline} | {delta} | {ck} · {folder}/{evidence} |")
        if not metrics:
            print("No evidence-backed counts were recorded in this window.")
        print()
    if not count:
        print("No checkpoints in the selected week.")


# Workspace recovery

def save_weekly(store, ending=None):
    day = date.fromisoformat(ending) if ending else datetime.now(timezone.utc).date()
    name = f"reports/weekly-through-{day.isoformat()}.md"
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        weekly(store, day.isoformat())
    store.commit("Refresh weekly progress through " + day.isoformat(), {name: output.getvalue().encode("utf-8")})
    return name


def refresh_checkpoint_report(store):
    try:
        save_weekly(store)
    except (Problem, OSError, ValueError) as err:
        print(f"Weekly report refresh pending: {err}. Retry with weekly --save.", file=sys.stderr)


def fetch_records(repo, records, oid, refname):
    git(repo, "check-ref-format", refname)
    require(refname.startswith("refs/heads/"), "Invalid records branch.")
    git(repo, "update-ref", "refs/task-monitor/recovered-records", oid)
    git(records, "fetch", "-q", "--no-tags", "--no-write-fetch-head", "--", str(repo),
        "+refs/task-monitor/recovered-records:refs/task-monitor/records-input")
    git(records, "update-ref", refname, oid)
    git(records, "symbolic-ref", "HEAD", refname)
    git(records, "-c", "core.autocrlf=false", "read-tree", "--reset", "-u", oid)


def settings_from_args(args):
    if args.backup_dir:
        return folder_settings(args.backup_dir)
    root = optional(Path.cwd(), "rev-parse", "--show-toplevel")
    cfg = read_json(gitpath(Path(root), "task-monitor/backup.json")) if root else None
    require(cfg and cfg.get("kind") == "folder", "Specify the backup folder with --backup-dir PATH.")
    return cfg


def choose_task(tasks, selection):
    if selection:
        tid, _, cp = selection.partition("/")
        require(tid in tasks and (not cp or CHECKPOINT.fullmatch(selection)), f"Unknown task or checkpoint {selection!r}.")
        return tid, cp or tasks[tid][1]["last_checkpoint"]
    if not tasks:
        return None, None
    tid = max(tasks, key=lambda key: (tasks[key][1]["status"] == "in-progress", tasks[key][1]["updated"], key))
    return tid, tasks[tid][1]["last_checkpoint"]


def restore(args):
    cfg = settings_from_args(args)
    target = Path(args.to).expanduser().absolute()
    require(not os.path.lexists(target), "Restore needs a new destination. An existing file or directory is left intact.")
    parent = target.parent.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    original = optional(parent, "rev-parse", "--show-toplevel")
    require(not original, "Choose a new restore directory outside an existing working repository.")
    oid = advertised(parent, cfg)
    require(oid, "No backup is published at the selected destination.")
    with tempfile.TemporaryDirectory(dir=parent, prefix=".task-restore-") as temp:
        code = Path(temp) / "project"
        init_repo(parent, code, oid)
        data = receive(code, cfg, oid)
        require(re.fullmatch(r"[a-fA-F0-9-]{36}", data["project"]), "Invalid backup project ID.")
        for key, pair in data["checkpoints"].items():
            require(CHECKPOINT.fullmatch(key) and len(pair) == 2, "Invalid checkpoint entry in backup.")
            for prefix, value, kind in zip(("refs/ckpt/", "refs/ckpt-index/"), pair, ("commit", "tree")):
                require(val(code, "cat-file", "-t", value) == kind, "Invalid checkpoint object.")
                git(code, "update-ref", prefix + key, value)
        default = data["base"]
        require(default in data["branches"], "Missing the saved default branch.")
        for name, value in data["branches"].items():
            require(name.startswith("refs/heads/"), "Invalid task branch.")
            git(code, "check-ref-format", name)
            git(code, "update-ref", name, value)
        store = Store(code, gitpath(code, "task-monitor"))
        init_repo(code, store.root, oid)
        fetch_records(code, store.root, data["records"], data["records_branch"])
        for key, fallback in (("user.name", "Task Monitor"), ("user.email", "task-monitor@localhost")):
            if not optional(store.root, "config", "--get", key):
                git(store.root, "config", "--local", key, fallback)
        tasks = store.tasks()
        tid, selected = choose_task(tasks, args.id)
        historical = bool(tid and selected and selected != tasks[tid][1]["last_checkpoint"])
        if historical:
            key = tid + "/" + selected
            require(key in data["checkpoints"], "Checkpoint is outside this backup.")
            original_name = Path(tasks[tid][0]).name + "/checkpoints/" + selected + ".json"
            revision = val(store.root, "log", "-1", "--format=%H", "--no-renames", "--diff-filter=A",
                           data["records"], "--", original_name)
            require(revision, "Historical records revision is unavailable.")
            fetch_records(code, store.root, revision, data["records_branch"])
            tasks = store.tasks()
            for _, meta, _ in tasks.values():
                t = tasks[meta["id"]]
                cp = load_cp(store, t)
                git(code, "update-ref", "refs/heads/" + meta["branch"], cp["base"] if cp else meta["created_base"])
            # Future checkpoint numbers and branches belong to the newer timeline.
            for key in data["checkpoints"]:
                owner, number = key.split("/")
                last = tasks.get(owner, (None, {}, None))[1].get("last_checkpoint")
                if not last or int(number[1:]) > int(last[1:]):
                    for prefix in ("refs/ckpt/", "refs/ckpt-index/"):
                        git(code, "update-ref", "-d", prefix + key)
            wanted = {default, *("refs/heads/" + t[1]["branch"] for t in tasks.values())}
            for name in data["branches"].keys() - wanted:
                git(code, "update-ref", "-d", name)
        task = tasks.get(tid)
        cp = load_cp(store, task, selected) if task and selected else None
        active = "refs/heads/" + task[1]["branch"] if task else default
        base = cp["base"] if cp else (task[1]["created_base"] if task else data["branches"][default])
        tree = cp["tree"] if cp else ref(code, base + "^{tree}")
        staged = cp["index"] if cp else tree
        for obj in (base, tree, staged):
            tree_guard(code, obj)
        git(code, "update-ref", active, base)
        git(code, "symbolic-ref", "HEAD", active)
        git(code, "read-tree", "--reset", "-u", tree)
        git(code, "read-tree", staged)
        ex = gitpath(code, "info/exclude")
        atomic(ex, (ex.read_bytes() if ex.exists() else b"") + b"\n/.tasks/\n")
        git(code, "config", "--local", "taskmonitor.baseRef", default)
        require(capture(code) == (tree, staged), "Restored code or staged content differs from the saved trees.")
        if task and cp:
            for name, prior in cp["needs"].items():
                if prior.get("captured"):
                    proof = inside(store.root, task[0] + "/inputs/" + selected + "/" + safe_relative(name))
                    dest = inside(code, name)
                    require(file_digest(proof) == prior["sha256"], "Captured required-file digest mismatch.")
                    require(not dest.exists() or (dest.is_file() and file_digest(dest) == prior["sha256"]),
                            f"Existing file conflicts with captured input {name!r}.")
                    if git(code, "check-ignore", "-q", "--", name, check=False).returncode != 0:
                        # Local exclude rules are machine-specific. Recreate only the
                        # literal exception expressly authorized in the saved manifest.
                        pattern = "".join(("\\" + ch) if ch in "*?[]# !\\" else ch for ch in name)
                        atomic(ex, ex.read_bytes() + b"\n/" + pattern.encode() + b"\n")
                    require(git(code, "check-ignore", "-q", "--", name, check=False).returncode == 0,
                            f"Captured fixture {name!r} must stay outside the code tree.")
                    if not dest.exists():
                        atomic(dest, proof.read_bytes())
            require(capture(code) == (tree, staged), "A restored required file changed the saved Git state.")
        prepare_recovered_sources(code, base, tree, staged, (cp or {}).get("project_guides", []))
        if not historical:
            inherited = dict(cfg, project=data["project"])
            atomic(store.control / "backup.json", jsonbytes(inherited))
            accept(store, inherited, oid, data)
        # Publish the finished checkout as one directory move on this filesystem.
        if os.name == "nt":
            os.rename(code, target)  # Windows refuses to replace an existing destination.
        else:
            target.mkdir()  # Claim the destination exclusively before replacing our empty directory.
            try:
                os.replace(code, target)
            except BaseException:
                try:
                    target.rmdir()
                except OSError:
                    pass
                raise
    store = Store(target, gitpath(target, "task-monitor"))
    if historical:
        config(store)
    if task:
        print(f"Restored {tid}" + ("/" + selected if selected else "") + f" to {target}.")
    else:
        print(f"Restored the project to {target}.")
    print(f"Code fidelity: exact {tree}. Staged tree: exact {staged}.")
    print("Records and evidence: restored from verified Git objects.")
    proof_path = store.control / "restore-proof.json"
    restoration = dict(checkpoint=cp["id"] if cp else None, backup=oid, tree=tree, index=staged,
                       restored=now(), code="exact", validation="pending")
    atomic(proof_path, jsonbytes(restoration))
    if historical:
        print("Historical continuation has a separate backup destination. The newer timeline remains available.")
    if not cp:
        print("Validation: pending. This task has no saved test.")
        return 0
    required = needs(target, task[1]["needs"])
    gaps = need_gaps(cp["needs"], required)
    print("Required files: " + (", ".join(gaps) if gaps else "match" if required else "none configured") + ".")
    env = environment(target)
    same_env = env == cp["environment"] and env_ready(env)
    print("Environment: " + ("matches." if same_env else "changed or needs a local probe."))
    proof_cp = cp
    if cp.get("last_verified") and not cp["verification"].get("argv"):
        earlier = load_cp(store, task, cp["last_verified"])
        if earlier["tree"] == tree and earlier["needs"] == cp["needs"]:
            proof_cp = earlier
    test = proof_cp["verification"]
    if test.get("evidence"):
        evidence = inside(store.root, task[0] + "/" + test["evidence"])
        require(evidence.is_file() and file_digest(evidence) == test.get("sha256"), "Saved evidence digest mismatch.")
    if gaps:
        restoration["required_file_gaps"] = gaps
        atomic(proof_path, jsonbytes(restoration))
        print("Validation: pending required inputs. The recovered workspace is available.")
        return 3
    if args.run_check and valid_argv(test.get("argv")):
        outcome, evidence = check_result(target, {"argv": test["argv"]})
        print("Validation replay: " + outcome["state"] + " · " + outcome["result"])
        if evidence:
            print(evidence.split(b"\n\n", 1)[-1].decode(errors="replace").rstrip())
        require(capture(target) == (tree, staged), "Validation changed the recovered code. The backup remains available.")
        restoration["validation"] = outcome["state"]
        atomic(proof_path, jsonbytes(restoration))
        return 0 if outcome["state"] == "verified" else 3
    print("Validation: pending a fresh run. Recorded result: " + test["state"] + ".")
    return 3 if args.run_check else 0


# Command line




def destination(p):
    p.add_argument("--backup-dir", metavar="PATH", help="dedicated backup folder outside the project")


def local_option(p):
    group = p.add_mutually_exclusive_group()
    group.add_argument("--local", action="store_true", help="save this operation locally without publishing")
    group.add_argument("--durable", action="store_true", help="publish and verify the backup (default)")


def parser():
    cli = argparse.ArgumentParser(description="Copilot Task Monitor · task handoffs and verified backups")
    commands = cli.add_subparsers(dest="verb", required=True)
    p = commands.add_parser("init", help="initialize records, backup settings and a missing project guide")
    p.add_argument("--base")
    local_option(p)
    destination(p)
    p = commands.add_parser("configure", help="select a project backup destination and verify a backup")
    destination(p)
    p = commands.add_parser("new", help="create a task and branch")
    p.add_argument("title")
    p.add_argument("--request", required=True)
    p.add_argument("--criterion", action="append", required=True)
    p.add_argument("--step", action="append", required=True)
    p.add_argument("--next", dest="next_action")
    p.add_argument("--need", nargs=2, metavar=("PATH","RESTORE"), action="append", default=[])
    p.add_argument("--capture-need", nargs=2, metavar=("PATH","RESTORE"), action="append", default=[])
    p.add_argument("--base", metavar="REV")
    p.add_argument("--adopt-current", action="store_true", help="assign existing edits on this unmanaged branch to the new task")
    local_option(p)
    p = commands.add_parser("list", help="list tasks and show records/backup status")
    p.add_argument("--verify", action="store_true", help="read back the current external generation")
    p = commands.add_parser("plan", help="revise plan steps or criteria with a dated decision")
    p.add_argument("id")
    p.add_argument("--reason", required=True)
    p.add_argument("--step", nargs=3, action="append", default=[], metavar=("ID", "STATE", "TEXT"))
    p.add_argument("--criterion", nargs=3, action="append", default=[], metavar=("ID", "STATE", "TEXT"))
    local_option(p)
    p = commands.add_parser("note", help="save a finding or dead end immediately")
    p.add_argument("id")
    p.add_argument("text")
    p.add_argument("--ruled-out", action="store_true")
    local_option(p)
    p = commands.add_parser("checkpoint", help="save working code, staging, handoff and evidence")
    p.add_argument("id")
    p.add_argument("--input", metavar="FILE", required=True, help="JSON file, or - for stdin")
    local_option(p)
    p = commands.add_parser("switch", help="save the outgoing task and load the incoming task")
    p.add_argument("id")
    p.add_argument("--input", metavar="FILE", help="outgoing handoff, or - for stdin")
    local_option(p)
    p = commands.add_parser("resume", help="read the handoff and report drift")
    p.add_argument("id")
    commands.add_parser("backup", help="publish or retry all committed task records and checkpoints")
    p = commands.add_parser("restore", help="recover a new workspace, including saved staging and records")
    p.add_argument("id", nargs="?", help="task ID or T-001/C01")
    p.add_argument("--to", required=True, metavar="NEW_DIRECTORY")
    p.add_argument("--run-check", action="store_true", help="replay the recorded command in the recovered project")
    destination(p)
    p = commands.add_parser("done", help="archive work with evidence for each criterion")
    p.add_argument("id")
    p.add_argument("--accept", action="append", metavar="AC1=C01")
    local_option(p)
    p = commands.add_parser("weekly", help="build a seven-day Markdown progress report")
    p.add_argument("--ending", metavar="YYYY-MM-DD")
    p.add_argument("--save", action="store_true", help="save and back up the dated derived report")
    local_option(p)
    p = commands.add_parser("overview", help="read task indexes for specified projects")
    p.add_argument("projects", nargs="+")
    p = commands.add_parser("doctor", help="check the pasted source, guide and backup")
    p.add_argument("--verify", action="store_true")
    commands.add_parser("recover", help="complete an interrupted local operation")
    return cli


def normalized_source(raw):
    return raw.decode("utf-8-sig").replace("\r\n", "\n").rstrip("\n")


def source_digest(raw):
    text = normalized_source(raw)
    # The checksum covers all source lines including the final marker, except the digest itself.
    pattern = r'(?m)^EDITION_DIGEST = "[a-f0-9]{64}"$'
    data = re.sub(pattern, 'EDITION_DIGEST = "' + "0" * 64 + '"', text, count=1).encode()
    return sha(data)


def direct_guide(data):
    try:
        body = normalized_source(data)
    except UnicodeDecodeError:
        return False
    front = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", body, re.S)
    return bool(front and re.search(r'(?m)^name:\s*task\s*$', front[1]) and "task.py" in body)


def ensure_pasted_sources(repo, create_guide=False):
    py = inside(repo, SCRIPT_REL)
    md = inside(repo, GUIDE_REL)
    require(py.is_file(), f"Paste the Python source at {SCRIPT_REL}.")
    if not md.exists() and create_guide:
        require(not ref(repo, "HEAD:" + GUIDE_REL) and not ref(repo, ":" + GUIDE_REL),
                "The tracked skill guide is missing from disk. Restore its intended contents first.")
        atomic(md, GUIDE_TEXT.encode("utf-8"))
    require(md.is_file() and direct_guide(md.read_bytes()),
            f"Paste the direct-run SKILL.md at {GUIDE_REL}, or use init to create a missing guide.")
    return py, md


def pasted_project_guides(repo):
    """Recognize exact untracked distribution copies. Custom/team instructions remain project files."""
    found = set()
    for name, source in PROJECT_GUIDES.items():
        path = repo / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 65536:
            continue
        try:
            if normalized_source(path.read_bytes()) == normalized_source(source.encode()):
                found.add(name)
        except (UnicodeError, FileNotFoundError):
            continue
    return found


def workspace_paths(repo, tracked):
    # Untracked copies stay visible to VS Code and to ordinary git status.
    # Exact distribution copies stay available across task branches until staged.
    paths = ["."]
    for name in (SCRIPT_REL, GUIDE_REL, *sorted(pasted_project_guides(repo))):
        if name not in tracked:
            paths.append(":(top,exclude,literal)" + name)
    return paths


def managed_status(code):
    tracked = set(tree_guard(code, ref(code, "HEAD")))
    cached = git(code, "--literal-pathspecs", "ls-files", "-z", "--", SCRIPT_REL, GUIDE_REL, *PROJECT_GUIDES).stdout
    tracked.update(items(cached))
    return git(code, "status", "--porcelain", "-z", "--", *workspace_paths(code, tracked)).stdout


def prepare_recovered_sources(code, base, tree, staged, project_guides):
    """Use the two plain project files after a recovery, preserving snapshot-owned paths."""
    tracked = set()
    for obj in (base, tree, staged):
        tracked.update(tree_guard(code, obj))
    guide = GUIDE_TEXT.encode()
    source = Path(__file__).resolve()
    if source.name == "task.py":
        sibling = source.with_name("SKILL.md")
        if sibling.is_file() and not sibling.is_symlink() and direct_guide(sibling.read_bytes()):
            guide = sibling.read_bytes()
    assets = {SCRIPT_REL: source.read_bytes(), GUIDE_REL: guide}
    assets.update({name: PROJECT_GUIDES[name].encode() for name in project_guides if name in PROJECT_GUIDES})
    for name, raw in assets.items():
        if name in tracked or any(name.startswith(parent + "/") or parent.startswith(name + "/") for parent in tracked):
            continue
        try:
            dest = inside(code, name)
        except Problem:
            continue
        if not dest.exists():
            atomic(dest, raw)
    require(capture(code) == (tree, staged), "Recovered source files would change the saved code or staged tree.")


def current_project(create=False):
    cwd = Path.cwd().resolve()
    root = optional(cwd, "rev-parse", "--show-toplevel")
    if not root:
        require(create, "Open the project folder. For a new project run the pasted script with init.")
        require(optional(cwd, "rev-parse", "--is-bare-repository") != "true",
                "Task Monitor needs a working checkout.")
        # Check the intended target before creating a repository in it.
        require(inside(cwd, SCRIPT_REL).is_file(), f"Run init from the project containing {SCRIPT_REL}.")
        git(cwd, "init", "-q", "-b", "main")
        root = str(cwd)
    code = Path(root).resolve()
    if not ref(code, "HEAD"):
        require(create, "This project has no Git commit. Run the pasted script with init to create an empty base.")
        ensure_pasted_sources(code, create_guide=True)
        empty = val(code, "mktree", data=b"")
        commit = val(code, "commit-tree", empty, "-m", "Initial empty base for local tasks", env=internal_identity(code))
        git(code, "update-ref", branch(code), commit, "0" * len(commit))
        print("Created an empty local base. Existing files and staged contents are available for the first task.")
    return code


def check_pasted_files(code):
    py, md = ensure_pasted_sources(code)
    raw = py.read_bytes()
    if source_digest(raw) == EDITION_DIGEST:
        print("Python source: complete, matches the copy-and-paste edition.")
    else:
        print("Python source: locally edited or an incomplete copy. Review it against your source.")
    guide_status = "matches the copy sheet" if normalized_source(md.read_bytes()) == normalized_source(GUIDE_TEXT.encode()) else "locally customized"
    print(f"Copilot guide: {guide_status} at {md.relative_to(code)}.")
    for name, source in PROJECT_GUIDES.items():
        file = code / name
        if not file.is_file():
            status = "absent (optional)" if name.endswith(".agent.md") else "absent (automatic task rules unavailable)"
        elif file.is_symlink():
            status = "symlink; check the project configuration"
        else:
            saved = normalized_source(file.read_bytes())
            status = "contains the copy-sheet text" if normalized_source(source.encode()) in saved else "locally customized; review"
        print(f"{name}: {status}.")


def main():
    args = parser().parse_args()
    require(sys.version_info >= (3, 9), "This source uses Python 3.9 or newer.")
    version = re.search(r"\b(\d+)\.(\d+)\.", val(Path.cwd(), "--version"))
    require(version and tuple(map(int, version.groups())) >= (2, 43), "Use an existing Git 2.43 or newer.")
    if args.verb == "restore":
        return restore(args)
    if args.verb == "overview":
        for project in args.projects:
            code = Path(val(Path(project), "rev-parse", "--show-toplevel")).resolve()
            store = Store(code, gitpath(code, "task-monitor"))
            store.validate()
            print(f"## {code}\n\n" + render_index(store.tasks()))
        return 0
    root = current_project(create=args.verb == "init")
    control = gitpath(root, "task-monitor")
    store = Store(root, control)
    if args.verb == "doctor":
        check_pasted_files(root)
        check_repo(root)
        if not (store.root / ".git").exists():
            require(not args.verify, "Task records start with your first task. There is no backup to verify yet.")
            print("Ready. Give Copilot your first work request.")
            return 0
    with lock(control):
        if args.verb == "recover":
            store.validate()
            store.recover()
            finish_switch(store)
            print("Local task operations are consistent.")
            if (control / "backup-pending.json").exists():
                backup(store)
            return
        require(not store.journal.exists() and not (control / "switch.json").exists(),
                "An interrupted operation is pending. Run the pasted script with recover.")
        if args.verb == "init" or not (store.root / ".git").exists():
            require(args.verb in ("init", "new", "list", "configure"),
                    "Give Copilot a new task, or run the pasted script with init.")
            ensure_pasted_sources(root, create_guide=args.verb == "init")
            base = store.init(getattr(args, "base", None) if args.verb == "init" else None)
            if args.verb == "init":
                if not args.local or args.backup_dir:
                    config(store, args.backup_dir)
                auto_backup(store, args.local)
                print(f"Task records ready. Common base {base}. Run the pasted Python file directly.")
                return
        else:
            store.validate()
        if args.verb == "configure":
            config(store, args.backup_dir)
            backup(store)
        elif args.verb == "new":
            new_task(store, args)
            auto_backup(store, args.local)
        elif args.verb == "list":
            list_tasks(store)
            summary(store, args.verify)
        elif args.verb == "plan":
            revise_plan(store, args)
            auto_backup(store, args.local)
        elif args.verb == "note":
            note(store, args)
            auto_backup(store, args.local)
        elif args.verb == "checkpoint":
            checkpoint(store, task_by_id(store.tasks(), args.id), payload(args.input))
            auto_backup(store, args.local)
        elif args.verb == "switch":
            switch(store, args.id, args.input, None if args.local else auto_backup)
            try:
                auto_backup(store, args.local)
            except Problem as err:
                raise Problem(f"Incoming task {args.id} is active. {err}")
        elif args.verb == "resume":
            resume(store, args.id)
        elif args.verb == "backup":
            backup(store)
        elif args.verb == "done":
            done(store, args)
            auto_backup(store, args.local)
        elif args.verb == "weekly":
            if args.save:
                name = save_weekly(store, args.ending)
                print(f"Saved .tasks/{name}")
                auto_backup(store, args.local)
            else:
                weekly(store, args.ending)
        elif args.verb == "doctor":
            summary(store, args.verify)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.stderr.reconfigure(errors="backslashreplace")
    try:
        sys.exit(main())
    except (Problem, OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(f"task: {error}")
    except KeyboardInterrupt:
        sys.exit("task: interrupted. Use the pasted script with recover if an operation is pending.")

# END OF COPILOT TASK MONITOR SOURCE
