"""Flatline+ (1590B): Hollis Flatline optical compressor with the Atomium mods, plus:
  - U1A dry buffer, so the input sees 1M and BLEND gets a low-impedance dry signal
  - side chain on its own op-amp (U2): the detector no longer loads the audio output
  - differential bridge drive (U2A -4.7x, U2B +4.7x): same threshold as the original 5.7x with the GR LED added
  - BLEND (parallel compression), gain-reduction LED in series with the vactrol LED
  - RELEASE toggle: 220u (stock) or 440u (slow)
usage: build_flatline.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('Flatline', 'A2')
FR = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
FC = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FCP = 'Capacitor_SMD:CP_Elec_6.3x7.7'
FPOT = 'Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical'
FPAD = 'Connector_Wire:SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm'
FSO8 = 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
RL = {'1M': 'C17514', '10k': 'C17414', '47k': 'C17713', '220k': 'C17556', '330': 'C17630', '4k7': 'C17673'}
CL = {'220n': 'C5378', '47p': 'C14857', '220p': 'C107145', '10u': 'C15850', '22u': 'C45783', '100n': 'C49678', '220u': 'C970695'}
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V9(p): s.power('+9V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def Rh(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'R', v, cx, y, 90, fp=FR, lcsc=RL[v], desc=desc or f'Resistor {v} 1% 0805', text='t')
def Rv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'R', v, x, cy, 0, fp=FR, lcsc=RL[v], desc=desc or f'Resistor {v} 1% 0805', text=side)
def Ch(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'C', v, cx, y, 90, fp=FC, lcsc=CL[v], desc=desc or f'Ceramic {v} 0805', text='t')
def Cv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'C', v, x, cy, 0, fp=FC, lcsc=CL[v], desc=desc or f'Ceramic {v} 0805', text=side)
def CPv(ref, x, cy, side='r', desc=''):
    s.part(ref, 'Device', 'C_Polarized', '220u', x, cy, 0, fp=FCP, lcsc=CL['220u'], desc=desc, text=side,
           extra={'FT Rotation Offset': '180'})   # DMBJ RVT caps: JLC places them reversed without this (UF1/UF3 lesson)
def POT(ref, v, name, x, y, rot=0, mirror=None, text='r'):
    if text == 'r': text = ((x + 4.445, y - 1.27), (x + 4.445, y + 1.27), 'left')
    s.part(ref, 'Device', 'R_Potentiometer', v, x, y, rot, mirror=mirror, fp=FPOT,
           desc=f'{name}: Alpha RD901F 9 mm, back side, hand-soldered', text=text, extra={'Panel': name}, bom=False)
def PAD(ref, name, x, y):
    s.part(ref, 'Connector_Generic', 'Conn_01x01', name, x, y, 180, fp=FPAD, desc=f'Wire pad: {name}', bom=False,
           text=((x - 2.54, y - 1.27), (x - 2.54, y + 1.27), 'right'))
    return P(ref, '1')
def OP(ref, part, lcsc, unit, x, y, desc):
    lib = 'Amplifier_Operational'
    s.part(ref, lib, part, part, x, y, 0, unit=unit, fp=FSO8, lcsc=lcsc, desc=desc, text='ic')
def OPA(unit, x, y): OP('U1', 'OPA2134', 'C87361', unit, x, y, 'OPA2134UA audio op-amp (dry buffer + gain cell)')
def TL(unit, x, y): OP('U2', 'TL072', 'C6961', unit, x, y, 'TL072 side-chain drivers')

# ================================================================ CONNECTORS
s.box('CONNECTORS', g(4), g(6), g(40), g(48))
s.part('J1', 'Connector_Generic', 'Conn_01x04', 'IN/LED/GND/OUT', g(12), g(16), 180,
       fp='Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical', desc='Ribbon header to the footswitch board', text=((g(8), g(11)), (g(8), g(20)), 'right'), bom=False)
for pin, net in (('1', 'IN'), ('2', 'LED_K'), ('4', 'OUT')):
    q = P('J1', pin); W(q, (q[0] + g(3), q[1])); lab(net, (q[0] + g(3), q[1]))
q = P('J1', '3'); W(q, (q[0] + g(3), q[1])); GND((q[0] + g(3), q[1]))
q = PAD('J2', '9V', g(14), g(30)); W(q, (q[0] + g(3), q[1])); lab('9V_IN', (q[0] + g(3), q[1]))
for ref, name, y in (('J3', 'GND', 34), ('J4', 'IN GND', 38), ('J5', 'OUT GND', 42)):
    q = PAD(ref, name, g(14), g(y)); W(q, (q[0] + g(3), q[1])); GND((q[0] + g(3), q[1]))
    if ref == 'J3': s.power('PWR_FLAG', (q[0] + g(3), q[1]))
s.text('1x4 ribbon to the footswitch board. IN GND / OUT GND: jack sleeves (star ground).', g(5), g(46))

# ================================================================ POWER + BIAS
s.box('POWER + BIAS: reverse protection, VB = 4.5 V', g(4), g(52), g(40), g(98))
q = (g(8), g(58)); lab('9V_IN', q, 'l')
s.part('D1', 'Diode', 'SS14', 'SS14', g(13), g(58), 180, fp='Diode_SMD:D_SMA', lcsc='C2480', desc='Reverse-polarity protection', text='t')
W(q, P('D1', '2')); W(P('D1', '1'), (g(20), g(58)))
V9((g(20), g(58))); s.power('PWR_FLAG', (g(20), g(58)))
W((g(20), g(58)), (g(33), g(58)))
for ref, v, x, d in (('C1', '22u', 23, 'Supply reservoir'), ('C2', '100n', 28, 'U1 decoupling'), ('C3', '100n', 33, 'U2 decoupling')):
    Cv(ref, v, g(x), g(61.5), side='r', desc=d); W((g(x), g(58)), P(ref, '1')); GND(P(ref, '2'))
Rv('R1', '10k', g(10), g(72), desc='VB divider'); V9(P('R1', '1'))
Rv('R2', '10k', g(10), g(80), desc='VB divider'); GND(P('R2', '2'))
W(P('R1', '2'), P('R2', '1'))
W((g(10), g(76)), (g(16), g(76))); W((g(16), g(76)), (g(16), g(79.5) - 3.81)); Cv('C4', '22u', g(16), g(79.5), side='r', desc='VB filter'); GND(P('C4', '2'))
W((g(16), g(76)), (g(20), g(76))); lab('VB', (g(20), g(76))); s.power('PWR_FLAG', (g(20), g(76)))
OPA(3, g(28), g(84)); V9(P('U1', '8')); GND(P('U1', '4'))
TL(3, g(35), g(84)); V9(P('U2', '8')); GND(P('U2', '4'))
s.text('U1 OPA2134 (audio), U2 TL072 (side chain).', g(5), g(96))

# ================================================================ INPUT + DRY BUFFER + GAIN CELL
s.box('INPUT + DRY BUFFER (U1A) + GAIN CELL (U1B): gain = 1 + (R7 || LDR) / (R6 + SUSTAIN), x3 to x23', g(44), g(6), g(150), g(62))
y = g(20)
lab('IN', (g(47), y), 'l')
W((g(47), y), (g(52), y))
Rv('R3', '1M', g(52), y + g(3.5), side='l', desc='Input pull-down (no pop)'); W((g(52), y), P('R3', '1')); GND(P('R3', '2'))
W((g(52), y), (g(54), y)); Ch('C5', '220n', g(55.5), y, desc='Input coupling (Atomium: 1M / 220n)')
W((g(54), y), P('C5', '1')); W(P('C5', '2'), (g(60), y))
Rv('R4', '1M', g(60), y + g(3.5), side='r', desc='Input bias to VB (1M input impedance)'); W((g(60), y), P('R4', '1'))
q = P('R4', '2'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
OPA(1, g(70), y + 2.54)                     # + input at (x-7.62, y)
W((g(60), y), P('U1', '3'))
o = P('U1', '1'); m = P('U1', '2')
W(m, (m[0] - g(1), m[1]), (m[0] - g(1), m[1] + g(3)), (o[0] + g(1), m[1] + g(3)), (o[0] + g(1), o[1]))
W(o, (o[0] + g(1), o[1]), (o[0] + g(4), o[1])); lab('DRY', (o[0] + g(4), o[1]))
s.text('U1A: unity dry buffer', g(64), y + g(7))

# gain cell U1B: + at the top (y1), - below, feedback network and ground leg below
x0, y1 = g(112), g(18)
lab('DRY', (x0 - g(14), y1), 'l')
OPA(2, x0, y1 + 2.54)
W((x0 - g(14), y1), P('U1', '5'))
mi = P('U1', '6'); ou = P('U1', '7')
fbL, fbR = mi[0] - g(2), ou[0] + g(2)
fy = mi[1] + g(5)
W(mi, (fbL, mi[1])); W((fbL, mi[1]), (fbL, fy + g(6)))
W(ou, (fbR, ou[1])); W((fbR, ou[1]), (fbR, fy + g(6)))
Rh('R7', '220k', (fbL + fbR) / 2, fy, desc='Gain-cell feedback (max gain with R6)')
W((fbL, fy), P('R7', '1')); W(P('R7', '2'), (fbR, fy))
Ch('C6', '47p', (fbL + fbR) / 2, fy + g(3), desc='Bandwidth limit (Atomium 68p; 47p = 15 kHz)')
W((fbL, fy + g(3)), P('C6', '1')); W(P('C6', '2'), (fbR, fy + g(3)))
W((fbL, fy + g(6)), (fbL + g(3), fy + g(6))); lab('LDR_A', (fbL + g(3), fy + g(6)))
W((fbR, fy + g(6)), (fbR - g(3), fy + g(6))); lab('WET', (fbR - g(3), fy + g(6)), 'l')
gx = fbL - g(6)
W((fbL, mi[1]), (gx, mi[1]))
Rv('R6', '10k', gx, mi[1] + g(3.5), side='l', desc='Gain-cell ground leg (sets max gain x23)'); W((gx, mi[1]), P('R6', '1'))
POT('RV1', 'A100k', 'SUSTAIN', gx, P('R6', '2')[1] + g(2) + 3.81, mirror='x',
    text=((gx - g(5), mi[1] + g(10)), (gx - g(5), mi[1] + g(11.5)), 'right'))
W(P('R6', '2'), P('RV1', '3'))
w2 = P('RV1', '2'); p1 = P('RV1', '1')
W(w2, (w2[0] + g(1), w2[1]), (w2[0] + g(1), p1[1] + g(1)), (p1[0], p1[1] + g(1)))
W(p1, (p1[0], p1[1] + g(2))); lab('VB', (p1[0], p1[1] + g(2)), 'l')
W((fbR, ou[1]), (fbR + g(6), ou[1])); lab('WET', (fbR + g(6), ou[1]))
s.text('SUSTAIN: wiper tied to pin 1, as the original (CW = more gain into the LDR)', g(95), g(58))

# ================================================================ SIDE CHAIN + DETECTOR
s.box('SIDE CHAIN (U2): differential bridge drive from WET, buffered off the audio path', g(44), g(66), g(150), g(126))
def inv(unit, x, ytop, rin, rf, rf_val, cf, in_lab, out_lab, rin_desc, rf_desc):
    """inverting stage on U2: + at ytop (to VB), - below; input resistor from the left, feedback below"""
    TL(unit, x, ytop + 2.54)
    pl, mi, ou = (P('U2', '3'), P('U2', '2'), P('U2', '1')) if unit == 1 else (P('U2', '5'), P('U2', '6'), P('U2', '7'))
    W(pl, (pl[0] - g(6), pl[1])); lab('VB', (pl[0] - g(6), pl[1]), 'l')
    Rh(rin, '10k', mi[0] - 6.35, mi[1], desc=rin_desc)
    W(P(rin, '2'), mi)
    q = P(rin, '1'); W(q, (q[0] - g(2), q[1])); lab(in_lab, (q[0] - g(2), q[1]), 'l')
    tap = P(rin, '2'); fy = mi[1] + g(4)
    W(tap, (tap[0], fy))
    rx = ou[0] + g(1)
    Rh(rf, rf_val, (tap[0] + rx) / 2, fy, desc=rf_desc)
    W((tap[0], fy), P(rf, '1')); W(P(rf, '2'), (rx, fy))
    bot = fy
    if cf:
        Ch(cf, '220p', (tap[0] + rx) / 2, fy + g(3), desc='Side-chain bandwidth (Atomium)')
        W((tap[0], fy), (tap[0], fy + g(3)), P(cf, '1')); W(P(cf, '2'), (rx, fy + g(3)))
        bot = fy + g(3)
    W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, bot))
    W((rx, ou[1]), (rx + g(4), ou[1])); lab(out_lab, (rx + g(4), ou[1]))
inv(1, g(64), g(74), 'R8', 'R9', '47k', 'C7', 'WET', 'SC_N', 'Side-chain input', 'Side-chain gain (-4.7x)')
inv(2, g(64), g(98), 'R10', 'R11', '10k', None, 'SC_N', 'SC_P', 'Unity inverter in', 'Unity inverter feedback (SC_P = +4.7x)')

# bridge + LED string
bx, by = g(118), g(96)          # bridge diamond: left node BA, right node BB, top BP, bottom BN
lab('SC_P', (g(98), by), 'l')
Rh('R12', '330', g(104), by, desc='LED current limit (Atomium 330R)'); W((g(98), by), P('R12', '1'))
BA, BB, BP, BN = (bx - g(8), by), (bx + g(8), by), (bx, by - g(8)), (bx, by + g(8))
W(P('R12', '2'), BA)
lab('SC_N', (BB[0] + g(5), BB[1])); W(BB, (BB[0] + g(5), BB[1]))
# D2: BA -> BP, D3: BB -> BP, D4: BN -> BA, D5: BN -> BB  (vertical diodes on the diamond sides)
s.part('D2', 'Device', 'D_Schottky', 'B5819W', BA[0], by - g(4), 270, fp='Diode_SMD:D_SOD-123', lcsc='C8598', desc='Bridge (1N5817 equivalent)', text='l')
s.part('D3', 'Device', 'D_Schottky', 'B5819W', BB[0], by - g(4), 270, fp='Diode_SMD:D_SOD-123', lcsc='C8598', desc='Bridge', text='r')
s.part('D4', 'Device', 'D_Schottky', 'B5819W', BA[0], by + g(4), 270, fp='Diode_SMD:D_SOD-123', lcsc='C8598', desc='Bridge', text='l')
s.part('D5', 'Device', 'D_Schottky', 'B5819W', BB[0], by + g(4), 270, fp='Diode_SMD:D_SOD-123', lcsc='C8598', desc='Bridge', text='r')
# connect: for rot 90 the anode/cathode ends are vertical; route each to its node
for ref, anode_node, cath_node in (('D2', BA, BP), ('D3', BB, BP), ('D4', BN, BA), ('D5', BN, BB)):
    a, k = P(ref, '2'), P(ref, '1')
    s.L(a, anode_node, first='v'); s.L(k, cath_node, first='v')
lab('BR_P', (BP[0], BP[1] - g(2))); W(BP, (BP[0], BP[1] - g(2)))
lab('BR_N', (BN[0], BN[1] + g(2))); W(BN, (BN[0], BN[1] + g(2)))
s.text('Full-wave bridge driven between SC_P and SC_N (9.4x WET).', g(98), g(110))

# LED string + release caps
lx = g(132)
lab('BR_P', (lx, g(72)), 'l')
W((lx, g(72)), (lx + g(3), g(72)))
s.part('D6', 'Device', 'LED', 'GR LED', lx + g(3), g(76), 90, fp='LED_THT:LED_D3.0mm',
       desc='Gain-reduction LED (red, panel, back side): glows as it compresses', text='r', bom=False, extra={'Panel': 'GR LED'})
W((lx + g(3), g(72)), P('D6', '2'))
s.part('U3', 'Isolator', 'NSL-32', 'Vactrol', lx + g(11), g(84), 0, fp='Flatline:Vactrol_LED_LDR_DIY',
       desc='VTL5C3 / Xvive VTL5C3 or DIY LED + LDR (hand-soldered)', text=((lx + g(11), g(79)), (lx + g(11), g(80.5)), None), bom=False)
W(P('D6', '1'), (P('D6', '1')[0], P('U3', '1')[1]), P('U3', '1'))
k = P('U3', '2')
W(k, (lx + g(3), k[1]), (lx + g(3), g(90)))
s.part('RV2', 'Device', 'R_Potentiometer_Trim', '1k', lx + g(3), g(90) + 3.81, 0, fp='Flatline:Potentiometer_Bourns_3362P_Vertical',
       desc='LED current trim (original POT1), Bourns 3362P, hand-soldered', text='l', bom=False)
W((lx + g(3), g(90)), P('RV2', '1'))
w2 = P('RV2', '2'); p3 = P('RV2', '3')
W(w2, (w2[0] + g(1), w2[1]), (w2[0] + g(1), p3[1] + g(1)), (p3[0], p3[1] + g(1)))
W(p3, (p3[0], g(101))); lab('BR_N', (p3[0], g(101)), 'l')
q = P('U3', '4'); W(q, (q[0] + g(3), q[1])); lab('LDR_A', (q[0] + g(3), q[1]))
q = P('U3', '3'); W(q, (q[0] + g(3), q[1])); lab('WET', (q[0] + g(3), q[1]))
# release caps: C8 always in (220u, the stock value); C9 switched in by RELEASE (440u)
cx = g(122)
lab('BR_P', (cx, g(112)), 'l'); lab('BR_N', (cx, g(124)), 'l')
CPv('C8', cx + g(4), g(118), side='r', desc='Release cap (always in): 220u, the stock value')
W((cx, g(112)), (cx + g(4), g(112))); W((cx + g(4), g(112)), P('C8', '1')); W(P('C8', '2'), (cx + g(4), g(124)))
W((cx + g(4), g(112)), (cx + g(12), g(112)))
s.part('SW1', 'Switch', 'SW_SPDT', 'RELEASE', cx + g(15), g(112), 0, fp='Flatline:SW_Taiway_200_SPDT',
       desc='RELEASE: FAST (open) / SLOW (adds C9). Sub-mini SPDT, back side, hand-soldered', text='t', bom=False, extra={'Panel': 'RELEASE'})
W((cx + g(12), g(112)), P('SW1', '2'))
sw1 = P('SW1', '1'); sw3 = P('SW1', '3')
s.noconnect(sw3)
CPv('C9', cx + g(19), g(118), side='r', desc='Release cap (SLOW): adds 220u')
W(sw1, (cx + g(19), sw1[1]), P('C9', '1'))
W(P('C9', '2'), (cx + g(19), g(124)))
W((cx, g(124)), (cx + g(19), g(124)))
s.text('Gain-reduction LED + vactrol LED + RV2 trim in series. RELEASE: FAST = 220u, SLOW = 440u.', g(98), g(127.5))

# ================================================================ OUTPUT: BLEND + VOLUME
s.box('OUTPUT: BLEND (dry <-> compressed) + VOLUME', g(154), g(6), g(214), g(62))
lab('WET', (g(157), g(18)), 'l'); lab('DRY', (g(157), g(36)), 'l')
Ch('C12', '10u', g(161.5), g(18), desc='WET coupling'); W((g(157), g(18)), P('C12', '1'))
Ch('C13', '10u', g(161.5), g(36), desc='DRY coupling'); W((g(157), g(36)), P('C13', '1'))
W(P('C12', '2'), (g(170), g(18))); W(P('C13', '2'), (g(170), g(36)))
Rv('R13', '1M', g(167), g(21.5), side='l', desc='Pull-down (no pop)'); W((g(167), g(18)), P('R13', '1')); GND(P('R13', '2'))
Rv('R14', '1M', g(167), g(39.5), side='l', desc='Pull-down (no pop)'); W((g(167), g(36)), P('R14', '1')); GND(P('R14', '2'))
POT('RV3', 'B100k', 'BLEND', g(170), g(27), mirror='x', text=((g(173), g(23)), (g(173), g(24.5)), 'left'))
W((g(170), g(18)), P('RV3', '3')); W((g(170), g(36)), P('RV3', '1'))
w = P('RV3', '2')
W(w, (g(186), w[1]))
POT('RV4', 'A100k', 'VOLUME', g(186), w[1] + 3.81, mirror='x', text=((g(189), g(29)), (g(189), g(30.5)), 'left'))
GND(P('RV4', '1'))
w = P('RV4', '2'); W(w, (g(196), w[1])); lab('OUT', (g(196), w[1]))
s.text('BLEND CW = compressed (WET), CCW = dry. Both paths are in phase.', g(156), g(52))

# ================================================================ ON LED
s.box('ON LED (panel): lit by the footswitch through LED_K', g(154), g(66), g(214), g(98))
V9((g(160), g(74)))
Rv('R15', '4k7', g(160), g(77.5), side='r', desc='ON LED current (~1.5 mA)'); W((g(160), g(74)), P('R15', '1'))
s.part('D7', 'Device', 'LED', 'ON LED', g(160), g(85), 90, fp='LED_THT:LED_D3.0mm', desc='ON LED (panel, back side)', text='r', bom=False, extra={'Panel': 'ON LED'})
W(P('R15', '2'), P('D7', '2'))
q = P('D7', '1'); W(q, (q[0], q[1] + g(2))); lab('LED_K', (q[0], q[1] + g(2)))

s.write(OUT, title_block={'title': 'Flatline+ (1590B)', 'rev': '1.0', 'company': 'Super-Freq',
                         'comments': ['Hollis Flatline optical compressor, Atomium mods, plus dry buffer, BLEND, GR LED, RELEASE',
                                      'Side chain on its own op-amp (detector no longer loads the audio output)']})
print('written', OUT)
