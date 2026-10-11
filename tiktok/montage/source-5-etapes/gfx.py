# Calque graphique : sous-titres, cartes d'illustration (vitre dépolie sur le bas de l'image,
# sous son visage) et cartes d'étape plein écran (décor flouté derrière, elles cachent les
# changements de prise). Tout est dessiné en sRGB puis
# converti en HLG BT.2020 au moment du rendu.
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from words import captions, src2edit, SPANS, TOTAL_SPEECH

W, H = 1080, 1920
FPS = 60.0
HOLD = 4.4
TOTAL = TOTAL_SPEECH + HOLD
WHITE = (255, 255, 255)
GOLD = (222, 172, 72)
GREY = (205, 207, 213)
DIM = (110, 112, 120)
FD = "/usr/share/fonts/opentype/inter/"
SS = 2

_f = {}
def font(name, size):
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

# ---------- cartes (en bas, sur le polo ; le visage reste visible) ----------
CARD = (60, 1160, 1020, 1530)
CW, CH = CARD[2] - CARD[0], CARD[3] - CARD[1]

def appear(t, t0, d=0.35):
    return ease((t - t0) / d)

def card_hook(p, t):
    p.text(480, 62, "RÉUSSIR TON PROJET", "Inter-Bold", 24, rgba(GREY, appear(t, E(18.75))))
    for i in range(5):
        k = appear(t, E(19.1) + i * 0.22, 0.3)
        if k <= 0: continue
        x = 160 + i * 160
        p.circle(x, 205, 58 * lerp(0.6, 1, k), fill=rgba(GOLD if i == 4 else WHITE, (1 if i == 4 else 0.08) * k), outline=rgba(GOLD, k), width=3)
        p.text(x, 205, str(i + 1), "InterDisplay-Black", 40, rgba((20, 20, 24) if i == 4 else WHITE, k))
    p.text(480, 335, "étapes à valider", "Inter-ExtraBold", 28, rgba(GOLD, appear(t, E(21.2))))

def card_pitch(p, t):
    kq = appear(t, E(24.65)) * (1 - ease_io((t - E(26.75)) / 0.25))
    if kq > 0:
        p.text(480, 150, "Qu'est-ce que tu veux", "Inter-ExtraBold", 40, rgba(WHITE, kq))
        p.text(480, 230, "faire exactement ?", "Inter-ExtraBold", 40, rgba(GOLD, kq))
    kc = appear(t, E(26.9))
    if kc > 0:
        chip(p, 480, 52, "TON PITCH EN MOINS D'1 MIN", kc, size=22)
        # petit chrono qui tourne
        cx, cy = 480 + p.tw("TON PITCH EN MOINS D'1 MIN", "Inter-Bold", 22) / 2 + 60, 52
        p.circle(cx, cy, 24, outline=rgba(GOLD, kc), width=4)
        a = -90 + 360 * clamp((t - E(27.0)) / 8)
        p.line([(cx, cy), (cx + 15 * math.cos(math.radians(a)), cy + 15 * math.sin(math.radians(a)))], rgba(GOLD, kc), 4)
    items = [(250, 165, "Le problème", 29.55), (710, 165, "Le besoin", 30.9), (250, 295, "La solution", 31.8), (710, 295, "La valeur ajoutée", 33.85)]
    for i, (x, y, txt, ts) in enumerate(items):
        k = appear(t, E(ts))
        box(p, x, y, 420, 104, txt, k, col=GOLD if i == 3 else WHITE, size=26, filled=(i == 3))

