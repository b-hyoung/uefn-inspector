using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/SpatialMath }

# ?? Shadow Bait - ?? ?? ??
# ???? ??? ??. ??(????)? ??(??)? ??
# ??? ?? ?? ?? 3?? ???? ???? ??.
# ??? ??? ??? ??. ?? ???? GUI ??? ?? ??.

GM_ROUND_SEC   : float = 180.0   # ??? ????
GM_GOAL_COUNT  : int   = 3       # ???? ? ?? ?
GM_TOUCH_R     : float = 260.0   # ?? ?? ??
GM_TICK        : float = 0.25

gm_arena := class<final>:
    Name : string
    X    : float
    Y    : float
    Half : float

GM_GetArenas():[]gm_arena =
    array:
        gm_arena{ Name := "A(teal)",   X := -30000.0, Y := 30000.0, Half := 2600.0 }
        gm_arena{ Name := "B(purple)", X :=      0.0, Y := 30000.0, Half := 2600.0 }
        gm_arena{ Name := "C(red)",    X :=  30000.0, Y := 30000.0, Half := 2600.0 }
        gm_arena{ Name := "D(blue)",   X :=  60000.0, Y := 30000.0, Half := 4200.0 }

# ??? ?? ?? ?? 3?(?? ?? ???? ??)
GM_GoalOffsets():[]tuple(float, float) =
    array:
        (0.62, 0.62)
        (-0.68, 0.55)
        (0.55, -0.70)

shadow_bait_game := class(creative_device):

    @editable var GuardSpawner : guard_spawner_device = guard_spawner_device{}
    @editable var DecoyAudio : audio_player_device = audio_player_device{}

    OnBegin<override>()<suspends>:void=
        Print("[GAME] Shadow Bait - round start")
        loop:
            RunRound()
            Print("[GAME] ?? ????? 5?")
            Sleep(5.0)

    RunRound()<suspends>:void=
        Arenas := GM_GetArenas()
        Goals := GM_GoalOffsets()
        var Elapsed : float = 0.0
        var GoalIdx : int = 0
        var Ended : logic = false
        var Result : string = "none"
        var Announced : int = -1

        Print("[GAME] ROUND START - ?? {GM_GOAL_COUNT}?? ????. ?? {GM_ROUND_SEC}?")

        loop:
            if (Ended?) { break }
            Sleep(GM_TICK)
            set Elapsed = Elapsed + GM_TICK

            # ?? ?? = ??
            if (Elapsed >= GM_ROUND_SEC):
                set Result = "TIMEOUT"
                set Ended = true

            if (not Ended?):
                Players := GetPlayspace().GetPlayers()
                for (P : Players):
                    if (C := P.GetFortCharacter[]):
                        # ?? ?? = ??
                        if (C.GetHealth() <= 0.0):
                            set Result = "CAUGHT"
                            set Ended = true
                        Pos := C.GetTransform().Translation
                        # ?? ??? ??
                        if (A := GM_ArenaAt[Arenas, Pos]):
                            # ?? ?? ??
                            if (Off := Goals[GoalIdx]):
                                GX := A.X + Off(0) * A.Half
                                GY := A.Y + Off(1) * A.Half
                                Dx := Pos.X - GX
                                Dy := Pos.Y - GY
                                # ?? ??(? ??)
                                if (Announced <> GoalIdx):
                                    set Announced = GoalIdx
                                    Print("[GAME] ?? {GoalIdx + 1}/{GM_GOAL_COUNT} - {A.Name} ?, ?? ({GX}, {GY})")
                                if (Dx*Dx + Dy*Dy <= GM_TOUCH_R * GM_TOUCH_R):
                                    set GoalIdx = GoalIdx + 1
                                    Print("[GAME] ?? ??! {GoalIdx}/{GM_GOAL_COUNT}")
                                    if (GoalIdx >= GM_GOAL_COUNT):
                                        set Result = "WIN"
                                        set Ended = true

            # ?? ?? ??(30? ??)
            Rem := GM_ROUND_SEC - Elapsed
            if (Rem > 0.0, Rem < 30.5, Rem > 29.5) { Print("[GAME] ?? ?? 30?") }
            if (Rem > 0.0, Rem < 10.5, Rem > 9.5)  { Print("[GAME] ?? ?? 10?!") }

        # ??
        if (Result = "WIN"):
            Print("[GAME] === ??! ?? {GM_GOAL_COUNT}? ?? ?? (?? {Elapsed}?) ===")
        else if (Result = "CAUGHT"):
            Print("[GAME] === ?? - ???? ??? (?? {Elapsed}?) ===")
        else:
            Print("[GAME] === ?? - ?? ?? (?? {GoalIdx}/{GM_GOAL_COUNT}) ===")

    # ??? ?? ???
    GM_ArenaAtHelper():void = {}

GM_ArenaAt(Arenas:[]gm_arena, Pos:vector3)<decides><transacts>:gm_arena=
    var FoundIdx : int = -1
    for (I -> A : Arenas):
        if (Abs(Pos.X - A.X) <= A.Half, Abs(Pos.Y - A.Y) <= A.Half, FoundIdx < 0):
            set FoundIdx = I
    FoundIdx >= 0
    Arenas[FoundIdx]
