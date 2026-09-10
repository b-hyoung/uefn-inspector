# verify_arenas.py — uefn-inspector 오프라인 분석으로 4개 아레나 구조검증
# 에디터 ON/OFF 무관 (디스크에 저장된 .uasset을 읽음)
import sys, json, math
from pathlib import Path

INSPECTOR = r"C:\Users\hunvr\Desktop\bobs_projects\uefn-inspector\src"
sys.path.insert(0, INSPECTOR)

LEVEL = Path(r"C:\Users\hunvr\Documents\Fortnite Projects\TestProject\Content\__ExternalActors__\TestProject")

from uefn_inspector.model.index import build_index
from uefn_inspector.level import inspect_actor, audit_level
from uefn_inspector.analysis import census as C
from uefn_inspector.analysis import spatial as S

# 아레나 정의 (build_arena_one.ps1과 동일)
ARENAS = {
    "A": dict(cx=-30000, cy=30000, half=2600, lure=False, sw=False),
    "B": dict(cx=0,      cy=30000, half=2600, lure=True,  sw=True),
    "C": dict(cx=30000,  cy=30000, half=2600, lure=True,  sw=True),
    "D": dict(cx=60000,  cy=30000, half=4200, lure=True,  sw=True),
}

def which_arena(x, y):
    for aid, a in ARENAS.items():
        if abs(x - a["cx"]) <= a["half"] + 600 and abs(y - a["cy"]) <= a["half"] + 600:
            return aid
    return None

print("=" * 66)
print("uefn-inspector 오프라인 구조검증 — Shadow Bait 4 아레나")
print("=" * 66)

# 1) 레벨 audit (중복·경고)
try:
    a = audit_level(str(LEVEL))
    print("\n[1] 레벨 audit")
    print(f"  액터 수: {a.get('actor_count')}")
    dups = a.get("duplicate_names") or a.get("duplicates") or []
    print(f"  중복 이름: {len(dups)}")
    for w in (a.get("warnings") or [])[:5]:
        print(f"  ⚠ {w}")
except Exception as e:
    print(f"[1] audit 실패: {e}")

# 2) 인덱스 + 액터별 좌표 → 아레나 귀속
idx = build_index(str(LEVEL))
print(f"\n[2] 패키지 인덱스: {len(idx.packages)}개")

rows = []
for p in idx.packages:
    fp = Path(p)
    try:
        act = inspect_actor(fp)
    except Exception:
        continue
    loc = getattr(act, "location", None)
    cls = getattr(act, "class_name", None) or getattr(act, "device_class", None) or "?"
    if loc is None:
        rows.append((cls, None, None, None))
        continue
    x, y, z = loc[0], loc[1], loc[2]
    rows.append((cls, x, y, which_arena(x, y)))

placed = [r for r in rows if r[1] is not None]
print(f"  좌표 디코드 성공: {len(placed)}/{len(rows)}")

# 3) 아레나별 구성 검증
print("\n[3] 아레나별 배치 (오프라인 좌표 기준)")
EXPECT = {
    "A": dict(light=6,  switch=0,  audio=0, guard=1, spawn=1),
    "B": dict(light=6,  switch=4,  audio=1, guard=1, spawn=1),
    "C": dict(light=10, switch=4,  audio=1, guard=1, spawn=1),
    "D": dict(light=4,  switch=4,  audio=1, guard=1, spawn=1),
}
def kind(cls):
    c = (cls or "").lower()
    if "pointlight" in c: return "light"
    if "switch" in c: return "switch"
    if "audioplayer" in c: return "audio"
    if "guardspawner" in c: return "guard"
    if "playerspawn" in c or "spawnpad" in c or "player_spawner" in c or "spawner_prop" in c: return "spawn"
    return None

summary = {aid: {} for aid in ARENAS}
outside = {}
for cls, x, y, aid in placed:
    k = kind(cls)
    if not k: continue
    if aid is None:
        outside[k] = outside.get(k, 0) + 1
    else:
        summary[aid][k] = summary[aid].get(k, 0) + 1

allok = True
for aid in ["A", "B", "C", "D"]:
    got = summary[aid]; exp = EXPECT[aid]
    parts, ok = [], True
    for k in ["light", "switch", "audio", "guard", "spawn"]:
        g, e = got.get(k, 0), exp[k]
        mark = "OK" if g == e else "MISMATCH"
        if g != e: ok = False; allok = False
        parts.append(f"{k} {g}/{e} {mark}")
    print(f"  [{aid}] " + " · ".join(parts))
if outside:
    print(f"  ※ 아레나 밖 잔여 디바이스: {outside}")

# 4) 공간 분석 (bounds/density/spacing)
print("\n[4] 공간 분석 (spatial)")
try:
    b = S.bounds(idx)
    print(f"  전체 bounds: {b}")
except Exception as e:
    print(f"  bounds 스킵: {e}")
try:
    d = S.min_spacing(idx)
    print(f"  최소 간격: {d}")
except Exception as e:
    print(f"  spacing 스킵: {e}")

# 5) 중복 배치 탐지
print("\n[5] 중복 배치 탐지")
try:
    dups = C.find_duplicates(idx)
    items = list(dups.items()) if hasattr(dups, "items") else list(dups)
    print(f"  중복 그룹: {len(items)}")
    for k, v in items[:6]:
        print(f"   - {k}: {v}")
except Exception as e:
    print(f"  스킵: {e}")

# 6) 타입 census
print("\n[6] 타입 census")
try:
    tc = C.type_census(idx)
    top = sorted(tc.items(), key=lambda kv: -kv[1])[:8] if hasattr(tc, "items") else []
    for k, v in top:
        print(f"   {k}: {v}")
except Exception as e:
    print(f"  스킵: {e}")

print("\n" + "=" * 66)
print("판정:", "모든 아레나 배치 = 스펙 일치 ✅" if allok else "불일치 있음 ⚠ (위 MISMATCH 확인)")
print("=" * 66)
