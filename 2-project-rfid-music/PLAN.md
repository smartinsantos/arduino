# RFID Music Box: Plan

A music box for a 4-year-old. Tap a card on the reader, and the songs in that card's folder play in order. The LCD shows the folder's title and the song number. A knob sets the volume, and three buttons handle previous, play/pause and next.

The work is split into three phases:

| Phase | What | Status |
|---|---|---|
| 1 | RFID reader and LCD: tap a card, see its ID | **Built**, waiting for a hardware test |
| 2 | MP3 player, card-to-folder table, volume knob, buttons | Planned. Code will be written once the DFPlayer Mini arrives |
| 3 | Put it all in a box | Constraints only. Needs its own design session after phase 2 works |

## Decisions

| Topic | Decision | Why |
|---|---|---|
| Board | Arduino **Uno** (the same board as the mini piano) | It's the board on hand. It fits, but only just: every pin except D0/D1 is used by phase 2 (see the pin table), the DFPlayer needs SoftwareSerial, and RAM is 2KB, so keep strings in flash with `F()`. |
| Display | **LCD1602**, 4-bit parallel wiring | 16x2 characters is enough for a title and "Song 2 of 7". The kit's 8x8 matrix and 7-segment displays can't show words well. |
| LCD contrast | **Fixed resistor** from V0 to GND (start with 1k ohm) | The kit's potentiometer is used for volume. |
| MP3 module | **DFPlayer Mini** (DFRobot, Amazon B089D5NLW1) | It plays from the microSD card we already have and is the most-used module with Arduino. Rejected: DFPlayer Pro (128MB built-in memory, few examples). |
| Speaker | **One** CQRobot 3W 8 ohm speaker (B0738NLFTG); the second is a spare | The DFPlayer's amp is mono. |
| Tags | **13.56 MHz** MIFARE Classic 1K cards or NTAG213 stickers | The RC522 reads only 13.56 MHz. 125 kHz tags will not work. |
| Card mapping | A table in `src/cards.h`: card ID, folder number, title | It's the only option that gives the LCD real titles. To add a card, read its ID off the screen, add a line and re-upload. |
| SD layout | Numbered folders `01`..`99`, files `001.mp3`..`255.mp3` | The DFPlayer only understands numbered folders. The readable name lives in `cards.h`. |
| Song count | Ask the module with `readFileCountsInFolder()` | Adding songs to a folder needs no code change. Fallback: move on until the module reports "file not found". |
| Volume | Potentiometer on A0, mapped to 0..`MAX_VOLUME` (start at 20 of 30) | Even a full turn stays safe for small ears. |
| Power | 5V/2A USB charger or power bank into the Uno's USB port | The DFPlayer takes power from the Uno's 5V pin. The RC522 uses the Uno's own 3.3V pin (no resistor or diode needed). A power bank makes it portable. |
| Libraries | `miguelbalboa/MFRC522`, `arduino-libraries/LiquidCrystal`, `dfrobot/DFRobotDFPlayerMini` (phase 2) | |
| Tests | None automated. A manual checklist per phase (below) | Same as the mini piano: it's mostly wiring and timing. |

## Pin assignments (Uno)

Every pin from D2 to A5 is spoken for once phase 2 is wired. D0/D1 stay free for USB (upload and Serial Monitor).

