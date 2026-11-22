---
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