def card_market(p, t):
    k1 = appear(t, E(48.1))
    if k1 > 0:
        for i, hgt in enumerate([60, 100, 80, 130]):
            x = 110 + i * 42
            p.rbox(x, 250 - hgt * k1, x + 28, 250, 6, fill=rgba(WHITE, 0.35 * k1))
        magnifier(p, 185 + 16 * math.sin(t * 2.4), 165, 52, rgba(GOLD, k1), 8)
        p.text(175, 320, "Étude de marché", "Inter-ExtraBold", 28, rgba(WHITE, k1))
    p.arrow(305, 200, 375, 200, ease((t - E(53.6)) / 0.3), rgba(GREY, 1), 5)
    for i, (x, ts) in enumerate([(430, 54.4), (500, 54.8), (570, 56.6)]):
        k = appear(t, E(ts))
        if k > 0:
            person(p, x, 210 + (1 - k) * 12, 1.15, rgba(GOLD if i == 2 else WHITE, k))
    p.text(500, 320, "Futurs clients", "Inter-ExtraBold", 28, rgba(WHITE, appear(t, E(54.4))))
    p.arrow(625, 200, 695, 200, ease((t - E(58.0)) / 0.3), rgba(GREY, 1), 5)
    kv = appear(t, E(58.4), 0.4)
    if kv > 0:
        p.circle(810, 195, 70 * lerp(0.6, 1, kv), fill=rgba(GOLD, kv))
        check(p, 810, 195, 44, rgba((20, 20, 24), kv), k=clamp((t - E(58.55)) / 0.35), width=9)
        p.text(810, 320, "Besoin validé", "Inter-ExtraBold", 28, rgba(GOLD, kv))

def card_goals(p, t):
    ka = appear(t, E(99.8)) * (1 - ease_io((t - E(105.2)) / 0.3))
    if ka > 0:
        p.text(480, 95, "Je veux atteindre telle chose", "Inter-Bold", 30, rgba(GREY, ka))
        tw = p.tw("Je veux atteindre telle chose", "Inter-Bold", 30)
        kx = clamp((t - E(101.6)) / 0.35)
        if kx > 0:
            p.line([(480 - tw / 2 - 8, 97), (lerp(480 - tw / 2 - 8, 480 + tw / 2 + 8, kx), 97)], rgba(WHITE, ka), 5)
        kd = appear(t, E(102.5)) * ka
        if kd > 0:
            p.rbox(90, 185, 870, 330, 26, fill=rgba(WHITE, 0.06 * kd), outline=rgba(GOLD, kd), width=3)
            # calendrier
            p.rbox(130, 215, 220, 300, 12, outline=rgba(WHITE, kd), width=4)
            p.rbox(130, 215, 220, 238, 8, fill=rgba(WHITE, kd))
            p.text(175, 272, "J", "Inter-ExtraBold", 32, rgba(WHITE, kd))
            p.text(250, 258, "À telle date", "Inter-ExtraBold", 30, rgba(WHITE, kd), anchor="lm")
            kn = appear(t, E(104.3)) * ka
            p.arrow(560, 258, 625, 258, ease((t - E(104.0)) / 0.3) * ka, rgba(GREY, ka), 5)
            p.text(650, 258, "tel chiffre", "Inter-ExtraBold", 30, rgba(GOLD, kn), anchor="lm")
    kb = appear(t, E(105.35))
    if kb > 0:
        p.text(480, 60, "L'évolution de ton projet", "Inter-ExtraBold", 32, rgba(WHITE, kb))
        x0, x1, y = 90, 760, 215
        kl = clamp((t - E(105.6)) / 1.6)
        p.line([(x0, y), (x1, y)], rgba(WHITE, 0.25 * kb), 6)
        if kl > 0:
            p.line([(x0, y), (lerp(x0, x1, kl), y)], rgba(GOLD, kb), 6)
        for i in range(4):
            x = lerp(x0, x1, (i + 1) / 5)
            kc = appear(t, E(109.5) + i * 0.32, 0.3)
            p.circle(x, y, 26, fill=rgba(GOLD if kc > 0 else (40, 40, 46), kb), outline=rgba(GOLD, kb), width=3)
            if kc > 0:
                check(p, x, y, 18, rgba((20, 20, 24), kc), k=kc, width=5)
            p.text(x, y + 62, f"Étape {i + 1}", "Inter-Medium", 22, rgba(GREY, kb))
        kt = appear(t, E(111.5))
        if kt > 0:
            cx, cy = 850, y
            for r, c in [(62, WHITE), (42, GOLD), (22, WHITE)]:
                p.circle(cx, cy, r * kt, outline=rgba(c, kt), width=5)
            p.circle(cx, cy, 8, fill=rgba(GOLD, kt))
            p.text(cx, cy + 96, "Objectif", "Inter-ExtraBold", 24, rgba(GOLD, kt))