| Part | Part pin | Uno pin | Notes |
|---|---|---|---|
| RC522 | SDA (SS) | D10 | |
| RC522 | MOSI | D11 | Hardware SPI, fixed on the Uno. |
| RC522 | MISO | D12 | Hardware SPI. |
| RC522 | SCK | D13 | Hardware SPI. |
| RC522 | RST | D9 | |
| RC522 | 3.3V | **3.3V** | **Not 5V.** The Uno makes 3.3V itself; the pin is on the power header between RESET and 5V. |
| RC522 | GND | GND | IRQ is not connected. |
| LCD1602 | VSS, RW, K | GND | |
| LCD1602 | VDD | 5V | |
| LCD1602 | V0 | 1k ohm to GND | Contrast. Use a higher value if you see solid blocks, lower if the text is faint. |
| LCD1602 | A | 220 ohm to 5V | Backlight. |
| LCD1602 | RS, E | D2, D3 | |
| LCD1602 | D4, D5, D6, D7 | D4, D5, D6, D7 | Same numbers on both ends. LCD D0-D3 are not connected. |
| *Phase 2* | | | |
| DFPlayer | VCC, GND | 5V, GND | |
| DFPlayer | TX | D8 | SoftwareSerial RX. |
| DFPlayer | RX | A1 **through 1k ohm** | SoftwareSerial TX. The resistor cuts hiss and protects the module's 3.3V input. |
| DFPlayer | BUSY | A2 | LOW while a song is playing. |
| DFPlayer | SPK1, SPK2 | Speaker | Connect the speaker directly. Never connect SPK to GND. |
| Potentiometer | outer legs, wiper | 5V and GND, **A0** | |
| Button "previous" | | A3 to GND | `INPUT_PULLUP`. Left button. |
| Button "play/pause" | | A4 to GND | `INPUT_PULLUP`. Middle button. |
| Button "next" | | A5 to GND | `INPUT_PULLUP`. Right button. |

If a pin is ever needed for something else, the three buttons can share one analog pin through a resistor ladder, which frees two pins.

## Phase 1: reader and LCD

**Goal:** tapping a card shows its ID on the LCD and in the Serial Monitor. This also becomes the way to collect card IDs for phase 2.

What it does:
- While idle, the LCD shows `Tap a card...`.
- On a tap, the LCD shows `Card:` on line 1 and the ID on line 2 (`A3 4F 12 9C`). It also prints `Card UID: A3 4F 12 9C` to Serial at 9600 baud.
- The card is put to sleep after it's read, so a card left on the reader is reported only once.
- After 3 seconds, the screen goes back to `Tap a card...`.
- A 7-byte ID (NTAG stickers) is printed without spaces so it fits in 16 characters.

Tasks:
- [x] Rename `1-project` to `1-project-mini-piano`
- [x] `platformio.ini` for the Uno, with the MFRC522 and LiquidCrystal libraries
- [x] `src/main.cpp`, phase 1 sketch (builds: 20% RAM, 23% flash). On startup it checks the reader answers, and shows `RFID not found` if not.
- [x] `README.md` and `assets/phase-1-rfid-lcd.pdf` schematic
- [x] Upload to the Uno (boots and prints its startup message)
- [ ] Wire it on the breadboard
- [ ] Hardware check:
  - [ ] LCD shows `Tap a card...`. Swap the contrast resistor if the text is blank or shows solid blocks.
  - [ ] The kit's card and blue key fob each show a different, stable ID every time they're tapped
  - [ ] Leaving a card on the reader doesn't spam the Serial Monitor
  - [ ] Screen goes back to idle after about 3 seconds
- [ ] Buy: DFPlayer Mini and a pack of 13.56 MHz tags

## Phase 2: music player

**Goal:** a card plays its folder. A knob controls volume, and three buttons control playback.

### SD card

- Use a microSD card of 32GB or less, formatted **FAT32** (Disk Utility: "MS-DOS (FAT)").
- Layout:
  ```
  /01/001.mp3, 002.mp3, ...   <- "Dinosaur Songs"
  /02/001.mp3, ...            <- "Bedtime"
  ```
- After copying from the Mac, run `dot_clean /Volumes/<CARD>` and delete any `._*` files. The DFPlayer counts them as tracks.

### `src/cards.h`

The ID is written exactly as the LCD and Serial show it, so it can be copied and pasted:

```cpp
const Card CARDS[] = {
  {"A3 4F 12 9C", 1, "Dinosaur Songs"},
  {"04A1B2C3D4E5F6", 2, "Bedtime"},
};
```

Titles are 16 characters at most (one LCD line).

### Behavior

