# Calque graphique v2 : sous-titres blancs à contour noir (mots-clés sur pastille jaune),
# illustrations en « stickers » blancs qui rebondissent sur le bas de l'image, écrans d'étape
# plein écran (vidéo floutée derrière, ils cachent les changements de prise) et écran de fin
# en texte sur sa vidéo floutée. Tout est dessiné en sRGB puis
# converti en HLG BT.2020 au moment du rendu.
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from words import captions, src2edit, SPANS, TOTAL_SPEECH

W, H = 1080, 1920
FPS = 60.0
HOLD = 4.6
TOTAL = TOTAL_SPEECH + HOLD
WHITE = (255, 255, 255)
GOLD = (255, 210, 63)   # v2 : jaune vif (accent unique)
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

END_SPEECH = E(171.36)

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

# ---------- illustrations (bas de l'image, sous les sous-titres) ----------
def card_hook(p, t):
    sticker(p, 540, 1215, 420, 120, t, E(20.25), "5 ÉTAPES", 62, fill=GOLD, font_="InterDisplay-Black")
    for i in range(5):
        sticker(p, 300 + i * 120, 1375, 90, 90, t, E(20.45) + i * 0.1, str(i + 1), 42, font_="InterDisplay-Black", r=45)

def card_pitch(p, t):
    k = 1 - ease_io((t - E(29.4)) / 0.2)
    if k > 0 and t > E(24.65):
        sticker(p, 540, 1220, 860, 110, t, E(24.65), "Que veux-tu faire exactement ?", 40)
    sticker(p, 540, 1220 if t > E(29.4) else 1360, 640, 104, t, E(26.9), "PITCH EN MOINS D'1 MIN", 38, fill=GOLD, icon=ic_clock)
    for i, (txt, ts) in enumerate([("Le problème", 29.55), ("Le besoin", 30.9), ("La solution", 31.8), ("La valeur ajoutée", 33.85)]):
        x, y = (300, 1370) if i == 0 else (780, 1370) if i == 1 else (300, 1490) if i == 2 else (780, 1490)
        sticker(p, x, y, 440, 96, t, E(ts), txt, 38, fill=GOLD if i == 3 else WHITE)

def card_market(p, t):
    sticker(p, 540, 1200, 600, 104, t, E(48.1), "Étude de marché", 42, icon=ic_search)
    sticker(p, 540, 1330, 600, 104, t, E(54.4), "Futurs clients", 42, icon=ic_people)
    sticker(p, 540, 1460, 600, 104, t, E(58.4), "Besoin validé", 42, fill=GOLD, icon=ic_check)

def card_goals(p, t):
    if t < E(105.3):
        a = sticker(p, 540, 1220, 860, 104, t, E(99.85), "Je veux atteindre telle chose", 38, icon=ic_x)
        kx = clamp((t - E(101.7)) / 0.3)
        if a and kx > 0:
            tw = p.tw("Je veux atteindre telle chose", "Inter-ExtraBold", 38)
            x0 = 540 - tw / 2 + 25
            p.line([(x0, 1222), (lerp(x0, x0 + tw, kx), 1222)], rgba(INK, a), 6)
        sticker(p, 540, 1360, 860, 112, t, E(102.5), "À telle date  →  tel chiffre", 44, fill=GOLD, icon=ic_cal)
        return
    sc, a = pop(t, E(105.35))
    if a <= 0: return
    x0, x1, y0, y1 = 540 - 440 * sc, 540 + 440 * sc, 1290 - 170 * sc, 1290 + 170 * sc
    p.rbox(x0 + 6, y0 + 10, x1 + 6, y1 + 10, 40, fill=rgba((0, 0, 0), 0.35 * a))
    p.rbox(x0, y0, x1, y1, 40, fill=rgba(WHITE, a))
    p.text(540, 1180, "L'évolution de ton projet", "Inter-ExtraBold", int(40 * sc), rgba(INK, a))
    lx0, lx1, ly = 150, 820, 1300
    kl = clamp((t - E(105.6)) / 1.6)
    p.line([(lx0, ly), (lx1, ly)], rgba(INK, 0.15 * a), 10)
    if kl > 0: p.line([(lx0, ly), (lerp(lx0, lx1, kl), ly)], rgba(INK, a), 10)
    for i in range(4):
        x = lerp(lx0, lx1, (i + 1) / 5)
        ss, ka = pop(t, E(109.5) + i * 0.32, 0.35)
        p.circle(x, ly, 28, fill=rgba(WHITE, a), outline=rgba(INK, a), width=5)
        if ka > 0:
            p.circle(x, ly, 28 * ss, fill=rgba(GOLD, ka)); check(p, x, ly, 18, rgba(INK, ka), width=6)
        p.text(x, ly + 60, f"Étape {i + 1}", "Inter-Bold", 26, rgba(INK, 0.7 * a))
    st, kt = pop(t, E(111.5))
    if kt > 0:
        for r, c in [(56, INK), (38, GOLD), (20, INK)]:
            p.circle(880, ly, r * st, fill=rgba(c, kt))
        p.text(880, ly + 86, "Objectif", "Inter-ExtraBold", 28, rgba(INK, kt))

