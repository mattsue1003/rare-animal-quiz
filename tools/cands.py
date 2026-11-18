# 找每種動物的額外照片候選：Commons 搜尋、篩授權與尺寸，下載小圖並做對照表
# 用法: python3 tools/cands.py fl.tsv outdir
import json, sys, re, subprocess, html, os, time, urllib.parse
UA = "RareAnimalQuizBuilder/1.0 (educational teaching page; https://mattsue1003.github.io/)"
OK = re.compile(r"^(CC BY(-SA)? [0-9.]+|CC0|Public domain|PD.*)$", re.I)
BAD = re.compile(r"skull|skelet|bone|museum|taxiderm|specimen|mounted|stuffed|herbar|illustr|drawing|plate|_map|range_map|distribution|stamp|coin|logo|diagram|\.svg|\.tif|sketch|painting|statue|sculpture|toy|plush|fossil|track|footprint|scat|dung|poster|banknote|cartoon", re.I)
EXTRA = {  # 額外搜尋字（全株、樹、花海等）
 "default": ["", " tree", " plant"],
}
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="utf-8")]
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
res = {}
for key, name, sci, cur, en in rows:
    s = re.split(r"[（(]", sci)[0].replace(" spp.", "").replace("×", "").replace("hybrids", "").strip()
    s = " ".join(re.sub(r"\s+", " ", s).split()[:2])
    seen = {urllib.parse.unquote(cur).replace(" ", "_")}
    picks = []
    for q in [s, en, s + " zoo"]:
        args = ["curl", "-s", "-A", UA, "-G", "https://commons.wikimedia.org/w/api.php",
                "--data-urlencode", "gsrsearch=" + q + " filetype:bitmap",
                "-d", "action=query", "-d", "generator=search", "-d", "gsrnamespace=6", "-d", "gsrlimit=30",
                "-d", "prop=imageinfo", "-d", "iiprop=url|extmetadata|size", "-d", "iiurlwidth=1000", "-d", "format=json"]
        for t in range(3):
            r = subprocess.run(args, capture_output=True, text=True).stdout
            try:
                d = json.loads(r); break
            except Exception:
                time.sleep(5); d = {}
        for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
            ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
            g = lambda k: re.sub("<[^>]+>", "", html.unescape(m.get(k, {}).get("value", ""))).strip()
            fn = p["title"][5:].replace(" ", "_")
            if fn in seen or BAD.search(fn): continue
            if not fn.lower().endswith((".jpg", ".jpeg")): continue
            if ii["width"] < 900 or ii["height"] < 600: continue
            lic = g("LicenseShortName")
            if not OK.match(lic): continue
            seen.add(fn)
            picks.append(dict(file=fn, thumb=ii["thumburl"], w=ii["width"], h=ii["height"], author=g("Artist")[:60] or "Unknown",
                              lic=lic, licurl=m.get("LicenseUrl", {}).get("value", ""), page=ii["descriptionurl"]))
        time.sleep(1)
        if len(picks) >= 12: break
    res[key] = picks[:12]
    print(key, len(res[key]), flush=True)
json.dump(res, open(os.path.join(out, "cands.json"), "w"), ensure_ascii=False, indent=1)
