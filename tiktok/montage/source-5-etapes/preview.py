# Planche d'aperçu rapide : pour chaque temps (montage), compose l'image HLG comme le rendu
# puis la convertit en SDR uniquement pour l'affichage.
import sys, subprocess, numpy as np
from PIL import Image
import render, gfx
TM = "zscale=t=linear:npl=203:p=bt709:tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=limited,format=gbrpf32le,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=pc,format=rgb24"
def still(te):
    ts, si = render.edit2src(min(te, render.TOTAL_SPEECH - 0.5 / render.FPS))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ts:.3f}", "-i", render.SRC, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint16); SW, SH = render.SW, render.SH
    Y, U, V = a[:SW * SH].reshape(SH, SW), a[SW * SH:SW * SH * 5 // 4].reshape(SH // 2, SW // 2), a[SW * SH * 5 // 4:].reshape(SH // 2, SW // 2)
    ov, frosts = render.overlay_job(int(round(te * render.FPS)))
    buf = render.compose(*render.crop_planes(Y, U, V, render.ZOOMS[si]), ov, frosts)
    rgb = subprocess.run(["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "yuv420p10le", "-s", "1080x1920", "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-i", "-",
                          "-vf", TM, "-f", "rawvideo", "-"], input=buf, capture_output=True).stdout
    return Image.frombytes("RGB", (1080, 1920), rgb)
if __name__ == "__main__":
    ts = [float(x) for x in sys.argv[2:]]
    cols = 6; rows = (len(ts) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 360, rows * 640))
    for i, t in enumerate(ts):
        sheet.paste(still(t).resize((360, 640)), ((i % cols) * 360, (i // cols) * 640))
    sheet.save(sys.argv[1], quality=85)
