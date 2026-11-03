# Rush vertical 1080p : redressé (rotation automatique) puis fenêtre 1080x1440 autour de lui, sans mise à l'échelle.
# Colle les segments des deux rushes dans un fichier intermédiaire sans perte (FFV1 10 bits,
# HLG conservé tel quel, son PCM) : c'est le SRC du reste du pipeline.
# Images recalées sur N/FPS (le rush est à fréquence variable : sans ça le son glissait de ~0,03 s à chaque segment).
# Un segment à la fois (un seul filtre concat sur deux rushes saturait la mémoire).
import os, subprocess, sys
from edl import CUTS_SRC, RUSH, SRC, FPS, CROP
tmp = os.path.dirname(SRC)
parts = []
for i, (k, a, b, off) in enumerate(CUTS_SRC):
    n = int(round((b - a) * FPS))
    out = os.path.join(tmp, f"seg{i}.mkv")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.5f}", "-i", RUSH[k], "-map", "0:v:0", "-map", "0:a:0", "-vf", "crop=1080:1440:%d:%d,setpts=N/%g/TB" % (CROP[k] + (FPS,)), "-r", f"{FPS:g}",
                    "-frames:v", str(n), "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p10le",
                    "-c:a", "pcm_s24le", "-ar", "48000", "-af", f"pan=mono|c0=c0,apad,atrim=end={n / FPS:.5f}", out], check=True)
    got = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip().strip(","))
    print(i, k, f"{a:.3f}", n, got, flush=True)
    parts.append(out)
lst = os.path.join(tmp, "segs.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", SRC]).returncode
for p in parts: os.remove(p)
sys.exit(r)
