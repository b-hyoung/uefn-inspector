"""design_lint on synthetic Level objects — no project files needed."""
from uefn_inspector.analysis.design_lint import DEFAULT_PROFILE, design_lint
from uefn_inspector.level import Level, PlacedActor

CUBE = "/Game/Creative/Devices/Destruction_Object/Meshes/S_Cube"
PROPS = "/Game/Playgrounds/Items/Props"


def _a(cls, loc, refs=(), scale=None, rot=None, name=""):
    return PlacedActor(cls, name or cls, loc, list(refs), scale, rot)


def _by_id(out):
    return {c["id"]: c for c in out["checks"]}


def test_flat_greybox_grid_fails_the_design_checks():
    """The failure mode we want caught: untextured cubes on one plane, axis-aligned."""
    actors = [_a("GrayBox_Solid_Wall_C", (x * 500.0, y * 500.0, 0.0), [CUBE],
                 scale=(5.0, 0.2, 3.0), rot=(0.0, 0.0, 90.0 * ((x + y) % 4)))
              for x in range(6) for y in range(4)]
    actors.append(_a("Device_PlayerSpawner_C", (0.0, 0.0, 0.0)))
    out = design_lint(Level(name="grey", actors=actors))
    c = _by_id(out)
    assert c["graybox_share"]["status"] == "fail"
    assert c["mesh_variety"]["status"] == "fail" and c["material_variety"]["status"] == "fail"
    assert c["gallery_sources"]["status"] == "fail"           # nothing pulled in
    assert c["verticality"]["status"] == "fail"               # one height band
    assert c["flat_props"]["status"] == "fail"                # thin walls everywhere
    assert c["rotation_variety"]["status"] == "fail"          # all multiples of 90
    assert c["lighting"]["status"] == "fail"
    assert c["function_elements"]["status"] == "ok"           # spawner present
    assert set(out["fail"]) >= {"graybox_share", "verticality", "gallery_sources"}


def test_dressed_level_with_gallery_props_and_height_passes():
    actors = []
    props = ["SM_RoadCase", "SM_Speaker", "SM_Scaffold", "SM_Barrel", "SM_Crate",
             "SM_Cable", "SM_Spotlight", "SM_Truss", "SM_Fence"]
    mats = ["M_Metal", "MI_Wood", "M_Rubber", "MI_Paint_Red", "M_Concrete", "MI_Glow"]
    for i in range(30):
        prop, mat = props[i % len(props)], mats[i % len(mats)]
        actors.append(_a("StaticMeshActor", ((i % 6) * 800.0, (i // 6) * 800.0, (i % 3) * 250.0),
                         [f"{PROPS}/{prop}", f"/Game/Playgrounds/Materials/{mat}"],
                         scale=(1.0, 1.0, 1.0), rot=(0.0, 17.0 * i, 0.0)))   # (pitch, yaw, roll)
    actors += [_a("Device_PlayerSpawner_C", (0.0, 0.0, 0.0)),
               _a("Device_PointLight_V2_C", (1000.0, 1000.0, 300.0))]
    out = design_lint(Level(name="dressed", actors=actors))
    c = _by_id(out)
    assert out["fail"] == [], out["fail"]
    assert c["gallery_sources"]["value"] >= 1 and PROPS.startswith(c["gallery_sources"]["evidence"][:20])
    assert c["verticality"]["value"]["bands"] >= 2
    assert c["dominant_mesh"]["status"] == "ok"


def test_missing_transform_data_reports_unverified_not_fail():
    actors = [_a("Device_PlayerSpawner_C", None), _a("Device_PointLight_V2_C", None)]
    out = design_lint(Level(name="x", actors=actors))
    c = _by_id(out)
    assert c["verticality"]["status"] == "unverified"
    assert c["flat_props"]["status"] == "unverified"
    assert c["rotation_variety"]["status"] == "unverified"
    assert "verticality" in out["unverified"] and "verticality" not in out["fail"]


def test_player_start_counts_as_spawn_and_yaw_is_index_1():
    """Measured on the UEFN 심플 template: FortPlayerStartCreative is the spawn, and
    turned props decode as (pitch=0, yaw=30, roll=0)."""
    actors = [_a("FortPlayerStartCreative", (0, 0, 0)), _a("Device_PointLight_V2_C", (0, 0, 400)),
              _a("StaticMeshActor", (500, 0, 0), rot=(0.0, 30.0, 0.0)),
              _a("StaticMeshActor", (1000, 0, 0), rot=(0.0, 90.0, 0.0))]
    c = _by_id(design_lint(Level(name="t", actors=actors)))
    assert c["function_elements"]["status"] == "ok"
    assert c["rotation_variety"]["value"] == 0.5          # one of two rotations is off-grid


def test_profile_overrides_thresholds_and_required_classes():
    actors = [_a("Device_GoalZone_C", (0, 0, 0)), _a("Device_PointLight_V2_C", (0, 0, 500))]
    strict = design_lint(Level(name="p", actors=actors),
                         profile={"required_class_substrings": ["Spawn", "Goal"], "graybox_share_max": 0.0})
    c = _by_id(strict)
    assert c["function_elements"]["status"] == "fail" and "Spawn" in c["function_elements"]["evidence"]
    assert "Goal" not in c["function_elements"]["evidence"]   # Goal present, only Spawn missing
    assert strict["profile"]["graybox_share_max"] == 0.0 and DEFAULT_PROFILE["graybox_share_max"] == 0.20


def test_empty_level():
    out = design_lint(Level(name="e", actors=[]))
    assert out["summary"] == "no actors" and out["checks"] == []