| Situation | What happens | LCD line 1 / line 2 |
|---|---|---|
| Power on, no card yet | Nothing plays. All buttons are ignored. | `Tap a card...` |
| Known card, **different** from the current one | Its folder plays from song 1. Works whether the box is playing, paused or finished. | title / `Song 1 of 7` |
| **Same** card as the current one | Nothing happens, whether playing, paused or finished. Only a change of card counts. | unchanged |
| Unknown card | Music carries on. The card does **not** become the current card. | `New card:` / ID for about 3s, then back |
| Song ends (BUSY goes HIGH) | The next song plays. | title / `Song 3 of 7` |
| Last song ends | Playback stops. | `Tap a card...` |
| **Next** | Next song. After the last song, it wraps to song 1. | title / `Song n of N` |
| **Previous** | Previous song. On song 1, it restarts song 1. | title / `Song n of N` |
| **Play/pause** while playing | Pause. | title / `Paused  2 of 7` |
| **Play/pause** while paused | Resume. | title / `Song 2 of 7` |
| **Play/pause** after a folder finished | Replay the last folder from song 1. | title / `Song 1 of N` |
| Next or previous while finished | Ignored. | `Tap a card...` |
| Turn the knob | Volume 0..`MAX_VOLUME`. Read about 10 times a second; a command is sent only when the value changes. | unchanged |

There is no sleep timeout. A paused box stays paused until a button or card is used.

### Implementation notes

- The DFPlayer runs on `SoftwareSerial(8, A1)` (RX, TX) at 9600 baud, using `DFRobotDFPlayerMini`. Call `begin(mp3Serial, true, false)` (ACK on, no reset) and wait about 1s after power-up. Hardware `Serial` stays free for the Serial Monitor.
- RAM is 2KB. Keep every string literal in flash with `F()`, keep the `cards.h` table in `PROGMEM` if it grows past about 20 cards, and check the RAM figure after each build (aim to stay under about 75%).
- Detecting the end of a song: BUSY takes a few hundred ms to go LOW after a play command. Ignore BUSY for about 500ms after each command so a new song isn't mistaken for a finished one. BUSY is also HIGH while paused, so only count it as "song ended" while in the playing state.
- Card changes are found by comparing the formatted ID with the current card's ID. A card left on the reader just repeats the same ID, so nothing happens. No removal detection is needed.
- Buttons are debounced about 30ms, and act on the press (HIGH to LOW), not while held.
- The volume pot is `analogRead` mapped to 0..`MAX_VOLUME`, with ±1 hysteresis to stop jitter.
- Split the code once it grows: `main.cpp` (state machine), `cards.h` (table). Keep the RFID, LCD and player helpers in `main.cpp` unless it passes about 250 lines.

### Tasks

- [ ] Prepare the SD card (FAT32, numbered folders, `dot_clean`)
- [ ] Wire the DFPlayer, speaker, potentiometer and three buttons
- [ ] Add `dfrobot/DFRobotDFPlayerMini` to `lib_deps`
- [ ] `cards.h` with the phase 1 card IDs
- [ ] State machine above
- [ ] `assets/phase-2-mp3.pdf` schematic and a README phase 2 section
- [ ] Hardware check: run through every row of the behavior table
- [ ] Tune `MAX_VOLUME` by ear

## Phase 3: the box (to design later)

Known constraints:
- The RC522 reads only about 2-3cm away. The lid over the reader must be **thin (3mm or less) and non-metal**. Mark the tap spot on the lid.
- It needs cutouts for the LCD window, volume knob, three buttons (previous | play/pause | next) and speaker grille, plus a way out for the USB power cable.
- The wiring moves from the breadboard to something permanent (an Uno prototype shield or perfboard, with soldered joints).
- It has to survive a 4-year-old: no loose wires, no sharp edges, nothing small enough to swallow.

Open questions for the phase 3 design session: the box material (wood craft box, project box or 3D print), where the parts mount, the power switch, and a way to get the SD card out without opening the box.

## Ideas for next time

- Continue where you left off (resume the last folder and song after power-off)
- Sleep timer
- A second speaker (it would need a stereo amp)
- A short error beep for unknown cards
