"""Place the Flatline+ board (unrouted) from the schematic netlist, on the Trem v2 outline and panel grid.
Run from the project folder with KiCad's python:
  kicad-cli sch export netlist -o /tmp/fl.net Flatline.kicad_sch
  python3 scripts/buildpcb_flatline.py /tmp/fl.net
Then nudge (overlaps) and route with _tools/autoroute.py. Don't re-run after hand edits: it overwrites the board."""
import sys, json
sys.path.insert(0, 'scripts')
from sx import parse, find, find1
import pcbnew
NET = sys.argv[1]
MM = pcbnew.FromMM
FPDIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
POTSTEP = '${KIPRJMOD}/3dmodels/pot_RD901F_T18_shaft_alpha_9mm_vertical.step'

# ---------------- netlist
r = parse(open(NET).read())
comps = {}
for c in find(find1(r, 'components'), 'comp'):
    ref = find1(c, 'ref')[1]
    props = {find1(p, 'name')[1]: (find1(p, 'value') or [0, ''])[1] for p in find(c, 'property')}
    flds = {}
    for fs in find(c, 'fields'):
        for f in find(fs, 'field'):
            flds[find1(f, 'name')[1]] = f[2] if len(f) > 2 and not isinstance(f[2], list) else ''
    flds['Datasheet'] = (find1(c, 'datasheet') or [0, ''])[1]; flds['Description'] = (find1(c, 'description') or [0, ''])[1]
    comps[ref] = dict(value=find1(c, 'value')[1], fp=find1(c, 'footprint')[1], fields=flds, props=props,
                      tstamp=find1(c, 'tstamps')[1])
pinnet = {}
for n in find(find1(r, 'nets'), 'net'):
    for nd in find(n, 'node'):
        pinnet[(find1(nd, 'ref')[1], find1(nd, 'pin')[1])] = find1(n, 'name')[1]

# ---------------- placement: ref -> (x, y, rot, side). Panel parts on the Trem v2 grid (back side).
PLACE = {
    # panel (back): pots at shaft + (2.5, 7.5), rot 90
    'RV1': (32.0, 38.5, 90, 'B'),    # SUSTAIN  (Trem RATE spot)
    'RV4': (60.25, 38.5, 90, 'B'),   # VOLUME   (Trem DEPTH spot)
    'RV3': (46.0, 57.5, 90, 'B'),    # BLEND    (Trem SHAPE spot)
    'D6': (44.77, 31.0, 180, 'B'),   # GR LED   (Trem LED spot)
    'D7': (61.27, 51.5, 180, 'B'),   # ON LED   (Trem RANGE toggle spot)
    'SW1': (27.0, 51.5, 180, 'B'),   # RELEASE  (Trem SQ/TRI spot)
    # front THT
    'J1': (39.69, 67.3, 90, 'F'), 'J2': (39.5, 22.6, 0, 'F'), 'J3': (47.5, 22.6, 0, 'F'),
    'J4': (23.95, 67.2, 0, 'F'), 'J5': (63.25, 67.2, 0, 'F'),
    'U3': (33.9, 47.5, 90, 'F'),     # vactrol, vertical, between RELEASE and BLEND (no legs under a pot body)
    'RV2': (57.0, 61.5, 0, 'F'),     # 3362P release-current trim
    # front SMD (targets; scripts/nudge clears overlaps)
    'D1': (43.5, 27.5, 0, 'F'), 'C1': (49.5, 27.5, 90, 'F'),
    'C8': (30.0, 25.5, 0, 'F'), 'C9': (56.5, 26.0, 0, 'F'),
    'U1': (42.5, 62.0, 0, 'F'), 'C2': (34.5, 57.25, 0, 'F'),
    'R3': (30.0, 58.0, 90, 'F'), 'C5': (30.0, 61.5, 90, 'F'), 'R4': (30.0, 65.0, 90, 'F'),
    'R6': (38.5, 56.0, 0, 'F'), 'R7': (38.5, 60.0, 0, 'F'), 'C6': (38.5, 62.5, 0, 'F'),
    'R1': (49.5, 62.0, 0, 'F'), 'R2': (49.5, 64.5, 0, 'F'), 'C4': (52.5, 63.5, 90, 'F'),
    'U2': (54.0, 46.5, 0, 'F'), 'C3': (58.5, 46.5, 90, 'F'),
    'R8': (50.0, 44.5, 0, 'F'), 'R9': (50.0, 47.0, 0, 'F'), 'C7': (50.0, 49.5, 0, 'F'),
    'R10': (58.0, 43.0, 0, 'F'), 'R11': (58.0, 50.0, 0, 'F'),
    'R12': (40.0, 36.0, 0, 'F'), 'D2': (36.0, 34.5, 0, 'F'), 'D3': (36.0, 37.5, 0, 'F'),
    'D4': (45.0, 35.0, 0, 'F'), 'D5': (45.0, 38.0, 0, 'F'),
    'C12': (51.5, 55.0, 90, 'F'), 'C13': (54.0, 55.0, 90, 'F'), 'R13': (51.5, 58.5, 90, 'F'), 'R14': (54.0, 58.5, 90, 'F'),
    'R15': (60.0, 57.0, 90, 'F'),
}

