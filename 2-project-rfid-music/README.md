# RFID Music Box

A music box for a 4-year-old, built on an Arduino Uno. Tap a card, and the songs in that card's folder play in order. The LCD shows what's playing, a knob sets the volume, and three buttons do previous, play/pause and next.

The project is built in phases. The full plan, the decisions behind it and the behavior table are in [PLAN.md](PLAN.md).

| Phase | What | Status |
|---|---|---|
| 1 | RFID reader and LCD: tap a card, see its ID | Done |
| 2 | MP3 player, volume knob, previous / play-pause / next buttons | Built. Cards play their folders; the knob and buttons wait for a hardware test |
| 3 | Put it all in a box: 3D-printed case, proto shield, I2C LCD, arcade buttons | Designed. Parts to order, case to print, then assembly |

## What it does

- While idle, the LCD shows `Tap a card...`.
- Tap a card listed in `src/cards.h` and its SD card folder plays from song 1. The LCD shows the folder's title and `Song 1`, and each song moves on to the next by itself. After the last song it goes back to `Tap a card...`.
- Tapping a different card switches folders. Tapping the same card again does nothing, and a card left on the reader doesn't count as a new tap.
- An unknown card shows `New card:` and its ID for 3 seconds while the music keeps playing. The ID is also printed to the Serial Monitor (`Card UID: A3 4F 12 9C`), ready to copy into `src/cards.h`.
- **Knob:** volume from 0 to 30.
- **Buttons**, left to right:
  - **Previous** goes back a song (on song 1 it restarts it).
  - **Play/pause** pauses or resumes (`Paused  2`). After a folder has finished, it plays that folder again.
  - **Next** skips a song (after the last song it goes back to song 1).
- On power-up the LCD shows `Starting...`. If the reader or the MP3 player doesn't answer, it stops at `RFID not found` or `MP3 not found`. If the LCD doesn't answer, the box still plays, and the Serial Monitor prints `LCD not found at 0x27 or 0x3F`.

## Pins

| Part | Part pin | Uno pin |
|---|---|---|
| RC522 RFID reader | SDA | D10 |
| | MOSI | D11 |
| | MISO | D12 |
| | SCK | D13 |
| | RST | D9 |
| | 3.3V | **3.3V** |
| | GND | GND |
| LCD1602 with I2C backpack | GND, VCC | GND, 5V |
| | SDA, SCL | A4, A5 |
| DFPlayer Mini | VCC (pin 1) | 5V |
| | GND (pin 7) | GND |
| | TX (pin 3) | D8 |
| | RX (pin 2) | A1, **through a 1k ohm resistor** |
| | BUSY (pin 16) | A2 |
| | DAC_R, DAC_L (pins 4, 5) | Each through a 10k ohm resistor to the amp's L input (SPK_1/SPK_2 stay empty) |
| PAM8403 amp | 5V, GND, input G | 5V, GND, GND, with a 100 uF capacitor across 5V and GND |
| | L+, L- | Dayton PC68-4 speaker. Never connect L- to GND |
| Potentiometer | middle leg | A0 (outer legs to 5V and GND) |
| Buttons | previous / play-pause / next | D2 / D3 / D4, other leg to GND |

D5, D6, D7 and A3 are free. D0/D1 stay free for USB.

The LCD changed in phase 3: it used to be wired in parallel (RS, E, D4-D7 on D2-D7, plus contrast and backlight resistors) with the buttons on A3-A5. The I2C backpack needs only 4 wires and has its own contrast screw.

## Wiring

- Phase 3 (the box, **current wiring**): [assets/phase-3-box.pdf](assets/phase-3-box.pdf). Shopping list with Amazon links, 3D printing notes for the case, the wiring through the proto shield, and step-by-step assembly.
- Phase 1 (reader and LCD): [assets/phase-1-rfid-lcd.pdf](assets/phase-1-rfid-lcd.pdf). Wiring diagram, a pin guide for the RC522, LCD and the Uno's power header, then parts and tips. Shows the old parallel LCD wiring.
- Phase 2 (MP3 player, knob, buttons): [assets/phase-2-mp3.pdf](assets/phase-2-mp3.pdf). Wiring diagram, a DFPlayer pin guide, a knob and button guide, then parts and tips. Shows the old LCD wiring, the buttons on A3-A5 and the speaker on the DFPlayer's SPK pins. Both older PDFs carry a "superseded" note.

In short:

