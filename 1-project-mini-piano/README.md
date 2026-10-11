# Mini Piano

A four-key piano for the Arduino UNO. Each button plays a note and lights its own LED.

The keys play C, D, E and G (a pentatonic scale), so any tune you mash out sounds reasonable.

| Button | Pin | Note | Pitch | LED pin |
|---|---|---|---|---|
| 1 | D2 | C4 | 262 Hz | D8 |
| 2 | D3 | D4 | 294 Hz | D9 |
| 3 | D4 | E4 | 330 Hz | D10 |
| 4 | D5 | G4 | 392 Hz | D11 |

The buzzer is on **D6**. If you press two keys at once, only the lowest-numbered key plays.

## Wiring

Full diagram, parts list and troubleshooting tips: [assets/mini-piano-schematic.pdf](assets/mini-piano-schematic.pdf)

In short:

- **Buttons**: one leg to the Uno pin, the opposite leg to GND. No resistor needed, because the sketch uses `INPUT_PULLUP`.
- **LEDs**: Uno pin, then a 220 ohm resistor, then the LED's long leg. The short leg goes to GND.
- **Buzzer**: the **passive** buzzer (bare green circuit board underneath). The `+` leg goes to D6 and the other leg to GND. An active buzzer will only make a single tone.
- **GND**: one jumper from the Uno GND pin to the breadboard's blue (-) rail. Everything else grounds to that rail.

## Build and upload

This is a [PlatformIO](https://platformio.org/) project (board: `uno`, framework: `arduino`).

```sh
pio run                # build
pio run -t upload      # build and flash the connected Uno
pio device list        # find the serial port if upload can't
```

If more than one serial device is connected, pick the Uno explicitly with `pio run -t upload --upload-port <port>`. The Uno is the one reporting `VID:PID=2341:0043`.

On Apple Silicon Macs, PlatformIO's AVR compiler is an Intel binary, so Rosetta 2 must be installed:

```sh
softwareupdate --install-rosetta --agree-to-license
```

## Layout

```
platformio.ini   board and framework config
src/main.cpp     the sketch
assets/          wiring schematic (PDF)
```

## Ideas for next time

- A fifth button that plays "Twinkle Twinkle" by itself.
- A memory game: the Uno plays a pattern of lights and tones, and the player copies it.
