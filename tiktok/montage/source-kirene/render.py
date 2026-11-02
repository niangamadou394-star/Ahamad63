# Rendu final : lecture du fichier combiné (segments d'IMG_2669 (Kirène), fenêtre 1080x1440 du rush vertical 1080p (HLG 10 bits), découpe, recadrage, vitres floutées,
# calque graphique converti en HLG, encodage x265 10 bits. Aucune conversion de couleur
# sur l'image filmée : on ne fait que recadrer et redimensionner les plans YUV.
import os, subprocess, sys
import numpy as np, cv2
from multiprocessing import Pool
import gfx
from words import SPANS, TOTAL_SPEECH

from edl import SRC, CUTS_SRC, seg_at
SW, SH = 1080, 1440
W, H = 1080, 1920
FPS = gfx.FPS
# visage dans la fenêtre 1080x1440 (px) : on zoome autour de ce point (le visage reste affiché vers y = 480 + 440).
# Téléphone un peu plus proche que pour Wari : zoom 1,15 pour garder la même taille de visage (cadrage large qu'il préfère).
FACE = {"A": (540, 400)}
BASE = {"A": 1.5}
ZOOM_B = 1.10

# ---------- conversion sRGB -> HLG BT.2020 (blanc graphique = 75 % HLG, BT.2408) ----------
M709_2020 = np.array([[0.6274, 0.3293, 0.0433], [0.0691, 0.9195, 0.0114], [0.0164, 0.0880, 0.8956]], np.float32)
def to_hlg_yuva(rgba):
    rgb = rgba[..., :3].astype(np.float32) / 255
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    lin = lin @ M709_2020.T
    fd = np.clip(lin * (203 / 1000), 0, 1)
    yd = fd @ np.array([0.2627, 0.6780, 0.0593], np.float32)
    e = fd * (np.maximum(yd, 1e-6) ** (-1 / 6))[..., None]
    a, b, c = 0.17883277, 0.28466892, 0.55991073
    ep = np.where(e <= 1 / 12, np.sqrt(3 * np.clip(e, 0, None)), a * np.log(np.maximum(12 * e - b, 1e-6)) + c)
    R, G, B = ep[..., 0], ep[..., 1], ep[..., 2]
    Y = 0.2627 * R + 0.6780 * G + 0.0593 * B
    return 64 + 876 * Y, 512 + 896 * (B - Y) / 1.8814, 512 + 896 * (R - Y) / 1.4746, rgba[..., 3].astype(np.float32) / 255

