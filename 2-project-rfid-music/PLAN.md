# RFID Music Box: Plan

A music box for a 4-year-old. Tap a card on the reader, and the songs in that card's folder play in order. The LCD shows the folder's title and the song number. A knob sets the volume, and three buttons handle previous, play/pause and next.

The work is split into three phases:

| Phase | What | Status |
|---|---|---|
| 1 | RFID reader and LCD: tap a card, see its ID | **Done**, tested on the breadboard |
| 2 | MP3 player, card-to-folder table, volume knob, buttons | **Built.** Stage A (cards play folders) works on the breadboard. Stage B (knob and buttons) is uploaded and waiting for a hardware test |
| 3 | Put it all in a box | Constraints only. Needs its own design session after phase 2 works |

## Decisions

| Topic | Decision | Why |
|---|---|---|
| Board | Arduino **Uno** (the same board as the mini piano) | It's the board on hand. It fits, but only just: every pin except D0/D1 is used by phase 2 (see the pin table), the DFPlayer needs SoftwareSerial, and RAM is 2KB, so keep strings in flash with `F()`. |
| Display | **LCD1602**, 4-bit parallel wiring | 16x2 characters is enough for a title and "Song 2". The kit's 8x8 matrix and 7-segment displays can't show words well. |
| LCD contrast | **5.1k ohm** fixed resistor from V0 to GND (the kit's 5K1) | The kit's potentiometer is used for volume. Found by trying: 220 ohm gave solid blocks, 1k left grey blocks behind faint letters, 5.1k is clear. Other LCD modules may need a different value. |
| MP3 module | **DFPlayer Mini** (DFRobot, Amazon B089D5NLW1) | It plays from the microSD card we already have and is the most-used module with Arduino. Rejected: DFPlayer Pro (128MB built-in memory, few examples). |
| Speaker | **One** CQRobot 3W 8 ohm speaker (B0738NLFTG); the second is a spare | The DFPlayer's amp is mono. |
| Tags | **13.56 MHz** MIFARE Classic 1K cards or NTAG213 stickers | The RC522 reads only 13.56 MHz. 125 kHz tags (EM4100, T5577, "proximity") will not work: the first pack bought was 125 kHz T5577 and the reader can't see them. |
| Card mapping | A table in `src/cards.h`: card ID, folder number, title | It's the only option that gives the LCD real titles. To add a card, read its ID off the screen, add a line and re-upload. |
| SD layout | Numbered folders `01`..`99`, files `001.mp3`..`255.mp3` | The DFPlayer only understands numbered folders. The readable name lives in `cards.h`. |
| Song count | **Not asked.** Play on until the module reports "file not found" for the next song | Our DFPlayer is a clone that answers the "files in folder" query (0x4E) with an error; the library then returned a stale "2" and every folder stopped after song 2. "File not found" works reliably, and adding songs still needs no code change. The cost: the LCD shows `Song 3`, not `Song 3 of 5`. |
| Volume | Potentiometer on A0, mapped to 0..`MAX_VOLUME` = **30** (the module's maximum) | Chosen for maximum loudness; the knob turns it down. Near the top the built-in amp may crackle, and loud bass can reset a weakly powered board: drop `MAX_VOLUME` to 25 if either happens. |
| Power | 5V/2A USB charger or power bank into the Uno's USB port | The DFPlayer takes power from the Uno's 5V pin. The RC522 uses the Uno's own 3.3V pin (no resistor or diode needed). A power bank makes it portable. |
| Libraries | `miguelbalboa/MFRC522`, `arduino-libraries/LiquidCrystal`, `dfrobot/DFRobotDFPlayerMini` | |
| Sample music | `assets/mp3/01`, `02`, `03`, laid out exactly as on the SD card. The MP3s are not in git; `assets/mp3/CREDITS.md` lists every file's source | About 57 MB is too heavy for the repo. Kevin MacLeod tracks (CC BY 4.0) and LibriVox lullabies (public domain). |
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
| LCD1602 | V0 | 5.1k ohm to GND | Contrast. Use a higher value if you see blocks behind the text, lower if the text is faint. |
| LCD1602 | A | 220 ohm to 5V | Backlight. |
| LCD1602 | RS, E | D2, D3 | |
| LCD1602 | D4, D5, D6, D7 | D4, D5, D6, D7 | Same numbers on both ends. LCD D0-D3 are not connected. |
| *Phase 2* | | | |
| DFPlayer | VCC, GND | 5V, GND | |
| DFPlayer | TX | D8 | SoftwareSerial RX. |
| DFPlayer | RX | A1 **through 1k ohm** | SoftwareSerial TX. The resistor cuts hiss and protects the module's 3.3V input. |
| DFPlayer | BUSY | A2 | LOW while a song is playing. |
| DFPlayer | SPK_1, SPK_2 (pins 6, 8) | Speaker | Connect the speaker directly. Never connect SPK to GND. |
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
- [x] Wire it on the breadboard
- [x] Hardware check:
  - [x] LCD shows `Tap a card...`. Contrast resistor swapped until the text was clear: 5.1k ohm (220 ohm gave solid blocks, 1k was dim).
  - [x] The kit's card (`EB 5A 25 0B`) and blue key fob (`75 E2 5A D3`) each show their own ID
- [x] Buy: DFPlayer Mini, microSD card, speaker
- [ ] Buy 13.56 MHz tags: the first pack (125 kHz T5577) doesn't work; replace it with MIFARE Classic 1K cards
- [x] Pin guide page in the phase 1 PDF (RC522, LCD1602, Uno power header)

## Phase 2: music player

**Goal:** a card plays its folder. A knob controls volume, and three buttons control playback.

Built in two stages, each tested before the next:
- **Stage A:** DFPlayer and speaker. A card plays its folder, songs advance on their own, unknown cards show their ID. Volume fixed.
- **Stage B:** the volume knob and the previous / play-pause / next buttons, plus the pause screen.

### SD card

- Use a microSD card of 32GB or less, formatted **FAT32** (Disk Utility: "MS-DOS (FAT)").
- Layout (the sample music in `assets/mp3/` is already laid out like this):
  ```
  /01/001.mp3 ... 005.mp3   <- "Happy Tunes"   (white kit card)
  /02/001.mp3 ... 004.mp3   <- "Bedtime"       (blue kit fob)
  /03/001.mp3 ... 012.mp3   <- "Lullaby Poems" (no card yet)
  ```
- After copying from the Mac, run `dot_clean /Volumes/<CARD>` and delete any `._*` files. The DFPlayer counts them as tracks.

### `src/cards.h`

The ID is written exactly as the LCD and Serial show it, so it can be copied and pasted. The table lives in flash (`PROGMEM`) so 30+ cards don't use up the Uno's RAM:

```cpp
const Card CARDS[] PROGMEM = {
  {"EB 5A 25 0B", 1, "Happy Tunes"},
  {"75 E2 5A D3", 2, "Bedtime"},
};
```

Titles are 16 characters at most (one LCD line). To add a card: tap it, copy the `New card:` ID into a new line, pick its folder and title, upload.

### Behavior

| Situation | What happens | LCD line 1 / line 2 |
|---|---|---|
| Power on | Checks the reader and the DFPlayer. A missing one stops here. | `Starting...`, then `Tap a card...`, or `RFID not found` / `MP3 not found` |
| No card yet | Nothing plays. All buttons are ignored. | `Tap a card...` |
| Known card, **different** from the current one | Its folder plays from song 1. Works whether the box is playing, paused or finished. | title / `Song 1` |
| **Same** card as the current one | Nothing happens, whether playing, paused or finished. Only a change of card counts. | unchanged |
| Unknown card | Music carries on. The card does **not** become the current card. | `New card:` / ID for about 3s, then back |
| Song ends (BUSY goes HIGH) | The next song plays. | title / `Song 3` |
| Last song ends | The module reports the next song missing, so playback stops. | `Tap a card...` |
| **Next** | Next song. After the last song, it wraps to song 1. Also works while paused (and resumes). | title / `Song n` |
| **Previous** | Previous song. On song 1, it restarts song 1. Also works while paused (and resumes). | title / `Song n` |
| **Play/pause** while playing | Pause. | title / `Paused  2` |
| **Play/pause** while paused | Resume. | title / `Song 2` |
| **Play/pause** after a folder finished | Replay the last folder from song 1. | title / `Song 1` |
| Next or previous while finished | Ignored. | `Tap a card...` |
| Turn the knob | Volume 0..`MAX_VOLUME`. Read about 10 times a second; a command is sent only when the value changes. | unchanged |

There is no sleep timeout. A paused box stays paused until a button or card is used.

### Implementation notes

- The DFPlayer runs on `SoftwareSerial(8, A1)` (RX, TX) at 9600 baud, using `DFRobotDFPlayerMini`. `begin(mp3Serial, true, true)` (ACK on, reset on start) so the module starts clean even when only the Uno was reset. Hardware `Serial` stays free for the Serial Monitor.
- Don't use the module's count queries (`readFileCountsInFolder`, `readFileCounts`): our clone answers them with an error. The end of a folder is found from the "file not found" error (`DFPlayerError` / `FileMismatch`) for the next song. Next on the last song uses the same error to wrap to song 1.
- RAM is 2KB. Keep every string literal in flash with `F()`, keep the `cards.h` table in `PROGMEM` if it grows past about 20 cards, and check the RAM figure after each build (aim to stay under about 75%).
- Detecting the end of a song: BUSY takes a few hundred ms to go LOW after a play command. Ignore BUSY for 1s after each play or resume command so a new song isn't mistaken for a finished one. BUSY is also HIGH while paused, so only count it as "song ended" while in the playing state.
- Card changes are found by comparing the formatted ID with the current card's ID. A card left on the reader just repeats the same ID, so nothing happens. No removal detection is needed.
- Buttons are debounced about 30ms, and act on the press (HIGH to LOW), not while held.
- The volume knob averages 4 `analogRead`s, ignores changes smaller than 24 (of 1023, half a volume step), and maps to 0..`MAX_VOLUME`. An unconnected A0 drifts on its own, so random volume changes in the Serial Monitor mean the knob's middle leg isn't connected.
- Code layout: `cards.h` holds the card table; `main.cpp` holds everything else (about 330 lines, one playback state: no card / playing / paused / finished). Kept as one file for now; split the input handling (buttons, knob) into its own file if it grows further.

### Tasks

- [x] Sample music in `assets/mp3/` (out of git, sources in `CREDITS.md`)
- [x] Prepare the SD card (FAT32, numbered folders, `dot_clean`)
- [x] Stage A: wire the DFPlayer and speaker
- [x] Add `dfrobot/DFRobotDFPlayerMini` to `lib_deps`
- [x] `cards.h` with the kit card and fob
- [x] Stage A code; hardware check: cards play their folders
- [x] Fix: folders stopped after 2 songs (clone module's count query); play until "file not found" instead
- [x] Stage B code: knob, buttons, pause
- [x] `MAX_VOLUME` set to 30
- [x] `assets/phase-2-mp3.pdf` schematic (wiring, DFPlayer pin guide, knob and button guide) and a README phase 2 section
- [ ] Stage B: wire the potentiometer and three buttons
- [ ] Hardware check: run through every row of the behavior table
- [ ] Add the 13.56 MHz cards to `cards.h` once they arrive

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
