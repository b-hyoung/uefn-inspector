# find_dupes.py — 아레나 범위 안에서 arena_*.json에 없는 잔여(중복) 액터 이름 산출
import sys, json
from pathlib import Path
sys.path.insert(0, r"C:\Users\hunvr\Desktop\bobs_projects\uefn-inspector\src")
LEVEL = Path(r"C:\Users\hunvr\Documents\Fortnite Projects\TestProject\Content\__ExternalActors__\TestProject")
STATE = Path(r"C:\Users\hunvr\Desktop\bobs_projects\shadow-bait\state")

from uefn_inspector.model.index import build_index
from uefn_inspector.level import inspect_actor

ARENAS = {"A": (0,20000,1500), "B": (20000,20000,1500), "C": (40000,20000,1500), "D": (60000,20000,2500)}

keep = set()
for aid in "ABCD":
    for it in json.loads((STATE / f"arena_{aid}.json").read_text(encoding="utf-8-sig")):
        keep.add(it["ref"].split(".")[-1])

def which(x, y):
    for aid,(cx,cy,h) in ARENAS.items():
        if abs(x-cx) <= h+600 and abs(y-cy) <= h+600: return aid
    return None

idx = build_index(str(LEVEL))
out = []
for p in idx.packages:
    try: act = inspect_actor(Path(p))
    except Exception: continue
    name = getattr(act, "name", None) or getattr(act, "actor_name", None) or Path(p).stem
    cls  = getattr(act, "class_name", None) or "?"
    loc  = getattr(act, "location", None)
    if loc is None: continue
    aid = which(loc[0], loc[1])
    if aid is None: continue
    if name in keep: continue
    out.append({"arena": aid, "name": name, "class": cls, "x": loc[0], "y": loc[1]})

print(json.dumps(out, ensure_ascii=False, indent=1))
print(f"\nTOTAL STRAY IN ARENAS: {len(out)}")
(STATE / "strays.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
