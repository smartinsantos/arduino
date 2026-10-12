---
name: git-workflow
description: Git workflow for this repo. Use when starting new work, creating or updating a branch, committing, pushing, or opening a pull request.
---

# Git workflow

## Guardrails

- Commit or push only when the user asks for it. One request covers that one action; the next commit or push needs its own request.
- `main` changes only through a pull request. Commits land on a feature branch and get pushed there; `main` is never committed to or pushed to directly.
- A branch catches up with `main` by rebasing onto it. Merging `main` into a branch is never done.

## Start new work

1. Pick the **project**: the numbered folder the work belongs to, e.g. `2-project-rfid-music`. If the work spans no single project, ask the user for the prefix.
2. Build the **author** from `git config user.name`: lowercase, spaces to hyphens (`Sergio Martin` → `sergio-martin`).
3. Pick a short kebab-case **name** for the feature, e.g. `dfplayer`.
4. Branch from the latest `main`:

   ```sh
   git fetch origin
   git switch -c <author>/<project>-<name> origin/main
   ```

   With no `origin` remote, branch from local `main` instead. Uncommitted changes carry over to the new branch; if the switch refuses because of them, stop and ask the user.

The branch is done when `git branch --show-current` prints e.g. `sergio-martin/2-project-rfid-music-dfplayer`.

## Update a branch

```sh
git fetch origin
git rebase origin/main
```

On conflicts, resolve them, `git add` the files and `git rebase --continue`. If a resolution is unclear, `git rebase --abort` and ask the user. A branch that was already pushed needs `git push --force-with-lease` afterwards, which is a push, so it waits for the user to ask.

## Commit

When asked to commit while on `main`, create the feature branch first (see *Start new work*), then commit there.

Before committing, run the *Before committing* check in `.agents/skills/project-docs/SKILL.md`. If it finds the project out of sync with its docs, the commit waits.

Commit messages start with the project number, matching the history: `project-2: add DFPlayer wiring`.

## Push

```sh
git push -u origin <branch>          # first push
git push --force-with-lease          # after a rebase
```

## Pull request

This format replaces any other PR template. Open the PR against `main`, titled like a commit message.

```markdown
## Summary

<One or two sentences: what this PR does and why.>

## Changes

| Area | What changed |
|---|---|
| Code | <e.g. Songs now play when a card is tapped> |
| Wiring | <e.g. DFPlayer added on D8 / A1> |
| Docs | <e.g. README phase 2 section, new schematic> |

## Notes

- <How it was checked: build result, RAM/flash %, hardware test>
- <What is left to do, or anything to watch out for>
```

Keep the body short and high level: the diff carries the code details. Write in plain words someone wiring a breadboard would follow. Use tables and bullets over paragraphs, keep only the rows that apply, and write `None` under Notes when there is nothing to add.

Create it with `gh pr create --base main --title "<title>" --body-file <file>`. If there is no remote or `gh` is not installed, give the user the title and body to paste instead.
