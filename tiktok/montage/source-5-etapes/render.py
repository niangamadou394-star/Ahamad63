# Rendu final : lecture du rush HDR (HLG BT.2020, 1080x1920), découpe, léger zoom, vitres floutées,
# calque graphique converti en HLG, encodage x265 10 bits. Aucune conversion de couleur
# sur l'image filmée : on ne fait que recadrer et redimensionner les plans YUV.
import os, subprocess, sys
import numpy as np, cv2
from multiprocessing import Pool
import gfx
from words import SPANS, TOTAL_SPEECH

from edl import SRC
SW, SH = 1080, 1920
W, H = 1080, 1920
FPS = gfx.FPS
FACE = (510, 620)  # visage dans le rush (px) : on zoome autour de ce point
ZOOM_B = 1.08

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

def edit2src(t):
    for i in range(len(SPANS) - 1, -1, -1):
        if t >= STARTS[i] - 1e-9:
            s, e = SPANS[i]
            return min(s + t - STARTS[i], e - 0.5 / FPS), i
    return SPANS[0][0], 0

def crop_planes(Y, U, V, z):
    cw, ch = SW / z, SH / z
    x0 = FACE[0] * (1 - 1 / z); y0 = FACE[1] * (1 - 1 / z)
    x0, y0 = int(round(x0 / 2)) * 2, int(round(y0 / 2)) * 2
    cw, ch = int(round(cw / 2)) * 2, int(round(ch / 2)) * 2
    Yc = cv2.resize(Y[y0:y0 + ch, x0:x0 + cw], (W, H), interpolation=cv2.INTER_AREA)
    Uc = cv2.resize(U[y0 // 2:(y0 + ch) // 2, x0 // 2:(x0 + cw) // 2], (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    Vc = cv2.resize(V[y0 // 2:(y0 + ch) // 2, x0 // 2:(x0 + cw) // 2], (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    return Yc.astype(np.float32), Uc.astype(np.float32), Vc.astype(np.float32)

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

def compose(Y, U, V, ov, frosts):
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
        "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-s", f"{W}x{H}", "-r", "60", "-i", "-",
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
                res = nxt.get()
                if i + 1 < len(bs):
                    nxt = pool.map_async(overlay_job, range(bs[i + 1], min(N, bs[i + 1] + 24)), chunksize=2)
                yield from res
        for n, (ov, frosts) in enumerate(jobs()):
            te = n / FPS
            ts, si = edit2src(min(te, TOTAL_SPEECH - 0.5 / FPS))
            fi = int(round(ts * FPS))
            while cur_idx < fi:
                f = read_frame()
                if f is None: break
                cur, cur_idx = f, cur_idx + 1
            Yc, Uc, Vc = crop_planes(*cur, ZOOMS[si])
            enc.stdin.write(compose(Yc, Uc, Vc, ov, frosts))
    enc.stdin.close(); dec.kill()
    return enc.wait()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
