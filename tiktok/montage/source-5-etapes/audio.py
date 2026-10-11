# Audio : on assemble les morceaux gardés puis on rend la voix plus claire.
import subprocess, sys, json
from edl import spans
from edl import SRC
from gfx import HOLD
sp = spans(); out = sys.argv[1]
fc = []
for i, (s, e) in enumerate(sp):
    d = e - s
    fc.append(f"[0:a]atrim={s:.5f}:{e:.5f},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={d-0.008:.5f}:d=0.008[a{i}]")
fc.append("".join(f"[a{i}]" for i in range(len(sp))) + f"concat=n={len(sp)}:v=0:a=1[c]")
VOICE = ("highpass=f=85,afftdn=nr=8:nf=-50:tn=1,"
         "equalizer=f=220:t=q:w=1.0:g=-2.5,equalizer=f=3200:t=q:w=0.9:g=3.5,equalizer=f=9000:t=h:w=0.7:g=1.5,"
         "acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=2,"
         "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,pan=stereo|c0=c0|c1=c0,apad=pad_dur=" + f"{HOLD + 0.4}")
fc.append(f"[c]{VOICE}[out]" if "--raw" not in sys.argv else "[c]anull[out]")
subprocess.run(["ffmpeg","-v","error","-y","-i",SRC,"-filter_complex",";".join(fc),"-map","[out]","-ar","48000",out],check=True)
