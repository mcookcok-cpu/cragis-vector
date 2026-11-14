import re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

SRC = "cragis-jiplak-huruf-lama.svg"   # sumber monogram + posisi slot huruf
OUT = "cragis-putih-jiplak.svg"
FONT = "fonts/nasa/Nasalization Rg.otf"
HALO = 16          # lebar stroke mask (8 unit tiap sisi, diukur dari versi jiplak)
BASE, TOP = 785, 682
S = (BASE - TOP) / 675.0   # skala dari cap-height font

s = open(SRC).read()
ps = re.findall(r'<path([^>]*?)d="([^"]*)"', s)
mono, let = ps[0][1], ps[1][1]

def subs(d): return [x for x in re.split(r'(?=M)', d) if x.strip()]
def bb(d):
    n = list(map(float, re.findall(r'-?\d+\.?\d*', d)))
    return min(n[0::2]), min(n[1::2]), max(n[0::2]), max(n[1::2])

# slot huruf dari versi jiplak, urut kiri -> kanan: C R A G I S
slots = sorted((bb(x) for x in subs(let)), key=lambda b: b[0])
centers = [(b[0] + b[2]) / 2 for b in slots]

f = TTFont(FONT); gs = f.getGlyphSet(); cm = f.getBestCmap()
paths = []
LB = [1e9, 1e9, -1e9, -1e9]
for ch, cx in zip("CRAGIS", centers):
    g = gs[cm[ord(ch)]]
    bp = BoundsPen(gs); g.draw(bp)
    x0, _, x1, _ = bp.bounds
    tx = cx - S * (x0 + x1) / 2
    pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    g.draw(TransformPen(pen, (S, 0, 0, -S, tx, BASE)))
    paths.append(pen.getCommands())
    bp2 = BoundsPen(gs); g.draw(TransformPen(bp2, (S, 0, 0, -S, tx, BASE)))
    b = bp2.bounds; LB = [min(LB[0], b[0]), min(LB[1], b[1]), max(LB[2], b[2]), max(LB[3], b[3])]
letters = "".join(paths)

lb = LB
mb = bb(mono)
x0, y0 = min(lb[0], mb[0]), min(lb[1], mb[1])
x1, y1 = max(lb[2], mb[2]), max(lb[3], mb[3])
vb = "%d %d %d %d" % (round(x0), round(y0), round(x1 - x0), round(y1 - y0))

svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s">'
 '<defs><mask id="h" maskUnits="userSpaceOnUse" x="%d" y="%d" width="%d" height="%d">'
 '<rect x="%d" y="%d" width="%d" height="%d" fill="#fff"/>'
 '<path d="%s" fill="#000" fill-rule="evenodd" stroke="#000" stroke-width="%d" stroke-linejoin="round"/></mask></defs>'
 '<path fill="#ffffff" fill-rule="evenodd" d="%s"/>'
 '<path mask="url(#h)" fill="#d2d2d2" d="%s"/></svg>') % (
 vb, x0-20, y0-20, x1-x0+40, y1-y0+40, x0-20, y0-20, x1-x0+40, y1-y0+40, mono, HALO, mono, letters)
open(OUT, "w").write(svg)
print("viewBox", vb, "| ukuran", len(svg), "byte | slot tengah", [round(c) for c in centers], "| skala", round(S, 4))
