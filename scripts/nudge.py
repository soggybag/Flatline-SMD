"""Move the listed front-side parts to the nearest spot clear of courtyards and through-hole pads.
usage: nudge.py board.kicad_pcb REF[,REF...] [maxdist_mm]"""
import sys, math, pcbnew
B, refs = sys.argv[1], sys.argv[2].split(',')
RMAX = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
MM, mm = pcbnew.FromMM, pcbnew.ToMM
b = pcbnew.LoadBoard(B)
e = b.GetBoardEdgesBoundingBox()
EX0, EY0, EX1, EY1 = mm(e.GetX()) + 0.5, mm(e.GetY()) + 0.5, mm(e.GetRight()) - 0.5, mm(e.GetBottom()) - 0.5

def crt(f):
    c = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
    if not c.OutlineCount():   # no courtyard (e.g. the DIY vactrol): use the outline bounding box
        bb = f.GetBoundingBox(False)
        return (mm(bb.GetX()) - 0.25, mm(bb.GetY()) - 0.25, mm(bb.GetRight()) + 0.25, mm(bb.GetBottom()) + 0.25)
    bb = c.BBox(); return (mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom()))

def obstacles(skip):
    rects = []
    for f in b.GetFootprints():
        if f.GetReference() in skip: continue
        if not f.IsFlipped():
            c = crt(f)
            if c: rects.append((f.GetReference(), c))
        for p in f.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                x, y = mm(p.GetPosition().x), mm(p.GetPosition().y)
                r = max(mm(p.GetSize().x), mm(p.GetSize().y)) / 2 + 0.25
                rects.append((f.GetReference() + ':pad', (x - r, y - r, x + r, y + r)))
    return rects

def clear(c, rects):
    if c[0] < EX0 or c[1] < EY0 or c[2] > EX1 or c[3] > EY1: return False
    return not any(c[0] < r[2] and c[2] > r[0] and c[1] < r[3] and c[3] > r[1] for _, r in rects)

placed = set()
for ref in refs:
    f = b.FindFootprintByReference(ref)
    rects = obstacles({ref})
    x0, y0, a0 = mm(f.GetPosition().x), mm(f.GetPosition().y), f.GetOrientationDegrees()
    best = None
    for rot in (a0, a0 + 90):
        f.SetOrientationDegrees(rot)
        f.SetPosition(pcbnew.VECTOR2I(MM(x0), MM(y0)))
        c0 = crt(f)
        steps = int(RMAX / 0.25)
        for i in range(-steps, steps + 1):
            for j in range(-steps, steps + 1):
                dx, dy = i * 0.25, j * 0.25
                d = math.hypot(dx, dy) + (0.6 if rot != a0 else 0)
                if d > RMAX or (best and d >= best[0]): continue
                c = (c0[0] + dx, c0[1] + dy, c0[2] + dx, c0[3] + dy)
                if clear(c, rects): best = (d, dx, dy, rot)
    if best is None:
        f.SetOrientationDegrees(a0); f.SetPosition(pcbnew.VECTOR2I(MM(x0), MM(y0)))
        print(ref, 'NO SPOT within', RMAX, 'mm'); continue
    d, dx, dy, rot = best
    t = f.Reference(); tp = t.GetPosition(); ta = t.GetTextAngleDegrees()
    f.SetOrientationDegrees(rot); f.SetPosition(pcbnew.VECTOR2I(MM(x0 + dx), MM(y0 + dy)))
    t.SetPosition(pcbnew.VECTOR2I(tp.x + MM(dx), tp.y + MM(dy))); t.SetTextAngleDegrees(ta)
    print('%-4s moved %.2f mm (dx %.2f, dy %.2f)%s' % (ref, math.hypot(dx, dy), dx, dy, ', rotated 90' if rot != a0 else ''))
pcbnew.SaveBoard(B, b)
