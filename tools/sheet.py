# 把候選圖做成編號對照表（每張 4 種花 × 12 張）
import json, sys, os, subprocess, io
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
UA = "RareAnimalQuizBuilder/1.0 (educational teaching page; https://mattsue1003.github.io/)"
d = sys.argv[1]; c = json.load(open(os.path.join(d, "cands.json")))
names = dict(l.split("\t")[:2] for l in open(sys.argv[2], encoding="utf-8"))
th = os.path.join(d, "th"); os.makedirs(th, exist_ok=True)
jobs = []
for k, L in c.items():
    for i, p in enumerate(L):
        jobs.append((os.path.join(th, f"{k}_{i}.jpg"), p["thumb"].replace("/1000px-", "/240px-")))
def get(j):
    f, u = j
    if not os.path.exists(f) or os.path.getsize(f) < 1000:
        subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", f, u])
with ThreadPoolExecutor(6) as ex: list(ex.map(get, jobs))
font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 22)
keys = list(c); W, H = 160, 120
for s in range(0, len(keys), 4):
    ks = keys[s:s+4]
    im = Image.new("RGB", (12*W + 110, len(ks)*(H+8)), "white"); dr = ImageDraw.Draw(im)
    for r, k in enumerate(ks):
        y = r*(H+8); dr.text((4, y+40), names[k], fill="black", font=font)
        for i in range(len(c[k])):
            try:
                t = Image.open(os.path.join(th, f"{k}_{i}.jpg")).convert("RGB"); t.thumbnail((W-4, H-4))
                im.paste(t, (110 + i*W, y))
            except Exception: pass
            dr.rectangle([110+i*W, y, 110+i*W+24, y+22], fill="black"); dr.text((114+i*W, y-1), str(i), fill="yellow", font=font)
    im.save(os.path.join(d, f"sheet{s//4}.jpg"), quality=80)
print("ok")
