# Flatline+ design notes

Based on your Flatline v2 (OPA2134, Atomium mods; Eagle `Flatline-v2.sch`), rebuilt for JLC SMD in a 1590B.

## What changed from Flatline v2

| Change | Why |
|---|---|
| **U1A dry buffer** (unity, 1M input) | Feeds the gain cell and BLEND's dry side from a low impedance |
| **Side chain on its own TL072 (U2)** | In v2, IC1A drove the volume pot *and* the bridge through 330 Ω, so the rectifier loaded the audio output while compressing. Now the gain cell only sees U2A's 10k input. |
| **Differential bridge drive** (U2A −4.7×, U2B +4.7× = 9.4× WET) | Keeps about the stock threshold with the GR LED's extra ~1.8 V in the string |
| **BLEND** (B100k, dry ↔ compressed) | Parallel compression; both paths are in phase |
| **GR LED** in series with the vactrol LED | Glows as hard as it's compressing |
| **RELEASE** toggle | FAST 220 µF (the stock value), SLOW 440 µF (C8 + C9: 220 µF DMBJ C970695, FT Rotation Offset 180) |
| C6 68p → **47p** | 68p isn't a part proven on our boards; 47p = 15 kHz corner (68p was 10.6 kHz). Easy to change. |
| POT1 1k → **RV2 3362P 1k trim** (hand-soldered) | Same job: LED-string current |

**Unchanged:** the gain cell (R7 220k ∥ LDR, R6 10k + SUSTAIN A100k), R8/R9 = R5/R4 (10k/47k), 220p, 330 Ω, the 1N5817-type Schottky bridge (B5819W), the 1M/220n input, VB 10k/10k.

## Panel (planned: Trem v2 drilling)

- **Top row:** SUSTAIN · GR LED · VOLUME.
- **Middle:** BLEND (centre), RELEASE (sub-mini toggle) on one side, ON LED on the other.
- **Bottom:** footswitch.
- **Header:** 1×4 IN/LED/GND/OUT, which runs straight to SwitchPCB v2.

## To check on the first build

- The threshold with the GR LED: if it compresses too late, R9 47k → 68k.
- The RV2 trim range.
- RELEASE feel.
- That BLEND levels match: the dry is unity, and the wet sits at the compressed level.

## Board (2026-10-07)

- **Outline and grid:** the Trem v2 outline and panel grid; the parts are listed in the README.
- **Parts kept out from under the pots:** no front-side through-hole part sits under a pot body.
  - The vactrol is vertical between RELEASE and BLEND.
  - The 3362P trimmer is bottom right.
  - The header is bottom centre.
- **Routing:** autorouted (17 vias), with GND pours on both layers.
- **Checks:** DRC 0 / 0, parity 0.
