# Enclosure: Hammond/Tayda 1590B

Flatline+ v1.1 face drilling, made 2026-10-18 from `Flatline.kicad_pcb`:
- pot shafts at the mid-point of the mounting tabs;
- LED centres;
- toggle bushings at the centre pin.

**Mapping (board → outside view):** X = 43.5 − x, Y = 69.5 − y. This is the same as the Trem v2: the top pots, BLEND / SHAPE and both toggle holes coincide with `Trem SMD/enclosure`.

## Face (outside view)

```
   VOLUME   ON LED · GR LED   SUSTAIN     (Y 38.5; the LEDs at X −3 / +3)
   TIGHT        BLEND         RELEASE     (Y 18 / 19.5)
                FOOTSWITCH                (Y −37.5)
```

| Hole | Ø mm |
|---|---|
| 9 mm pots | 7.5 |
| 3 mm LEDs | 3.2 (6 mm apart, centre to centre) |
| Sub-mini toggles (Taiway 200) | 5.2 |
| 3PDT footswitch | 12.2 |

- **Files:** `Flatline_1590B_drill.csv` (Tayda Box Tool: origin = face centre, +X right / +Y up, outside view) and `Flatline_1590B_drill_template.svg` (1:1; check the 50 × 5 mm box).
- **Jacks:** same as the Trem v2 (side jacks per your usual layout). Not in this file.