def overlay_job(n):
    t = n / FPS
    img, frosts = gfx.frame(t)
    arr = np.asarray(img)
    al = arr[..., 3]
    rows = np.where(al.any(axis=1))[0]
    if not len(rows):
        return None, frosts
    r0, r1 = rows[0] // 2 * 2, (rows[-1] + 2) // 2 * 2
    cols = np.where(al[r0:r1].any(axis=0))[0]
    c0, c1 = cols[0] // 2 * 2, (cols[-1] + 2) // 2 * 2
    y, u, v, a = to_hlg_yuva(arr[r0:r1, c0:c1])
    # chroma 4:2:0 prémultipliée
    def sub(x):
        return x.reshape(x.shape[0] // 2, 2, x.shape[1] // 2, 2).mean(axis=(1, 3))
    a2 = sub(a)
    return (r0, c0, (y * a).astype(np.float32), a.astype(np.float32), sub(u * a).astype(np.float32), sub(v * a).astype(np.float32), a2.astype(np.float32)), frosts

# ---------- montage ----------
STARTS = []
acc = 0
for s, e in SPANS:
    STARTS.append(acc); acc += e - s
# zoom alterné à chaque coupe visible (les coupes cachées sous un plein écran ne comptent pas)
ZOOMS = [1.0]
for c in gfx.CUTS:
    ZOOMS.append(ZOOMS[-1] if gfx.full_cover(c) > 0.5 else (ZOOM_B if ZOOMS[-1] == 1.0 else 1.0))

RUSHK = [CUTS_SRC[seg_at((s + e) / 2)][0] for s, e in SPANS]   # rush de chaque plan

def edit2src(t):
    for i in range(len(SPANS) - 1, -1, -1):
        if t >= STARTS[i] - 1e-9:
            s, e = SPANS[i]
            return min(s + t - STARTS[i], e - 0.5 / FPS), i
    return SPANS[0][0], 0

# mise en page : le rush horizontal est réduit (pas de recadrage serré) et posé en bas de l'écran,
# au-dessus le mur du décor est prolongé en flou pour laisser la place aux illustrations.
VID_Y = 480                      # haut de la zone vidéo nette
SCALE = (H - VID_Y) / SH         # 1440 / 2158
X0 = {k: FACE[k][0] - W / SCALE / 2 for k in FACE}   # fenêtre source (largeur W / SCALE) centrée sur lui
STRIP = 48                       # rangées de mur utilisées pour prolonger le décor vers le haut
FEATHER = 150
_ramp = None
def _resize(P, x0, y0, w, h, ow, oh):
    return cv2.resize(P[y0:y0 + h, x0:x0 + w], (ow, oh), interpolation=cv2.INTER_AREA).astype(np.float32)

def crop_planes(Y, U, V, z, k):
    global _ramp
    if _ramp is None:
        r = np.clip((np.arange(H) - VID_Y) / FEATHER, 0, 1)
        _ramp = (r * r * (3 - 2 * r)).astype(np.float32)[:, None]
    ww, hh = W / SCALE / z, (H - VID_Y) / SCALE / z
    z *= BASE[k]
    ww, hh = W / SCALE / z, (H - VID_Y) / SCALE / z
    x0 = FACE[k][0] - (FACE[k][0] - X0[k]) / z
    y0 = FACE[k][1] * (1 - 1 / z)
    x0, y0 = int(round(x0 / 2)) * 2, int(round(y0 / 2)) * 2
    ww, hh = int(round(ww / 2)) * 2, int(round(hh / 2)) * 2
    st = int(round(STRIP / z / 2)) * 2
    out = []
    for P, f, base in ((Y, 1, 64), (U, 2, 512), (V, 2, 512)):
        oh, ow, vy = H // f, W // f, VID_Y // f
        vid = _resize(P, x0 // f, y0 // f, ww // f, hh // f, ow, oh - vy)
        top = _resize(P, x0 // f, y0 // f, ww // f, st // f, ow // 8, (vy + FEATHER // f) // 8)
        top = cv2.GaussianBlur(top, (0, 0), 6)
        top = cv2.resize(top, (ow, vy + FEATHER // f), interpolation=cv2.INTER_CUBIC)
        full = np.empty((oh, ow), np.float32)
        full[vy:] = vid
        full[:vy] = top[:vy]
        rm = _ramp[::f][vy:vy + FEATHER // f]
        full[vy:vy + FEATHER // f] = top[vy:] * (1 - rm) + vid[:FEATHER // f] * rm
        out.append(full)
    return out

def blurred(P, f):
    h, w = P.shape
    s = cv2.resize(P, (w // f, h // f), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), 3.2)
    return cv2.resize(s, (w, h), interpolation=cv2.INTER_LINEAR)

_masks = {}
def rmask(rect, r):
    k = (rect, r)
    if k not in _masks:
        x0, y0, x1, y1 = rect
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        if r:
            cv2.rectangle(m, (r, 0), (x1 - x0 - 1 - r, y1 - y0 - 1), 255, -1)
            cv2.rectangle(m, (0, r), (x1 - x0 - 1, y1 - y0 - 1 - r), 255, -1)
            for cx, cy in [(r, r), (x1 - x0 - 1 - r, r), (r, y1 - y0 - 1 - r), (x1 - x0 - 1 - r, y1 - y0 - 1 - r)]:
                cv2.circle(m, (cx, cy), r, 255, -1, lineType=cv2.LINE_AA)
        else:
            m[:] = 255
        _masks[k] = m.astype(np.float32) / 255
    return _masks[k]

# spotlight (demandé) : la lumière reste sur lui, les bords de l'image s'assombrissent doucement.
SPOT_C, SPOT_R = (540, 1150), (600, 820)
_spot = {}
def spot_masks():
    if not _spot:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - SPOT_C[0]) / SPOT_R[0]) ** 2 + ((yy - SPOT_C[1]) / SPOT_R[1]) ** 2)
        k = np.clip((d - 0.55) / 0.7, 0, 1)
        m = 1 - 0.5 * k * k * (3 - 2 * k)
        _spot["y"] = m.astype(np.float32)
        _spot["c"] = m[::2, ::2].copy()
    return _spot["y"], _spot["c"]

def compose(Y, U, V, ov, frosts):
    my, mc = spot_masks()
    Y = 64 + (Y - 64) * my
    U = 512 + (U - 512) * mc
    V = 512 + (V - 512) * mc
    if frosts:
        Yb, Ub, Vb = blurred(Y, 8), blurred(U, 4), blurred(V, 4)
        for rect, r, a, dark in frosts:
            x0, y0, x1, y1 = rect
            m = rmask(rect, r) * a
            m2 = m[::2, ::2]
            yb = 64 + (Yb[y0:y1, x0:x1] - 64) * (1 - dark)
            Y[y0:y1, x0:x1] += (yb - Y[y0:y1, x0:x1]) * m
            for P, Pb in ((U, Ub), (V, Vb)):
                cb = 512 + (Pb[y0 // 2:y1 // 2, x0 // 2:x1 // 2] - 512) * (1 - dark * 0.5)
                P[y0 // 2:y1 // 2, x0 // 2:x1 // 2] += (cb - P[y0 // 2:y1 // 2, x0 // 2:x1 // 2]) * m2
    if ov:
        r0, c0, ya, a, ua, va, a2 = ov
        h, w = a.shape
        Y[r0:r0 + h, c0:c0 + w] = Y[r0:r0 + h, c0:c0 + w] * (1 - a) + ya
        U[r0 // 2:r0 // 2 + h // 2, c0 // 2:c0 // 2 + w // 2] = U[r0 // 2:r0 // 2 + h // 2, c0 // 2:c0 // 2 + w // 2] * (1 - a2) + ua
        V[r0 // 2:r0 // 2 + h // 2, c0 // 2:c0 // 2 + w // 2] = V[r0 // 2:r0 // 2 + h // 2, c0 // 2:c0 // 2 + w // 2] * (1 - a2) + va
    return b"".join(np.clip(np.round(P), 0, 1023).astype(np.uint16).tobytes() for P in (Y, U, V))

def main(out, audio, limit=None):
    N = int(round(gfx.TOTAL * FPS))
    if limit: N = min(N, int(limit))
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-map", "0:v:0", "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-"],
                           stdout=subprocess.PIPE, bufsize=SW * SH * 3)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-stats", "-y",
        "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-s", f"{W}x{H}", "-r", str(int(FPS)), "-i", "-",
        "-i", audio, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx265", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1",
        "-x265-params", "log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:repeat-headers=1",
        "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv",
        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    fsz = SW * SH * 2
    cur_idx, cur = -1, None
    def read_frame():
        buf = dec.stdout.read(fsz * 3 // 2)
        if len(buf) < fsz * 3 // 2:
            return None
        a = np.frombuffer(buf, np.uint16)
        return a[:SW * SH].reshape(SH, SW), a[SW * SH:SW * SH * 5 // 4].reshape(SH // 2, SW // 2), a[SW * SH * 5 // 4:].reshape(SH // 2, SW // 2)
    with Pool(3) as pool:
        def jobs():  # par lots, pour ne pas accumuler les calques en mémoire
            bs = list(range(0, N, 24))
            nxt = pool.map_async(overlay_job, range(0, min(N, 24)), chunksize=2)
            for i, b0 in enumerate(bs):
                cur_res = nxt.get()
                if i + 1 < len(bs):
                    nxt = pool.map_async(overlay_job, range(bs[i + 1], min(N, bs[i + 1] + 24)), chunksize=2)
                yield from cur_res
        for n, (ov, frosts) in enumerate(jobs()):
            te = n / FPS
            ts, si = edit2src(min(te, TOTAL_SPEECH - 0.5 / FPS))
            fi = int(round(ts * FPS))
            while cur_idx < fi:
                f = read_frame()
                if f is None: break
                cur, cur_idx = f, cur_idx + 1
            Yc, Uc, Vc = crop_planes(*cur, ZOOMS[si] * gfx.punch(te), RUSHK[si])
            enc.stdin.write(compose(Yc, Uc, Vc, ov, frosts))
    enc.stdin.close(); dec.kill()
    return enc.wait()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
