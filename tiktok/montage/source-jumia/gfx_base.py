# Calque graphique « JOJ Dakar 2026 » : même style que les vidéos Wave, Yango, Patisen et Dangote
# (sous-titres blancs à contour noir, mots-clés sur pastille orange, étiquettes qui rebondissent).
# Dessiné en sRGB puis converti en HLG BT.2020 au rendu.
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from words import captions, src2edit, SPANS, TOTAL_SPEECH

W, H = 1080, 1920
FPS = 30.0
HOLD = 4.2
TOTAL = TOTAL_SPEECH + HOLD
WHITE = (255, 255, 255)
GOLD = (246, 139, 30)   # orange Jumia
INK = (18, 18, 22)
GREY = (205, 207, 213)
DIM = (110, 112, 120)
FD = "/usr/share/fonts/opentype/inter/"
SS = 2

_f = {}
def font(name, size):
    size = max(1, int(size))
    k = (name, size)
    if k not in _f:
        _f[k] = ImageFont.truetype(FD + name + ".otf", size)
    return _f[k]

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))
def ease(x):
    x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x):
    x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, k):
    return a + (b - a) * k
def rgba(c, a):
    return tuple(c[:3]) + (int(round(255 * clamp(a))),)
def E(src):
    return src2edit(src)

# coupes du montage (temps vidéo)
CUTS = []
_acc = 0
for s, e in SPANS[:-1]:
    _acc += e - s; CUTS.append(_acc)
def cut_near(t):
    return min(CUTS, key=lambda c: abs(c - t))

# ---------- primitives (coordonnées en px de sortie, multipliées par s) ----------
class P:
    def __init__(self, d, s, ox=0, oy=0, z=1.0, cx=0, cy=0, ts=1.0):
        self.d, self.s, self.ox, self.oy = d, s, ox, oy
        self.z, self.cx, self.cy, self.ts = z, cx, cy, ts
    def xy(self, x, y):
        return (((x - self.cx) * self.z + self.cx - self.ox) * self.s, ((y - self.cy) * self.z + self.cy - self.oy) * self.s)
    def fs(self, size):
        return int(size * self.s * self.z * self.ts)
    def text(self, x, y, txt, fnt, size, fill, anchor="mm"):
        self.d.text(self.xy(x, y), txt, font=font(fnt, self.fs(size)), fill=fill, anchor=anchor)
    def tw(self, txt, fnt, size):
        return font(fnt, self.fs(size)).getlength(txt) / (self.s * self.z)
    def rbox(self, x0, y0, x1, y1, r, fill=None, outline=None, width=3):
        if x1 <= x0 or y1 <= y0: return
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        self.d.rounded_rectangle((*self.xy(x0, y0), *self.xy(x1, y1)), radius=r * self.s * self.z, fill=fill, outline=outline, width=max(1, int(width * self.s * self.z)))
    def line(self, pts, fill, width=4):
        width *= self.z
        self.d.line([self.xy(*p) for p in pts], fill=fill, width=int(width * self.s), joint="curve")
        r = width / 2 / self.z
        for p in (pts[0], pts[-1]):
            self.circle(p[0], p[1], r, fill=fill)
    def circle(self, x, y, r, fill=None, outline=None, width=3):
        self.d.ellipse((*self.xy(x - r, y - r), *self.xy(x + r, y + r)), fill=fill, outline=outline, width=max(1, int(width * self.s * self.z)))
    def arc(self, x, y, r, a0, a1, fill, width=4):
        self.d.arc((*self.xy(x - r, y - r), *self.xy(x + r, y + r)), a0, a1, fill=fill, width=int(width * self.s))
    def poly(self, pts, fill):
        self.d.polygon([self.xy(*p) for p in pts], fill=fill)
    def arrow(self, x0, y0, x1, y1, k, fill, width=5, head=16):
        if k <= 0: return
        x1, y1 = lerp(x0, x1, k), lerp(y0, y1, k)
        a = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * 0.8 * math.cos(a), y1 - head * 0.8 * math.sin(a)
        self.line([(x0, y0), (bx, by)], fill, width)
        self.poly([(x1, y1), (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5)),
                   (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))], fill)
    def dashed(self, pts, k, fill, width=4, dash=14, gap=12):
        """polyligne pointillée tracée jusqu'à la fraction k"""
        segs = list(zip(pts, pts[1:]))
        L = sum(math.dist(a, b) for a, b in segs); lim = L * clamp(k); pos = 0
        for a, b in segs:
            l = math.dist(a, b)
            u = 0
            while u < l and pos + u < lim:
                u1 = min(u + dash, l, lim - pos)
                p0 = (lerp(a[0], b[0], u / l), lerp(a[1], b[1], u / l))
                p1 = (lerp(a[0], b[0], u1 / l), lerp(a[1], b[1], u1 / l))
                self.line([p0, p1], fill, width)
                u += dash + gap
            pos += l

