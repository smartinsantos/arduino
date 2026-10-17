# RFID music box case

Four parts, all already turned the right way up for printing. None needs supports.

| File | What it is | Notes |
|---|---|---|
| `fit_test.stl` | Small plate with one of each critical hole | Print first (about 30 min) and check the fits below |
| `base.stl` | Bottom tray, 190 x 140 x 52 mm | Open side up |
| `lid.stl` | Top, with the posts and rims underneath | Upside down: the top face goes on the bed |
| `knob.stl` | 36 mm volume knob | Glued over the potentiometer's own knob |

Settings: PETG, 0.2 mm layers, 4 walls, 4 top and bottom layers, 20% infill. About 300 g in all.

The lid's square speaker rim is sized for a Dayton PC68-4 (68.1 mm frame, holes on a 73.4 mm circle). Measure the speaker before printing the lid and change `SPEAKER_FRAME` / `SPEAKER_BOLT_CIRCLE` if it differs.

Fit test checks:

- An arcade button snaps into the big hole and holds firmly.
- The potentiometer goes through the small hole and its nut threads on.
- A heat-set insert melts into the thick post, an M3 screw self-taps into the medium post, and an M2.5 screw into the thin one.
- The Uno's USB plug fits the square hole.

## Changing the design

`make_box.py` makes every STL from the numbers in its PARAMETERS section. Change a number and run it again:

```sh
pip install manifold3d trimesh numpy
python3 make_box.py
```

It prints `fit check: OK` when nothing under the lid hits the Uno. Assembly steps and wiring are in `../phase-3-box.pdf`.