def card_people(p, t):
    cx, cy = 540, 1320
    pts = [(250, 1200), (830, 1200), (300, 1460), (780, 1460)]
    for i, (x, y) in enumerate(pts):
        t0 = E(154.0) + i * 0.3
        k = clamp((t - t0) / 0.3)
        if k > 0: p.line([(cx, cy), (lerp(cx, x, k), lerp(cy, y, k))], rgba(WHITE, 0.9), 6)
        sc, a = pop(t, t0 + 0.15)
        if a > 0:
            p.circle(x, y, 58 * sc, fill=rgba(WHITE, a)); person(p, x, y + 16 * sc, 0.95 * sc, rgba(INK, a))
    sc, a = pop(t, E(153.6))
    if a > 0:
        p.circle(cx, cy, 82 * sc, fill=rgba(GOLD, a)); p.text(cx, cy, "TOI", "InterDisplay-Black", int(44 * sc), rgba(INK, a))
    sticker(p, 540, 1560, 520, 80, t, E(155.6), "Les bonnes personnes", 34, fill=GOLD)

def card_invest(p, t):
    sc, a = pop(t, E(159.55))
    if a <= 0: return
    x0, x1, y0, y1 = 540 - 440 * sc, 540 + 440 * sc, 1300 - 190 * sc, 1300 + 190 * sc
    p.rbox(x0 + 6, y0 + 10, x1 + 6, y1 + 10, 40, fill=rgba((0, 0, 0), 0.35 * a))
    p.rbox(x0, y0, x1, y1, 40, fill=rgba(WHITE, a))
    gx0, gx1, gy0, gy1 = 160, 900, 1150, 1440
    p.line([(gx0, gy0), (gx0, gy1), (gx1, gy1)], rgba(INK, 0.5 * a), 5)
    kg = clamp((t - E(160.2)) / 1.6)
    if kg > 0:
        pts = [(lerp(gx0, gx1, i / 60), gy1 - 130 * (1 - math.exp(-i / 60 * 5))) for i in range(int(60 * kg) + 2)]
        p.line(pts, rgba(INK, 0.45 * a), 7)
        p.text(gx1, gy1 - 160, "Sans investisseurs", "Inter-Bold", 28, rgba(INK, 0.6 * a), anchor="rm")
    kc = appear(t, E(163.6))
    if kc > 0:
        p.dashed([(gx0, gy1 - 138), (gx1, gy1 - 138)], kc, rgba(INK, 0.6), 4)
    km = clamp((t - E(165.8)) / 1.8)
    if km > 0:
        pts = []
        for i in range(int(60 * km) + 2):
            u = i / 60
            pts.append((lerp(gx0, gx1 - 130, u), gy1 - 130 * (1 - math.exp(-u * 5)) * (1 - u) - 250 * u ** 2.2))
        p.line(pts, rgba(GOLD, a), 10)
        ex, ey = pts[-1]
        p.circle(ex, ey, 34, fill=rgba(GOLD, a)); p.text(ex, ey + 1, "€", "InterDisplay-Black", 36, rgba(INK, a))
    sticker(p, 760, 1175, 250, 72, t, E(170.3), "Agrandir", 34, fill=INK, fg=GOLD)

def appear(t, t0, d=0.35):
    return ease((t - t0) / d)

# ---------- écrans d'étape plein écran ----------
STEPS = [("CLARIFIE", "LE BESOIN"), ("VALIDE", "LE BESOIN"), ("FIXE DES OBJECTIFS", "CHIFFRÉS"),
         ("RENCONTRE LES", "BONNES PERSONNES"), ("RENCONTRE DES", "INVESTISSEURS")]

def highlight(p, x, y, txt, size, t, t0, font_="InterDisplay-Black"):
    """Texte noir sur pastille jaune qui se déroule de gauche à droite."""
    k = ease((t - t0) / 0.4)
    if k <= 0: return
    tw = p.tw(txt, font_, size)
    x0 = x - tw / 2 - 26
    p.rbox(x0, y - size * 0.72, lerp(x0, x + tw / 2 + 26, k), y + size * 0.72, 18, fill=rgba(GOLD, 1))
    if k > 0.5:
        p.text(x, y + 3, txt, font_, size, rgba(INK, clamp((k - 0.5) * 3)))