def star(p, x, y, r, fill, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5 + rot
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    p.poly(pts, fill)

def person(p, x, y, sc, fill):
    p.circle(x, y - 34 * sc, 20 * sc, fill=fill)
    p.d.chord((*p.xy(x - 38 * sc, y - 8 * sc), *p.xy(x + 38 * sc, y + 62 * sc)), 180, 360, fill=fill)

def cross_icon(p, x, y, r, fill):
    a = r * 0.36
    p.rbox(x - a, y - r, x + a, y + r, a * 0.4, fill=fill)
    p.rbox(x - r, y - a, x + r, y + a, a * 0.4, fill=fill)

def check(p, x, y, r, fill, k=1, width=7):
    pts = [(x - r * 0.55, y + r * 0.02), (x - r * 0.12, y + r * 0.45), (x + r * 0.6, y - r * 0.45)]
    if k < 0.5:
        q = (lerp(pts[0][0], pts[1][0], k * 2), lerp(pts[0][1], pts[1][1], k * 2)); p.line([pts[0], q], fill, width)
    else:
        q = (lerp(pts[1][0], pts[2][0], (k - .5) * 2), lerp(pts[1][1], pts[2][1], (k - .5) * 2)); p.line([pts[0], pts[1], q], fill, width)

def xmark(p, x, y, r, fill, k=1, width=7):
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    if k1 > 0: p.line([(x - r, y - r), (lerp(x - r, x + r, k1), lerp(y - r, y + r, k1))], fill, width)
    if k2 > 0: p.line([(x + r, y - r), (lerp(x + r, x - r, k2), lerp(y - r, y + r, k2))], fill, width)

def bulb(p, x, y, r, fill, glow=0):
    if glow > 0:
        for i in range(8):
            a = -math.pi / 2 + (i - 3.5) * 0.42
            p.line([(x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35), (x + math.cos(a) * r * (1.35 + 0.35 * glow), y + math.sin(a) * r * (1.35 + 0.35 * glow))], rgba(GOLD, glow), 5)
    p.circle(x, y, r, fill=fill)
    p.rbox(x - r * 0.45, y + r * 0.75, x + r * 0.45, y + r * 1.25, 6, fill=fill)
    p.line([(x - r * 0.35, y + r * 1.42), (x + r * 0.35, y + r * 1.42)], fill, 6)

def magnifier(p, x, y, r, fill, width=8):
    p.circle(x, y, r, outline=fill, width=width)
    p.line([(x + r * 0.72, y + r * 0.72), (x + r * 1.45, y + r * 1.45)], fill, width * 1.6)

def paper(p, x0, y0, w, h, k_lines, hand=True, fill=WHITE, a=1.0):
    p.rbox(x0, y0, x0 + w, y0 + h, 14, fill=rgba(fill, a))
    ink = rgba((40, 44, 60), a)
    p.text(x0 + 24, y0 + 34, "Ordonnance", "Inter-Bold", 24, ink, anchor="lm")
    p.line([(x0 + 24, y0 + 58), (x0 + w - 24, y0 + 58)], rgba((40, 44, 60), a * 0.3), 2)
    n = 5
    for i in range(n):
        kk = clamp(k_lines * n - i)
        if kk <= 0: break
        yy = y0 + 90 + i * (h - 120) / n
        xe = x0 + 24 + (w - 60 - (i % 2) * 50) * kk
        if hand:
            pts = []
            xx = x0 + 24
            while xx < xe:
                pts.append((xx, yy + 7 * math.sin(xx * 0.11 + i) + 3 * math.sin(xx * 0.37)))
                xx += 4
            if len(pts) > 1: p.line(pts, ink, 3)
        else:
            p.rbox(x0 + 24, yy - 5, xe, yy + 5, 5, fill=rgba((90, 96, 112), a))

def phone(p, cx, cy, w, h, fill_k):
    p.rbox(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 34, fill=rgba((24, 25, 31), 1), outline=rgba(GREY, 1), width=4)
    p.rbox(cx - w / 2 + 14, cy - h / 2 + 40, cx + w / 2 - 14, cy + h / 2 - 30, 18, fill=rgba(WHITE, 0.96))
    p.rbox(cx - 30, cy - h / 2 + 16, cx + 30, cy - h / 2 + 24, 4, fill=rgba(GREY, 1))
    x0 = cx - w / 2 + 34
    p.text(x0, cy - h / 2 + 76, "Ordonnance", "Inter-Bold", 22, (40, 44, 60, 255), anchor="lm")
    for i in range(6):
        kk = clamp(fill_k * 6 - i)
        if kk <= 0: break
        yy = cy - h / 2 + 120 + i * 42
        p.rbox(x0, yy - 6, x0 + (w - 68 - (i % 3) * 40) * kk, yy + 6, 6, fill=(120, 126, 140, 255) if i % 3 else GOLD + (255,))

def chip(p, x, y, txt, k, col=GOLD, size=26, fg=(20, 20, 24)):
    if k <= 0: return
    tw = p.tw(txt, "Inter-Bold", size)
    w, h = tw + 44, size * 1.9
    yy = y + (1 - k) * 12
    p.rbox(x - w / 2, yy - h / 2, x + w / 2, yy + h / 2, h / 2, fill=rgba(col, k))
    p.text(x, yy + 1, txt, "Inter-Bold", size, rgba(fg, k))

def box(p, x, y, w, h, txt, k, col=WHITE, size=30, sub=None, filled=False):
    if k <= 0: return
    yy = y + (1 - k) * 14
    if filled:
        p.rbox(x - w / 2, yy - h / 2, x + w / 2, yy + h / 2, 22, fill=rgba(col, k))
        fg = (20, 20, 24)
    else:
        p.rbox(x - w / 2, yy - h / 2, x + w / 2, yy + h / 2, 22, fill=rgba(WHITE, 0.07 * k), outline=rgba(col, k), width=3)
        fg = col
    if sub:
        p.text(x, yy - 16, txt, "Inter-ExtraBold", size, rgba(fg, k))
        p.text(x, yy + 22, sub, "Inter-Medium", size * 0.62, rgba(fg if filled else GREY, k))
    else:
        p.text(x, yy, txt, "Inter-ExtraBold", size, rgba(fg, k))

def appear(t, t0, d=0.35):
    return ease((t - t0) / d)

# ---------- animation « sticker » ----------
def back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pop(t, t0, d=0.42):
    return back((t - t0) / d), clamp((t - t0) / 0.12)

from edl import ISLANDS as _I
END_SPEECH = E(_I[-1][1])

def sticker(p, cx, cy, w, h, t, t0, txt=None, size=40, fill=WHITE, fg=INK, icon=None, font_="Inter-ExtraBold", r=None):
    """Étiquette pleine qui rebondit à son apparition ; icon(p, x, y, s, a) dessine à gauche du texte."""
    sc, a = pop(t, t0)
    if a <= 0: return 0
    w2, h2 = w * sc / 2, h * sc / 2
    p.rbox(cx - w2 + 6, cy - h2 + 10, cx + w2 + 6, cy + h2 + 10, (r or h / 2.6) * sc, fill=rgba((0, 0, 0), 0.35 * a))
    p.rbox(cx - w2, cy - h2, cx + w2, cy + h2, (r or h / 2.6) * sc, fill=rgba(fill, a))
    tx = cx
    if icon:
        iw = h * 0.62
        tw = p.tw(txt, font_, size) if txt else 0
        x0 = cx - (iw + 18 + tw) / 2 * sc
        icon(p, x0 + iw / 2 * sc, cy, sc * h / 100, a, fg)
        tx = x0 + (iw + 18) * sc + tw * sc / 2
    if txt:
        p.text(tx, cy + 2, txt, font_, max(8, int(size * sc)), rgba(fg, a))
    return a

# icônes au trait (couleur fg), s = échelle
def ic_search(p, x, y, s, a, fg):
    p.circle(x - 6 * s, y - 6 * s, 20 * s, outline=rgba(fg, a), width=6 * s)
    p.line([(x + 9 * s, y + 9 * s), (x + 24 * s, y + 24 * s)], rgba(fg, a), 8 * s)
def ic_people(p, x, y, s, a, fg):
    person(p, x - 13 * s, y + 8 * s, 0.6 * s, rgba(fg, a)); person(p, x + 15 * s, y + 8 * s, 0.6 * s, rgba(fg, a))
def ic_check(p, x, y, s, a, fg):
    p.circle(x, y, 26 * s, fill=rgba(fg, a)); check(p, x, y, 18 * s, rgba(GOLD, a), width=6 * s)
def ic_clock(p, x, y, s, a, fg):
    p.circle(x, y, 24 * s, outline=rgba(fg, a), width=6 * s)
    p.line([(x, y), (x, y - 14 * s)], rgba(fg, a), 6 * s); p.line([(x, y), (x + 11 * s, y)], rgba(fg, a), 6 * s)
def ic_cal(p, x, y, s, a, fg):
    p.rbox(x - 24 * s, y - 22 * s, x + 24 * s, y + 24 * s, 7 * s, outline=rgba(fg, a), width=5 * s)
    p.rbox(x - 24 * s, y - 22 * s, x + 24 * s, y - 8 * s, 5 * s, fill=rgba(fg, a))
def ic_x(p, x, y, s, a, fg):
    xmark(p, x, y, 15 * s, rgba(fg, a), width=7 * s)
def ic_comment(p, x, y, s, a, fg):
    p.rbox(x - 26 * s, y - 22 * s, x + 26 * s, y + 14 * s, 9 * s, fill=rgba(fg, a))
    p.poly([(x - 14 * s, y + 12 * s), (x - 2 * s, y + 12 * s), (x - 16 * s, y + 28 * s)], rgba(fg, a))

