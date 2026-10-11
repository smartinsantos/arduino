# RFID Music Box

A music box for a 4-year-old, built on an Arduino Uno. Tap a card, and the songs in that card's folder play in order. The LCD shows what's playing.

The project is built in phases. The full plan, the decisions behind it and the phase 2 behavior are in [PLAN.md](PLAN.md).

| Phase | What | Status |
|---|---|---|
| 1 | RFID reader and LCD: tap a card, see its ID | Built |
| 2 | MP3 player, volume knob, previous / play-pause / next buttons | Waiting for the DFPlayer Mini |
| 3 | Put it all in a box | Later |

## Phase 1: reader and LCD

Tap a card, and the LCD shows its ID for 3 seconds:

```
Card:
A3 4F 12 9C
```

The same ID is printed to the Serial Monitor (`Card UID: A3 4F 12 9C`), ready to copy into phase 2's card table. Otherwise the screen shows `Tap a card...`. A card left lying on the reader is reported only once.

| Part | Part pin | Uno pin |
|---|---|---|
| RC522 RFID reader | SDA | D10 |
| | MOSI | D11 |
| | MISO | D12 |
| | SCK | D13 |
| | RST | D9 |
| | 3.3V | **3.3V** |
| | GND | GND |
| LCD1602 | RS | D2 |
| | E | D3 |
| | D4, D5, D6, D7 | D4, D5, D6, D7 |
| | VSS, RW, K | GND |
| | VDD | 5V |
| | V0 (contrast) | 1k ohm resistor to GND |
| | A (backlight) | 220 ohm resistor to 5V |

### Wiring

Full diagram, parts list and troubleshooting tips: [assets/phase-1-rfid-lcd.pdf](assets/phase-1-rfid-lcd.pdf)

In short:

- **RFID reader**: power it from the Uno's **3.3V** pin, never 5V. The Uno makes 3.3V itself from its 5V/USB supply: the pin is on the power header, between RESET and 5V. You don't need a resistor or diode. D11-D13 are the Uno's fixed SPI pins. Leave IRQ unconnected. If the kit's header pins aren't soldered on yet, solder them. Pins that are only pushed in give flaky reads.
- **LCD**: only the top four data pins (D4-D7) are used, and each goes to the Uno pin with the same number. Leave D0-D3 empty. Contrast comes from a fixed resistor, because the potentiometer is saved for the volume knob in phase 2. If the screen lights up but shows nothing, the contrast is wrong (see the PDF's tips). If it shows `RFID not found`, the sketch couldn't reach the reader: check its wiring and 3.3V.
- **Power and GND**: run the Uno's 5V and GND to the breadboard rails. The RFID reader's 3.3V is the one wire that goes straight to the Uno.

## Phase 2: music player (planned)

Every remaining Uno pin gets used. A DFPlayer Mini (on SoftwareSerial) plays MP3s from a microSD card through one 3W speaker. A table in `src/cards.h` maps each card to a numbered folder and a title. A potentiometer sets the volume, and three buttons do previous, play/pause and next. Pins, SD card layout and the full behavior table are in [PLAN.md](PLAN.md#phase-2-music-player).

## Build and upload

This is a [PlatformIO](https://platformio.org/) project (board: `uno`, framework: `arduino`). The libraries in `platformio.ini` download on the first build.

```sh
pio run                # build
pio run -t upload      # build and flash the connected Uno
pio device monitor     # watch card IDs (9600 baud), Ctrl+C to quit
pio device list        # find the serial port if upload can't
```

If more than one serial device is connected, pick the Uno explicitly with `pio run -t upload --upload-port <port>`. The Uno is the one reporting `VID:PID=2341:0043`.

On Apple Silicon Macs, PlatformIO's AVR compiler is an Intel binary, so Rosetta 2 must be installed:

```sh
softwareupdate --install-rosetta --agree-to-license
```

## Layout

```
platformio.ini   board, framework and libraries
src/main.cpp     the sketch
PLAN.md          phases, decisions, pins, phase 2 behavior
assets/          wiring schematics (PDF)
```

## Ideas for next time

- Continue where you left off after power-off.
- A sleep timer.
- A short error beep for unknown cards.