def make_full(n):
    def fn(p, t):
        a = FULLS[n][0]
        sticker(p, 540, 330, 300, 76, t, a - 0.1, f"ÉTAPE {n + 1} / 5", 34)
        sc, k = pop(t, a + 0.0, 0.5)
        if k > 0:
            p.text(540, 560, str(n + 1), "InterDisplay-Black", int(330 * sc), rgba(WHITE, k))
        k1 = appear(t, a + 0.2)
        p.text(540, 790 + (1 - k1) * 20, STEPS[n][0], "InterDisplay-Black", 70, rgba(WHITE, k1))
        highlight(p, 540, 885, STEPS[n][1], 70, t, a + 0.35)
        for i in range(5):
            x = 540 + (i - 2) * 64
            done = i <= n
            p.circle(x, 1270, 13 if i != n else 18, fill=rgba(GOLD if done else WHITE, k1 * (1 if done else 0.35)))
    return fn

# icônes des 5 étapes pour l'écran de fin (dessinées en INK dans un carré blanc)
def ic_bulb(p, x, y, s, a, fg):
    p.circle(x, y - 6 * s, 20 * s, fill=rgba(fg, a))
    p.rbox(x - 9 * s, y + 12 * s, x + 9 * s, y + 24 * s, 3 * s, fill=rgba(fg, a))
def ic_target(p, x, y, s, a, fg):
    for r, f in [(26, fg), (18, WHITE), (10, fg)]:
        p.circle(x, y, r * s, fill=rgba(f, a))
def ic_euro(p, x, y, s, a, fg):
    p.circle(x, y, 26 * s, fill=rgba(fg, a))
    p.text(x, y + 1, "€", "InterDisplay-Black", int(32 * s), rgba(WHITE, a))
END_ICONS = [ic_bulb, ic_check, ic_target, ic_people, ic_euro]
END_BG = (16, 16, 20)

def full_final(p, t):
    a = FULLS[-1][0]
    k0 = appear(t, a + 0.1)
    p.text(540, 330 + (1 - k0) * 20, "TU BLOQUES À", "InterDisplay-Black", 92, rgba(WHITE, k0))
    highlight(p, 540, 450, "QUELLE ÉTAPE ?", 92, t, a + 0.3)
    for i, (l1, l2) in enumerate(STEPS):
        t0 = a + 0.6 + i * 0.16
        sc, k = pop(t, t0, 0.35)
        if k <= 0: continue
        y = 640 + i * 118
        p.circle(130, y, 38 * sc, fill=rgba(GOLD, k))
        p.text(130, y + 2, str(i + 1), "InterDisplay-Black", int(42 * sc), rgba(INK, k))
        p.rbox(196, y - 44 * sc, 284, y + 44 * sc, 20 * sc, fill=rgba(WHITE, k))
        END_ICONS[i](p, 240, y, 0.95 * sc, k, INK if i != 1 else INK)
        p.text(316, y + 2, f"{l1} {l2}".capitalize(), "Inter-ExtraBold", 44, rgba(WHITE, k), anchor="lm")
    sticker(p, 540, 1320, 900, 130, t, a + 1.6, "Écris le numéro en commentaire", 46, icon=ic_comment)

# ---------- programme ----------
PRE = 0.26
FULLS = []
def add_full(a, b, fn):
    FULLS.append((a, b, fn))
add_full(cut_near(E(22.5)), cut_near(E(24.45)), make_full(0))
add_full(cut_near(E(35.6)), cut_near(E(47.99)), make_full(1))
add_full(cut_near(E(96.0)), cut_near(E(99.6)), make_full(2))
add_full(cut_near(E(150.0)), cut_near(E(153.43)), make_full(3))
add_full(E(157.75), cut_near(E(159.36)), make_full(4))
add_full(END_SPEECH + 0.15, TOTAL + 1, full_final)

CARDS = [
    (0.0, FULLS[0][0], card_hook),
    (FULLS[0][1], FULLS[1][0], card_pitch),
    (FULLS[1][1], FULLS[2][0], card_market),
    (FULLS[2][1], FULLS[3][0], card_goals),
    (FULLS[3][1], FULLS[4][0], card_people),
    (FULLS[4][1], FULLS[5][0], card_invest),
]