def card_people(p, t):
    k0 = appear(t, E(153.6))
    if k0 <= 0: return
    cx, cy = 480, 190
    pts = [(170, 120), (790, 120), (230, 300), (730, 300)]
    for i, (x, y) in enumerate(pts):
        k = appear(t, E(154.0) + i * 0.3)
        if k <= 0: continue
        p.line([(cx, cy), (lerp(cx, x, k), lerp(cy, y, k))], rgba(GOLD, 0.6 * k), 4)
        p.circle(x, y, 50, fill=rgba(WHITE, 0.08 * k), outline=rgba(WHITE, k), width=3)
        person(p, x, y + 14, 0.85, rgba(WHITE, k))
    p.circle(cx, cy, 70, fill=rgba(GOLD, k0))
    p.text(cx, cy, "Toi", "Inter-ExtraBold", 32, rgba((20, 20, 24), k0))
    kd = appear(t, E(155.6))
    p.text(480, 345, "les bonnes personnes", "Inter-ExtraBold", 28, rgba(GOLD, kd))

def card_invest(p, t):
    k0 = appear(t, E(159.55))
    if k0 <= 0: return
    x0, y0, x1, y1 = 90, 50, 870, 300
    p.line([(x0, y0), (x0, y1), (x1, y1)], rgba(GREY, 0.7 * k0), 4)
    # sans investisseurs : la courbe plafonne
    kg = clamp((t - E(160.2)) / 1.6)
    if kg > 0:
        pts = []
        for i in range(int(60 * kg) + 2):
            u = i / 60
            pts.append((lerp(x0, x1, u), y1 - 120 * (1 - math.exp(-u * 5))))
        p.line(pts, rgba(GREY, k0), 6)
        p.text(x1, y1 - 145, "Sans investisseurs", "Inter-Bold", 22, rgba(GREY, k0), anchor="rm")
    kc = appear(t, E(163.6))
    if kc > 0:
        p.dashed([(x0, y1 - 128), (x1, y1 - 128)], kc, rgba(WHITE, 0.5), 3)
        p.text(x0 + 14, y1 - 152, "plafond", "Inter-Medium", 20, rgba(WHITE, kc * 0.8), anchor="lm")
    # avec de l'argent : la courbe décolle
    km = clamp((t - E(165.8)) / 1.8)
    if km > 0:
        pts = []
        for i in range(int(60 * km) + 2):
            u = i / 60
            pts.append((lerp(x0, x1 - 120, u), y1 - 120 * (1 - math.exp(-u * 5)) * (1 - u) - 235 * u ** 2.2 - 0 * u))
        p.line(pts, rgba(GOLD, 1), 7)
        ex, ey = pts[-1]
        p.circle(ex, ey, 30, fill=rgba(GOLD, 1))
        p.text(ex, ey + 1, "€", "Inter-ExtraBold", 30, (20, 20, 24, 255))
    kg2 = appear(t, E(170.3))
    if kg2 > 0:
        p.text(x1 - 120 + 50, y0 + 8, "Grandir", "Inter-ExtraBold", 26, rgba(GOLD, kg2), anchor="lm")

# ---------- cartes d'étape plein écran ----------
STEPS = [("Clarifie", "le besoin", "Clarifier"), ("Valide", "le besoin", "Valider"), ("Fixe des objectifs", "chiffrés", "Objectifs"),
         ("Rencontre les", "bonnes personnes", "Réseau"), ("Rencontre des", "investisseurs", "Investisseurs")]

