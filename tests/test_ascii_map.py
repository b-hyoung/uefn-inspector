"""ascii_map: pure text-map rendering, no project files needed."""
def test_ascii_map_places_symbols_and_legend():
    from uefn_inspector.analysis.spatial import ascii_map
    items = [("Device_PlayerSpawner_C", (0.0, 0.0, 0.0)),
             ("Device_PlayerSpawner_C", (100.0, 0.0, 0.0)),      # same cell as the first
             ("Device_GuardSpawner_C", (2000.0, 1000.0, 0.0)),
             ("GrayBox_Wall_C", (2000.0, 0.0, 0.0))]
    out = ascii_map(items, cell=500.0)
    assert out["legend"]["P"] == "Device_PlayerSpawner_C"
    assert out["legend"]["G"] == "Device_GuardSpawner_C"
    assert out["legend"]["W"] == "GrayBox_Wall_C"
    assert out["cell"] == 500.0 and out["bounds"] == ((0.0, 0.0, 0.0), (2000.0, 1000.0, 0.0))
    rows = out["map"].splitlines()
    assert rows[0].startswith("cell=500")
    body = rows[1:]
    assert len(body) == 3                                   # y 0..1000 / 500 -> 3 rows
    assert body[0].endswith("|2...W")                       # two spawners in one cell -> count
    assert body[2].endswith("|....G")


def test_ascii_map_disambiguates_same_initial_and_handles_empty():
    from uefn_inspector.analysis.spatial import ascii_map
    out = ascii_map([("Device_Alpha_C", (0, 0, 0)), ("Device_Beta_C", (500, 0, 0)),
                     ("Device_Ant_C", (1000, 0, 0))])
    assert set(out["legend"].values()) == {"Device_Alpha_C", "Device_Beta_C", "Device_Ant_C"}
    assert len(out["legend"]) == 3                          # A, B and N (second letter of Ant)
    assert ascii_map([])["map"] == "" and ascii_map([])["bounds"] is None


def test_ascii_map_mixed_cell_and_coarsening():
    from uefn_inspector.analysis.spatial import ascii_map
    out = ascii_map([("Device_A_C", (0, 0, 0)), ("Device_B_C", (10, 0, 0))], cell=500.0)
    assert out["map"].splitlines()[1].endswith("|*")        # mixed kinds in one cell
    wide = ascii_map([("Device_A_C", (0, 0, 0)), ("Device_A_C", (100000, 0, 0))], cell=500.0, max_cols=20)
    assert wide["cell"] > 500.0 and len(wide["map"].splitlines()[1].split("|")[1]) == 20
