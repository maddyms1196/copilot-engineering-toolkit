# GitHub Copilot Engineering Kit

Reusable GitHub Copilot custom agents, agent skills, and project instructions for Visual Studio Code. Use the kit to explore unfamiliar codebases, review changes, debug failures, and verify fixes.

## What's included

| Component | Use it for |
| --- | --- |
| [Explorer](agents/explorer.agent.md) | Trace how a feature works and find the files and tests involved. |
| [Reviewer](agents/reviewer.agent.md) | Review changes for regressions, edge cases, and test gaps. |
| [Engineering Pro](custom/engineering-pro.agent.md) | Work through broader engineering tasks from investigation to verification. |
| [Agent skills](skills/) | Load workflows for [code review](skills/code-review/), [codebase investigation](skills/codebase-investigation/), [complex tasks](skills/complex-task-execution/), [data analysis](skills/data-analysis/), [performance optimization](skills/performance-optimization/), [root-cause debugging](skills/root-cause-debugging/), [safe implementation](skills/safe-implementation/), and [testing and verification](skills/testing-verification/). |
| [Task Monitor](agents/task-monitor.agent.md) and [task skill](skills/task/) | Track tasks and plan changes, resume in a fresh chat, restore checkpointed code, and report measured weekly progress. |
| [Context Curator](agents/context-curator.agent.md) | Teach Copilot project vocabulary through conversation. It clarifies ambiguous definitions, checks relevant local evidence when available, and saves what you agree. |
| [Project instructions](copilot-instructions.md) | Give Copilot guidance on how to investigate, implement, and verify changes in your workspace. |

## Project structure

```text
copilot-engineering-toolkit
    ├── copilot-instructions.md
    ├── agents/
    │   ├── context-curator.agent.md
    │   ├── engineering-pro.agent.md
    │   ├── explorer.agent.md
    │   ├── reviewer.agent.md
    │   └── task-monitor.agent.md
    └── skills/
        ├── code-review/
        │   ├── SKILL.md
        │   └── references/
        │       └── security-checklist.md
        ├── codebase-investigation/
        │   └── SKILL.md
        ├── complex-task-execution/
        │   └── SKILL.md
        ├── data-analysis/
        │   ├── SKILL.md
        │   └── references/
        │       ├── sql-checks.md
        │       └── statistical-checks.md
        ├── performance-optimization/
        │   ├── SKILL.md
        │   └── references/
        │       └── profiling-tools.md
        ├── root-cause-debugging/
        │   └── SKILL.md
        ├── safe-implementation/
        │   └── SKILL.md
        ├── task/
        │   ├── SKILL.md
        │   └── task.py
        └── testing-verification/
            └── SKILL.md
```

## Quick start

Open the project where you want to use the kit in VS Code with GitHub Copilot enabled. Copy the components you want into that project:

| From this repository | Into your project |
| --- | --- |
| `agents/*.agent.md` or `custom/engineering-pro.agent.md` | `.github/agents/` |
| Selected folders from `skills/`, including their `SKILL.md` and any supporting files | `.github/skills/` |
| `copilot-instructions.md` | `.github/copilot-instructions.md` |

If your project already has a `copilot-instructions.md`, merge in the guidance you want. Open Copilot Chat and select a custom agent from the agent picker.

## Copy the task and vocabulary tools into a work project

Open files in this kit from your browser and copy their raw contents to the destinations below. In the work project, merge the **Task Monitor** and **Plain-English requests and shared project vocabulary** sections into existing project instructions. Use the complete root file when starting from scratch.

| Source in this kit | Destination in your work project |
| --- | --- |
| [copilot-instructions.md](copilot-instructions.md) | `.github/copilot-instructions.md` |
| [agents/task-monitor.agent.md](agents/task-monitor.agent.md) | `.github/agents/task-monitor.agent.md` |
| [agents/context-curator.agent.md](agents/context-curator.agent.md) | `.github/agents/context-curator.agent.md` |
| [skills/task/SKILL.md](skills/task/SKILL.md) | `.github/skills/task/SKILL.md` |
| [skills/task/task.py](skills/task/task.py) | `.github/skills/task/task.py` |

**Track engineering work.** Use your coding agent for normal work. Select Task Monitor for a task list, handoff or weekly update. The helper uses the machine's existing Python 3.9+ and Git 2.43+. Save the shared setup through your normal project workflow on the common base branch for new tasks. In an existing Git project, tell Copilot the dedicated folder you want outside the code checkout, or run `python .github/skills/task/task.py configure --backup-dir "PATH"` once using your real path and installed Python launcher. Then say “Track this investigation and save what we verify.” Open `progress/INDEX.md` and `progress/reports/` in the chosen folder. The file `task-monitor.bundle` holds the recovery backup. The helper uses local Git and does not push to GitLab or GitHub. A backup on the same disk covers loss of the checkout; device-loss recovery needs a surviving copy.

**Teach a term.** Select Context Curator and say “When I say X, I mean Y.” The agent asks about ambiguities, checks a relevant schema, query or data when useful, and creates `docs/project-context.md` when the first definition is clear. Your usual agent can use those saved definitions in a fresh chat. For one glossary across task branches, set the context-file path in the work project's instructions to a writable location outside the code tree, such as a sibling of the generated `progress/` folder. Back up an external glossary separately.

Publish the reusable source templates in this kit. Keep project definitions, task records, evidence and backup bundles in the local project environment. Use fictional examples when contributing to this kit.

## Example prompts

- **Explore a codebase** — Trace how configuration is loaded. Point to the entry point, relevant files, and existing tests. Keep the investigation read-only.
- **Review a change** — Review the current diff for likely regressions and missing tests. Include file references and explain when each issue would occur.
- **Debug a failure** — Use the root-cause debugging workflow to investigate this failing test. Show the evidence for the likely cause and propose a minimal fix.

## VS Code documentation

- [Custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [Agent skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [Custom instructions](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference)