- **RFID reader**: power it from the Uno's **3.3V** pin, never 5V. The Uno makes 3.3V itself: the pin is on the power header, between RESET and 5V. No resistor or diode needed. Leave IRQ unconnected. Solder the header pins if they're loose.
- **LCD**: an LCD1602 with an I2C backpack soldered on the back: GND, VCC, SDA (A4), SCL (A5). Turn the blue screw on the backpack until the text is sharp. The sketch finds the backpack at address 0x27 or 0x3F by itself.
- **Speaker and amp**: the speaker is a Dayton Audio PC68-4 (2.5", 4 ohm), driven by a PAM8403 class-D amp. The amp takes the DFPlayer's line output (DAC_L and DAC_R, mixed through two 10k resistors), which sounds much cleaner than the DFPlayer's own small amp. The knob still works: the DFPlayer's volume sets the DAC level too. Phases 1-2 drove a small CQRobot speaker straight from SPK_1/SPK_2.
- **DFPlayer**: hold it with the microSD slot facing you and the half-moon notch at the top. Pin 1 (VCC) is then top-left and BUSY is top-right. The 1k resistor on RX is required: it protects the module and cuts hiss.
- **Knob**: middle leg to A0. If turning clockwise makes it quieter, swap the outer legs.
- **Buttons**: each button connects its Uno pin (D2, D3, D4) to GND when pressed. No resistor needed. On a breadboard, use two diagonal legs of the kit's buttons; in the box, the arcade buttons' two switch tabs.
- **Power and GND**: run the Uno's 5V and GND to the breadboard rails. Use a 5V/2A USB charger: at high volume, a weak supply can make the board reset.

## Music and cards

The SD card needs numbered folders `01`..`99` with songs named `001.mp3`, `002.mp3` and so on. The module can't read names, so each folder's title lives in `src/cards.h`.

Sample music is in [assets/mp3/](assets/mp3/), laid out exactly as it goes on the card:

| Folder | Title | Card |
|---|---|---|
| `01` | Happy Tunes (5 songs) | White kit card |
| `02` | Bedtime (4 songs) | Blue kit fob |
| `03` | Lullaby Poems (12 spoken lullabies) | None yet |

1. Format a microSD card (32GB or less) in Disk Utility as **MS-DOS (FAT)**, scheme **Master Boot Record**.
2. Copy the folders to the root of the card.
3. Run `dot_clean /Volumes/<card name>`, so the hidden `._` files macOS creates aren't counted as songs.

The MP3 files are not in git. [assets/mp3/CREDITS.md](assets/mp3/CREDITS.md) lists where each one comes from and the credits the licenses ask for.

To add a card: tap it, copy the ID that `New card:` shows into a new line in `src/cards.h` with its folder number and a title (16 characters at most), then upload.

## Build and upload

This is a [PlatformIO](https://platformio.org/) project (board: `uno`, framework: `arduino`). The libraries in `platformio.ini` (MFRC522, LiquidCrystal_I2C, DFRobotDFPlayerMini) download on the first build.

```sh
pio run                # build
pio run -t upload      # build and flash the connected Uno
pio device monitor     # watch card IDs and playback (9600 baud), Ctrl+C to quit
pio device list        # find the serial port if upload can't
```

If more than one serial device is connected, pick the Uno explicitly with `pio run -t upload --upload-port <port>`. The Uno is the one reporting `VID:PID=2341:0043`.

On Apple Silicon Macs, PlatformIO's AVR compiler is an Intel binary, so Rosetta 2 must be installed:

```sh
softwareupdate --install-rosetta --agree-to-license
```

## The box

The case is two 3D-printed parts: a base that holds the Uno (its USB port lines up with a hole in the left wall) and a lid with the LCD, the tap zone over the reader, three 24 mm arcade buttons, a big volume knob and a round grille over the 2.5" speaker. The wiring is soldered to a proto shield, and every lid part plugs into it with a JST-XH plug.

The files are in [assets/3d/](assets/3d/): `base.stl`, `lid.stl`, `knob.stl` and `fit_test.stl`, already turned for printing. `make_box.py` makes them from the measurements at its top (`pip install manifold3d trimesh numpy`, then `python3 make_box.py`), and checks that the parts inside don't collide. The full build, from the shopping list to closing the lid, is in [assets/phase-3-box.pdf](assets/phase-3-box.pdf).

## Layout

```
platformio.ini      board, framework and libraries
src/main.cpp        the sketch
src/cards.h         which card plays which folder, and its title
PLAN.md             phases, decisions, pins, behavior table, tasks
assets/             wiring schematics (PDF), one per phase; phase 3 is the build guide
assets/3d/          3D-printable case (STL) and make_box.py, which generates it
assets/mp3/         sample music, laid out like the SD card (MP3s not in git)
```

## Ideas for next time

- Continue where you left off after power-off.
- A sleep timer.
- A short error beep for unknown cards.