def step_track(p, t, n, t0, y=1290):
    x0, x1 = 170, 910
    pos = lambda k: lerp(x0, x1, k / 4)
    kl = appear(t, t0, 0.4)
    p.line([(x0, y), (x1, y)], rgba(WHITE, 0.22 * kl), 4)
    kf = ease_io((t - t0 - 0.1) / 0.6)
    if n > 0:
        p.line([(x0, y), (lerp(pos(max(n - 1, 0)), pos(n), kf), y)], rgba(GOLD, kl), 5)
    for k in range(5):
        on = k < n or (k == n and kf > 0.9)
        r = 18 if k != n else 18 * lerp(1, 1.5, appear(t, t0 + 0.55, 0.3))
        p.circle(pos(k), y, r, fill=rgba(GOLD if on else (34, 34, 40), kl), outline=rgba(GOLD if k <= n else GREY, kl), width=3)
        p.text(pos(k), y + 58, STEPS[k][2], "Inter-Bold" if k == n else "Inter-Medium", 22, rgba(GOLD if k == n else GREY, kl * (1 if k <= n else 0.6)))

def make_full(n):
    def fn(p, t):
        a = FULLS[n][0]
        k0 = appear(t, a - 0.05)
        p.text(540, 360, f"ÉTAPE {n + 1} / 5", "Inter-Bold", 30, rgba(GREY, k0))
        kn = appear(t, a + 0.05, 0.45)
        p.circle(540, 530, 105 * lerp(0.7, 1, kn), outline=rgba(GOLD, kn), width=5)
        p.text(540, 532, str(n + 1), "InterDisplay-Black", 120, rgba(GOLD, kn))
        k1 = appear(t, a + 0.2)
        p.text(540, 735 + (1 - k1) * 16, STEPS[n][0], "Inter-ExtraBold", 72, rgba(WHITE, k1))
        k2 = appear(t, a + 0.35)
        p.text(540, 830 + (1 - k2) * 16, STEPS[n][1], "InterDisplay-Black", 80, rgba(GOLD, k2))
        step_track(p, t, n, a + 0.2)
    return fn

def full_final(p, t):
    a = FULLS[-1][0]
    p.text(540, 330, "LES 5 ÉTAPES", "Inter-Bold", 30, rgba(GREY, appear(t, a)))
    for i, (l1, l2, _) in enumerate(STEPS):
        k = appear(t, a + 0.15 + i * 0.22, 0.3)
        if k <= 0: continue
        y = 440 + i * 105
        x = 150 + (1 - k) * 30
        p.circle(x, y, 30, fill=rgba(GOLD, k))
        check(p, x, y, 20, rgba((20, 20, 24), k), k=clamp((t - a - 0.3 - i * 0.22) / 0.3), width=6)
        txt = f"{l1} {l2}"
        p.text(x + 58, y, txt, "Inter-ExtraBold", 46, rgba(WHITE, k), anchor="lm")
    kc = appear(t, a + 1.6, 0.45)
    if kc > 0:
        p.text(540, 1110, "Tu bloques à quelle étape ?", "Inter-ExtraBold", 54, rgba(WHITE, kc))
        chip(p, 540, 1240, "Commente 1, 2, 3, 4 ou 5", kc, size=40)

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
add_full(TOTAL_SPEECH + 0.05, TOTAL + 1, full_final)

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
    """Opacité du voile plein écran : couvre la vidéo PRE s avant la première coupe, la découvre PRE s après la dernière."""
    k = 0.0
    for a, b, _ in FULLS:
        kin = ease_io((t - (a - PRE)) / (PRE - 0.03))
        kout = 1 - ease_io((t - (b + 0.03)) / (PRE - 0.03)) if b < TOTAL else 1
        k = max(k, min(kin, kout))
    return k

