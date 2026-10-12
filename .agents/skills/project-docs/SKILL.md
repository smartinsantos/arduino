---
name: project-docs
description: Project structure and documentation rules for this repo. Use when creating a project, changing a project's code, pins or libraries, editing its README, PLAN or schematics, or before committing.
---

# Project structure and docs

## Project shape

Every project is one numbered folder, created with `pio project init --board uno` and laid out like this:

```
N-project-<name>/
  platformio.ini   board, framework, libraries
  src/main.cpp     the sketch
  README.md        what it does, wiring summary, build and upload
  PLAN.md          phases, decisions, full pin map, task checklist (phased projects only)
  assets/          wiring schematic PDFs (one per phase in phased projects)
```

In a phased project, `PLAN.md` is the source of truth for decisions, pins and behavior. Read it before changing that project's code.

## Sync points

A project is **in sync** when its code and its docs describe the same thing. These are the places that drift:

| When this changes | These must match it |
|---|---|
| Pin constants in `src/main.cpp` | README pin table, `PLAN.md` pin table, schematic page 1 (diagram) and page 2 (connections table) |
| Behavior: LCD text, Serial output, timings, buttons, baud rate | README description, `PLAN.md` behavior table, schematic page 2 ("What it does" and troubleshooting tips) |
| Parts added or removed | README wiring section, `PLAN.md` decisions and pins, schematic diagram and parts list |
| `platformio.ini`: board, libraries, `monitor_speed` | README build section, `PLAN.md` libraries decision |
| Files added or removed | README layout section |
| A task or phase finished | `PLAN.md` task checkboxes, phase status tables in README and `PLAN.md` |

The check works both ways: a docs-only change has to match the code just as much.

## After changing a project

1. Go through every row of the sync table for the changed project. Read the actual README, `PLAN.md` and schematic (open the PDF) and compare them with the code; don't assume they still match.
2. If anything no longer matches, ask the user once whether to update the docs, listing each stale item by file:

   > `src/main.cpp` now shows the ID for 5 seconds. Out of date:
   > - README.md: "for 3 seconds"
   > - assets/phase-1-rfid-lcd.pdf, page 2: "What it does"
   >
   > Update README.md and the schematic?

3. Update what the user approves. Whatever they decline stays on the list of things out of sync.

This step is done when every row of the table has been checked and each stale item has been either fixed or reported to the user.

## Before committing

A commit goes in only when the project is in sync. Run *After changing a project* on everything about to be committed. If anything is still out of sync, including items the user chose not to update, hold the commit: tell the user what is out of sync and that the commit waits until code and docs match.

## Schematics

The PDFs in `assets/` are generated with Python ReportLab. The generator scripts are not committed, and ReportLab is not installed globally, so set up a throwaway virtualenv outside the repo, write a script there, and regenerate the whole PDF. Match the existing layout:

- **Page 1:** wiring diagram, with the Uno on the left, each part as a box, and GND/5V rails.
- **Page 2:** parts table, connections table, "If something is wrong" tips and "What it does".

Open the new PDF and check every pin and label against the code before calling it done.

## Writing style

READMEs, plans and schematics are written for a hobbyist wiring things on a breadboard: short plain sentences, tables for pins, explicit warnings (e.g. RC522 on 3.3V, never 5V).
