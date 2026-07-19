"""Brightness curve of the Christ region of GE Merry Christmas in the preview."""
import subprocess
import numpy as np

VID = "/Users/elliott.ohara/xlights/RenderCompare/holy_forever_christ_glow.mp4"
CROP = "crop=160:60:490:330"

expected = [(40.95, 44.675), (45.3, 48.125), (48.25, 51.75), (61.45, 64.9)]
for t in np.arange(40.0, 66.51, 0.5):
    out = subprocess.run(
        ["ffmpeg", "-ss", f"{t}", "-i", VID, "-frames:v", "1",
         "-vf", f"{CROP},signalstats,metadata=print", "-f", "null", "-"],
        capture_output=True, text=True)
    yavg = 0.0
    for line in out.stderr.splitlines():
        if "YAVG" in line:
            yavg = float(line.split("=")[-1])
    inwin = any(a <= t <= b for a, b in expected)
    print(f"{t:6.2f} {yavg:6.1f} {'#' * int(yavg * 2)}{'   <window>' if inwin else ''}")
