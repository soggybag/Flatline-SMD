# Flatline roadmap

Notes and ideas for after the first Flatline+ build. Started 2026-10-07.

## How the gain cell can be rearranged

The gain cell is U1B: gain = 1 + (R7 ∥ LDR) / (R6 + SUSTAIN). More light means less LDR resistance. Where the LDR sits decides what the effect does:

| LDR position | More light → | Effect |
|---|---|---|
| Across the feedback resistor R7 (now) | less gain | **Compressor** |
| Across the ground leg (R6 + SUSTAIN) | more gain | **Upward expander** (Punch Line idea): louder notes get louder |
| In series with the signal, after the gain cell, with a resistor to ground | less loss | **Downward expander:** gain is never above 1, so decays and noise drop away and loud notes pass at unity |

## Expander: does it have merit?

Yes, as a "dynamics restorer" (makes the pick attack jump out), but it needs care.

1. **Op-amp clipping.** An upward expander adds gain on exactly the loudest notes. With a bright LDR (~1–2k) in the ground leg, the gain can reach ×100+, and a 9 V OPA2134 runs out of swing at about ±4 V.
   - Fix: a resistor in series with the LDR to cap the maximum gain (e.g. 10k → about ×23, as now), plus a low resting gain.
   - Or use the **downward** form: the LDR as a series attenuator, gain ≤ 1, so it can't clip. Fixed make-up gain then brings the level back up.
2. **Runaway.** The detector listens to the **output** (feedback). In expand mode, output up → more light → more gain → output up again: positive feedback. It latches loud until it clips, or blooms in an uncontrolled way.
   - Fix: in expand mode, feed the detector from the **input (DRY)**. That makes it feed-forward and stable.
   - Flatline+ already has the buffered DRY node (U1A). Switching R8's input between WET and DRY is one pole of a toggle.
3. **Drive in front (Big Muff etc.).** A compressed fuzz has almost no level change left until the note dies.
   - An expander *after* it only sees that final drop, so it acts like a noise gate on the tail. It can't restore pick dynamics the fuzz has already flattened.

## Making a Big Muff dynamic: the useful version

Take the **detector from the clean guitar** and put the **gain element after the fuzz.** The fuzz's volume then follows your picking and the natural decay of the clean string.
- **As a standalone pedal:** that needs a **SEND/RETURN loop**. Send = the clean buffered input (DRY), the fuzz goes in the loop, and the vactrol gain cell sits on RETURN. The detector stays on the clean input.
- **Same idea as Penfold:** Penfold does this with an OTA (envelope from the clean input → VCA after the Rat stage). Its roadmap already has the effects-loop idea (switched RETURN jack, or one TRS insert jack).
- **An optical version** (a "Dynamic Loop" pedal) would make *any* fuzz or drive touch-sensitive. **This is the strongest new-product idea here.**

## Clipping diodes

**In the compressor (now):** put a diode pair across R7, the gain-cell feedback.
- The compressor holds the output near its threshold (~0.45 V peak), and Si diodes clip at ~±0.6 V. So they only catch the **attack transient**, before the LDR reacts (~2.5 ms turn-on).
- Result: a "crunchy pick" compressor, with clean sustain behind a bitten attack.
- Make it a toggle: OFF / Si (1N4148) / LED (softer, louder).
- Cheap to try: two 1N4148s tacked across R7.

**With the expander: clip on loud notes, clean up on decay.** Yes, and the diodes also solve the headroom problem.
- Put the diode pair across the feedback while the LDR is in the ground leg (upward expander, detector from DRY).
- Loud notes raise the gain and drive into the diodes, which cap the output at ±0.6 V (Si), so the op-amp never clips.
- As the note decays, the gain falls back, so the tail is clean *and* quieter.
- It's a sharper version of an overdrive's natural clean-up: hard picking = dirt, soft picking or the decay = clean.
- Watch out for: the output level jumps between the clipped and clean regions; the knee depends on the vactrol's ~35 ms release.

## Possible panel for a "Flatline X" (1590B, Trem v2 grid)

- **Top:** SUSTAIN · GR LED · VOLUME.
- **Middle:** BLEND, a MODE toggle (COMP / EXPAND), and a CLIP toggle (OFF / Si / LED). That's back to the Trem's exact two-toggle drilling; the GR LED doubles as the "it's working" light.
- **MODE switching** needs at least a DPDT:
  - one pole moves the LDR between the feedback and the ground leg (with its series resistor);
  - the other pole moves the detector input between WET and DRY.

## Bench experiments on the first Flatline+ build (no new board needed)

1. **Clipping on attack:** tack 1N4148s across R7, then try red LEDs. Listen at high SUSTAIN with BLEND full wet.
2. **Feed-forward compression:** lift R8 from WET and wire it to DRY (U1A pin 1). Compare the feel: feed-forward is harder, with a more obvious knee.
3. **Expander:**
   - Lift the LDR leads off the feedback and connect them across R6 + SUSTAIN, with a 10k in series.
   - Feed R8 from DRY.
   - Start with SUSTAIN at minimum.
4. **Loop test:** run a Big Muff between DRY and the gain-cell input (cut the U1A → U1B link). Fuzz into the gain cell, with the detector still on the clean input.

## Dynamic fuzz vs clean-up distortion: separate designs (2026-10-07)

Both ideas use a clean-input envelope follower driving a gain element. Where the gain element sits decides the effect:
- **After the fuzz → dynamic fuzz.** The envelope controls the volume, so the fuzz breathes with your picking. This is Penfold's design (LM13700 VCA). **Test Penfold first.** If its envelope ripple is audible, the LED/LDR version (Flatline-style vactrol) may be smoother (see the Penfold roadmap).
- **Before the clipper → clean-up distortion.** The envelope controls the drive: hard picking clips, soft picking and decays clean up. **Breadboard first**, as the LED/LDR version closest to Flatline / Punch Line: `~/Documents/KiCad/projects/Clean-Up Drive/`.

**Decision:** separate pedals that share the envelope block. Combine them (dual OTA, DYNAMICS knob) only if both prove themselves.

## TL072 vs OPA2134 (2026-10-07)

- **In the original Flatline the audio op-amp also drove the bridge** (IC1A, through 330 Ω, into the LED string). That's where the OPA2134 helps most:
  - it drives about 35 mA cleanly, against the TL072's ~20 mA;
  - the TL072's output stage distorts under that pulsed rectifier load.

  That's probably much of what Atomium heard.
- **Flatline+ moves the bridge drive to U2**, so the audio op-amp is unloaded and the gap shrinks.
- **What's left is noise and headroom:**
  - **Noise:** OPA2134 ≈ 8 nV/√Hz against TL072 ≈ 18 nV/√Hz. That's about 7 dB less hiss, and it's amplified ×23 at full SUSTAIN. Audible in a compressor, because the compressor raises the noise floor.
  - **Headroom:** slightly more output swing on 9 V.
- **Cost:** OPA2134UA ≈ $2 plus JLC's extended-part fee; TL072 is a basic part at ≈ $0.10.
- **Choice:** OPA2134 for U1 (audio), TL072 for U2 (side chain), as drawn. They're pin-compatible, so A/B them in a socket on the breadboard.