def lib_path(fpid):
    lib, name = fpid.split(':')
    return ('Flatline.pretty' if lib == 'Flatline' else FPDIR + lib + '.pretty'), name

# load footprints BEFORE the board object exists (pcbnew SwigPyObject quirk)
fps = {}
for ref, c in comps.items():
    path, name = lib_path(c['fp'])
    f = pcbnew.FootprintLoad(path, name)
    f.SetFPID(pcbnew.LIB_ID(c['fp'].split(':')[0], name))
    fps[ref] = f
enc = pcbnew.FootprintLoad('Flatline.pretty', 'Hammond_1590B')

b = pcbnew.BOARD()
nets = {}
for name in sorted(set(pinnet.values())):
    ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); nets[name] = ni

# outline (Trem v2)
pts = [(21, 26), (27, 20), (60, 20), (66, 26), (66, 70), (21, 70)]
for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
    sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts); sh.SetWidth(MM(0.1))
    sh.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0))); sh.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1))); b.Add(sh)

missing = []
for ref, c in sorted(comps.items()):
    f = fps[ref]; b.Add(f)
    f.SetReference(ref); f.SetValue(c['value'])
    f.SetPath(pcbnew.KIID_PATH('/' + c['tstamp'])); f.SetSheetname('Root'); f.SetSheetfile('Flatline.kicad_sch')
    for k, v in c['fields'].items():
        if k in ('Footprint', 'Reference', 'Value'):
            continue
        f.SetField(k, v); f.GetField(k).SetVisible(False)
    hand = 'exclude_from_bom' in c['props']
    f.SetExcludedFromBOM(hand); f.SetExcludedFromPosFiles(hand)
    x, y, rot, side = PLACE.get(ref, (75, 30, 0, 'F'))
    if ref not in PLACE:
        missing.append(ref)
    f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    if side == 'B':
        f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot)
    for p in f.Pads():
        k = (ref, p.GetNumber())
        if k in pinnet: p.SetNet(nets[pinnet[k]])
    if c['fp'].endswith('RD901F-40-00D_Single_Vertical'):
        for m in list(f.Models()):
            pass
        f.Models().clear()
        m = pcbnew.FP_3DMODEL(); m.m_Filename = POTSTEP
        m.m_Offset = pcbnew.VECTOR3D(6.6, -2.5, 4); m.m_Rotation = pcbnew.VECTOR3D(-90, 0, 0)
        f.Models().push_back(m)

b.Add(enc); enc.SetReference('ENC1'); enc.SetValue('Hammond 1590B')
enc.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
enc.SetPosition(pcbnew.VECTOR2I(MM(43.5), MM(69.5)))
enc.Flip(enc.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT); enc.SetOrientationDegrees(180)

pcbnew.SaveBoard('Flatline.kicad_pcb', b)
# SaveBoard rewrites the project's net classes: put the Trem classes back
src = json.load(open('../Trem SMD/Trem_23.kicad_pro'))
p = json.load(open('Flatline.kicad_pro'))
p['net_settings'] = src['net_settings']
p['net_settings']['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('+9V', 'GND', '/9V_IN', '/VB')]
json.dump(p, open('Flatline.kicad_pro', 'w'), indent=2)
print('board written; unplaced:', missing)
