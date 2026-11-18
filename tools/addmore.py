# 依挑選結果下載額外照片（每種動物 2 張）並寫入 data/media.js 的 more 欄位
import json, sys, os, subprocess, re
UA = "RareAnimalQuizBuilder/1.0 (educational teaching page; https://mattsue1003.github.io/)"
PICK = dict(pangolin=[6,7], leopardcat=[5,4], otter=[9,2], blackbear=[1,9], mongoose=[5,6], anteater=[11,2],
 ayeaye=[0,7], sloth=[0,9], platypus=[3,10], glider=[2,6], fennec=[4,2], okapi=[2,6],
 capybara=[1,11], redpanda=[3,5], snowleopard=[4,1], shoebill=[0,10], axolotl=[4,6], tapir=[3,5], proboscis=[3,7], dugong=[2,3],
 civet=[1,6], sambar=[8,0], serow=[5,3], marten=[0,2], greenturtle=[0,10], flyingsquirrel=[0,6], sunfish=[11,6], aardvark=[1,10],
 starmole=[5,9], armadillo=[0,9], loris=[5,6], tarsier=[6,4], fossa=[7,9], manedwolf=[5,7], devil=[9,11], kakapo=[4,2],
 babirusa=[1,6], saiga=[8,3], iguana=[11,3], pygmyhippo=[2,11])
c = json.load(open(sys.argv[1]))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, "data/media.js"), encoding="utf-8").read()
head, body = src.split("window.MEDIA=", 1)
mjson, rest = body.split("\n};", 1)
M = json.loads(mjson + "\n}")
for k, idx in PICK.items():
    more = []
    for n, i in enumerate(idx, start=2):
        p = c[k][i]; f = os.path.join(root, f"assets/img/{k}-{n}.jpg")
        if not os.path.exists(f) or os.path.getsize(f) < 5000:
            subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", f, p["thumb"]], check=True)
        more.append(dict(author=p["author"], lic=p["lic"], licurl=p["licurl"], page=p["page"]))
    M[k]["more"] = more
open(os.path.join(root, "data/media.js"), "w", encoding="utf-8").write(head + "window.MEDIA=" + json.dumps(M, ensure_ascii=False, indent=1) + ";" + rest.lstrip(";"))
print("done", len(PICK))
