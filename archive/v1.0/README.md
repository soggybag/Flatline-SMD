# Flatline SMD v1.0: archived revision

- **Git tag:** `v1.0` (commit `464e912`, 2026-10-18)
- **Tag note:** v1.0: first JLC order (Flatline+ V1.0), 2026-10
- **Archived:** 2026-10-23 with `_tools/archive_version.py`

## Finding a part

1. Open `Flatline_ibom.html` in a browser. Type a reference (R14) or a value (100k) in the filter box; the part lights up on the board.
   - Hover over a pad to see its net.
   - F / B switch sides.
2. Find the same reference in `Flatline_schematic.pdf` with Cmd-F.
3. `Flatline_board_front.pdf` / `_back.pdf` are printable: page 1 has the outlines and references, page 2 the copper. The back is mirrored, as you see it holding the board.

## Files

- `Flatline_board_back.pdf`
- `Flatline_board_front.pdf`
- `Flatline_ibom.html`
- `Flatline_render_bottom.png`
- `Flatline_render_top.png`
- `Flatline_schematic.pdf`
- `docs`/
- `parts.csv`
- `production`/

`production/` holds the files sent to JLCPCB for this revision: Flatline.zip, Flatline_hand_solder.csv, bom.csv, designators.csv, netlist.ipc, positions.csv.