def env(t, a, b, fi=0.3, fo=0.3):
    return min(ease_io((t - a) / fi) if a > 0 else 1.0, 1 - ease_io((t - (b - fo)) / fo) if b < TOTAL else 1.0)

def full_cover(t):
    k = 0.0
    for a, b, _ in FULLS:
        kin = ease_io((t - (a - PRE)) / (PRE - 0.03))
        kout = 1 - ease_io((t - (b + 0.03)) / (PRE - 0.03)) if b < TOTAL else 1
        k = max(k, min(kin, kout))
    return k

# ---------- sous-titres : blanc, contour noir, mot-clé sur pastille jaune ----------
CAPS = captions()
CAP_Y = 1045
def draw_caption(img, t):
    g = next((c for c in CAPS if c["s"] <= t < c["e"]), None)
    if g is None:
        return
    size = 70
    f = font("InterDisplay-Black", size)
    sp = f.getlength(" ")
    ws = [(w["w"].upper(), w["hl"], f.getlength(w["w"].upper()), w["s"]) for w in g["words"]]
    lines, cur, cw = [], [], 0
    for x in ws:
        if cur and cw + sp + x[2] > 960:
            lines.append(cur); cur, cw = [], 0
        cur.append(x); cw += (sp if len(cur) > 1 else 0) + x[2]
    lines.append(cur)
    lay = Image.new("RGBA", (W * SS, 300 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    F = font("InterDisplay-Black", size * SS)
    lh = size * 1.18
    y = 150 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        tw = sum(x[2] for x in ln) + sp * (len(ln) - 1)
        x = (W - tw) / 2
        for wd, hl, ww, ts in ln:
            k = clamp((t - ts + 0.04) / 0.14)
            if k <= 0:
                x += ww + sp; continue
            sc = back(k) * 0.25 + 0.75
            cx = x + ww / 2
            Fs = font("InterDisplay-Black", max(8, int(size * SS * sc)))
            if hl:
                bw, bh = (ww / 2 + 14) * sc, size * 0.62 * sc
                d.rounded_rectangle(((cx - bw) * SS, (y - bh) * SS, (cx + bw) * SS, (y + bh) * SS), radius=14 * SS, fill=GOLD + (255,))
                d.text((cx * SS, y * SS + 2 * SS), wd, font=Fs, fill=INK + (255,), anchor="mm")
            else:
                d.text((cx * SS, y * SS + 2 * SS), wd, font=Fs, fill=WHITE + (255,), anchor="mm", stroke_width=int(7 * SS * sc), stroke_fill=(0, 0, 0, 255))
            x += ww + sp
        y += lh
    lay = lay.resize((W, 300), Image.LANCZOS)
    img.alpha_composite(lay, (0, CAP_Y - 150))

# ---------- composition ----------
def draw_area(fn, t, box_, a):
    x0, y0, x1, y1 = box_
    im = Image.new("RGBA", ((x1 - x0) * SS, (y1 - y0) * SS), (0, 0, 0, 0))
    fn(P(ImageDraw.Draw(im), SS, ox=x0, oy=y0), t)
    im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    if a < 1:
        r, g, b, al = im.split()
        im = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))
    return im

FULL_BOX = (0, 200, 1080, 1480)
CARD_BOX = (0, 1080, 1080, 1640)

def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frosts = []
    cov = full_cover(t)
    if cov > 0:
        frosts.append(((0, 0, W, H), 0, cov, 0.5))
    fa = FULLS[-1][0]
    kb = ease_io((t - (fa - 0.1)) / 0.35)
    if kb > 0:
        ImageDraw.Draw(img).rectangle((0, 0, W, H), fill=END_BG + (int(255 * kb),))
    for a, b, fn in FULLS:
        if a - PRE - 0.05 <= t < b + PRE + 0.05:
            kc = env(t, a - 0.08, b + 0.25, 0.3, 0.25) if b < TOTAL else ease_io((t - (a - 0.08)) / 0.3)
            if kc > 0:
                img.alpha_composite(draw_area(fn, t, FULL_BOX, kc * cov), FULL_BOX[:2])
    for a, b, fn in CARDS:
        if a - 0.05 <= t < b + 0.05:
            kc = env(t, a, b, 0.2, 0.3) * (1 - cov)
            if kc > 0.003:
                img.alpha_composite(draw_area(fn, t, CARD_BOX, kc), CARD_BOX[:2])
    if t < END_SPEECH + 0.4:
        draw_caption(img, t)
    w = int(W * min(t / TOTAL, 1))
    if w > 1:
        ImageDraw.Draw(img).rectangle((0, 0, w, 6), fill=GOLD + (255,))
    return img, frosts
