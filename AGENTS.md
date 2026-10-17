# AGENTS.md

Guidance for AI coding agents working in this repository.

## Layout

A collection of independent Arduino Uno R3 projects (ATmega328P, 16 MHz), one folder each, numbered in build order (`1-project-mini-piano`, `2-project-rfid-music`, ...). Each folder is a self-contained PlatformIO project (`env:uno`, `atmelavr`, `arduino` framework) with its own code and docs. There is no shared code between projects.

## Build and upload

Run PlatformIO from inside a project folder. If `pio` is not on `PATH`, use `~/.platformio/penv/bin/pio`.

```sh
~/.platformio/penv/bin/pio run                 # build; check the RAM/flash % it prints
~/.platformio/penv/bin/pio run -t upload       # flash the connected Uno
~/.platformio/penv/bin/pio device list         # the Uno reports VID:PID=2341:0043
```

With several serial devices connected, add `--upload-port <port>`. On Apple Silicon the AVR toolchain needs Rosetta 2. There are no automated tests: verification is a successful build plus the manual hardware checklist in the project's `PLAN.md` / README.

## Skills

Read and follow these before the work they cover:

- `.agents/skills/git-workflow/SKILL.md`: before creating a branch, committing, pushing, rebasing or opening a pull request.
- `.agents/skills/project-docs/SKILL.md`: before creating a project, after changing a project's code, pins or libraries, when editing its README, `PLAN.md` or schematics, and before committing.

## ATmega328P constraints

- 2KB SRAM, 32KB flash (0.5KB taken by the bootloader), 1KB EEPROM. When looking up registers, timers or peripheral limits, use the ATmega328P datasheet.
- Keep string literals in flash with `F()`, and keep RAM under about 75% after each build.
- In `2-project-rfid-music`, only D5, D6, D7 and A3 are free (see `PLAN.md`); D0/D1 stay free for USB serial. A new part needs a pin plan before code.
- Buttons are wired pin-to-GND with `INPUT_PULLUP` (pressed reads `LOW`).
