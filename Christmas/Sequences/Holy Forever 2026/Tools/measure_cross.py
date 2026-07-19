"""Brightness curve of the cross region in the exported preview video."""
import subprocess
import numpy as np

VID = "/Users/elliott.ohara/xlights/RenderCompare/holy_forever_cross_intro.mp4"
# cross region in preview frame (found by inspecting c_5.0.jpg zoom)
CROP = "crop=30:45:325:160"

for t in np.arange(3.0, 15.51, 0.25):
    out = subprocess.run(
        ["ffmpeg", "-ss", f"{t}", "-i", VID, "-frames:v", "1",
         "-vf", f"{CROP},signalstats,metadata=print", "-f", "null", "-"],
        capture_output=True, text=True)
    yavg = 0.0
    for line in out.stderr.splitlines():
        if "YAVG" in line:
            yavg = float(line.split("=")[-1])
    print(f"{t:6.2f} {yavg:6.1f} {'#' * int(yavg)}")