# ---------- sous-titres ----------
CAPS = captions()
CAP_Y = 1045
def draw_caption(img, t):
    g = next((c for c in CAPS if c["s"] <= t < c["e"]), None)
    if g is None:
        return
    k = ease((t - g["s"]) / 0.12)
    size = int(round(74 * lerp(0.92, 1.0, k)))
    f = font("Inter-ExtraBold", size)
    sp = f.getlength(" ")
    ws = [(w["w"], w["hl"], f.getlength(w["w"]), w["s"]) for w in g["words"]]
    lines, cur, cw = [], [], 0
    for x in ws:
        if cur and cw + sp + x[2] > 940:
            lines.append(cur); cur, cw = [], 0
        cur.append(x); cw += (sp if len(cur) > 1 else 0) + x[2]
    lines.append(cur)
    lay = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(lay), ImageDraw.Draw(sh)
    lh = size * 1.12
    y = 150 - lh * len(lines) / 2
    for ln in lines:
        tw = sum(x[2] for x in ln) + sp * (len(ln) - 1)
        x = (W - tw) / 2
        for wd, hl, ww, ts in ln:
            # le mot s'allume quand il est prononcé
            on = 1.0 if t >= ts - 0.03 else 0.55
            col = GOLD if hl else WHITE
            d.text((x, y), wd, font=f, fill=col + (int(255 * k * on),), stroke_width=0)
            ds.text((x, y + 3), wd, font=f, fill=(0, 0, 0, int(230 * k)), stroke_width=7, stroke_fill=(0, 0, 0, int(200 * k)))
            x += ww + sp
        y += lh
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(lay)
    img.alpha_composite(sh, (0, CAP_Y - 150))

# ---------- composition ----------
def draw_area(fn, t, box_, a, full=False):
    """Dessine une scène suréchantillonnée dans la zone box_ et renvoie le calque (RGBA)."""
    x0, y0, x1, y1 = box_
    im = Image.new("RGBA", ((x1 - x0) * SS, (y1 - y0) * SS), (0, 0, 0, 0))
    if full:
        pp = P(ImageDraw.Draw(im), SS, ox=x0, oy=y0)
    else:
        pp = P(ImageDraw.Draw(im), SS, z=1.0, cx=480, cy=205, ts=1.28)
    fn(pp, t)
    im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    if a < 1:
        r, g, b, al = im.split()
        al = al.point(lambda v: int(v * a))
        im = Image.merge("RGBA", (r, g, b, al))
    return im

FULL_BOX = (0, 200, 1080, 1720)

def frame(t):
    """Renvoie (calque RGBA plein format ou None, liste de vitres [(rect, rayon, opacité, assombrissement)])."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frosts = []
    cov = full_cover(t)
    if cov > 0:
        frosts.append(((0, 0, W, H), 0, cov, 0.55))
    for a, b, fn in FULLS:
        if a - PRE - 0.05 <= t < b + PRE + 0.05:
            kc = env(t, a - 0.08, b + 0.25, 0.3, 0.25) if b < TOTAL else ease_io((t - (a - 0.08)) / 0.3)
            if kc > 0:
                x0, y0, x1, y1 = FULL_BOX
                lay = draw_area(fn, t, FULL_BOX, kc * cov, full=True)
                img.alpha_composite(lay, (x0, y0))
    for a, b, fn in CARDS:
        if a - 0.05 <= t < b + 0.05:
            kc = env(t, a, b, 0.3, 0.3)
            # la carte s'efface quand le plein écran la recouvre
            kc *= 1 - cov
            if kc > 0.003:
                frosts.append((CARD, 34, kc, 0.62))
                lay = draw_area(fn, t, CARD, kc)
                img.alpha_composite(lay, CARD[:2])
    draw_caption(img, t)
    # barre de progression fine en haut
    w = int(W * min(t / TOTAL, 1))
    if w > 1:
        ImageDraw.Draw(img).rectangle((0, 0, w, 5), fill=GOLD + (255,))
    return img, frosts

def _shift(p, y0):
    p.oy = y0
    return p
