using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/Simulation/Tags }

# Shadow Bait - Arena Hub
# ? ??? ??? ?? "?? ?"? ???? ?? ???? ??????.
# A -> B -> C -> D -> A ??. GUI ?? ???(?? ?? ?? ??).

arena_info := class<final>:
    Name : string
    X    : float
    Y    : float
    Half : float

# v2 ??? ?? (build_arena_v2.ps1? ??)
GetArenas():[]arena_info =
    array:
        arena_info{ Name := "A-base-noLure(teal)", X := -30000.0, Y := 30000.0, Half := 2600.0 }
        arena_info{ Name := "B-base-lure(purple)", X :=      0.0, Y := 30000.0, Half := 2600.0 }
        arena_info{ Name := "C-maze-lure(red)",    X :=  30000.0, Y := 30000.0, Half := 2600.0 }
        arena_info{ Name := "D-open-lure(blue)",   X :=  60000.0, Y := 30000.0, Half := 4200.0 }

HUB_PORTAL_R : float = 350.0      # ?? ? ??
HUB_SPAWN_IN : float = 500.0      # ?? ? ??? ???? ???? ??
HUB_TICK     : float = 0.35

shadow_bait_hub := class(creative_device):

    OnBegin<override>()<suspends>:void=
        Print("[HUB] Shadow Bait arena hub online")
        Arenas := GetArenas()
        for (A : Arenas):
            Print("[HUB] arena {A.Name} portal at ({A.X}, {A.Y - A.Half + 700.0})")
        spawn { WatchLoop(Arenas) }

    # ?? ????? ??? ????? ??? ?? ? ?? ? ??
    WatchLoop(Arenas:[]arena_info)<suspends>:void=
        var LastTeleport : float = -99.0
        var Elapsed : float = 0.0
        loop:
            Sleep(HUB_TICK)
            set Elapsed = Elapsed + HUB_TICK
            if (Elapsed - LastTeleport >= 2.0):              # ?? ?? ??
                Players := GetPlayspace().GetPlayers()
                for (P : Players):
                    if (C := P.GetFortCharacter[]):
                        Pos := C.GetTransform().Translation
                        if (Idx := PortalIndexAt[Arenas, Pos]):
                            NextIdx := Mod[Idx + 1, 4] or 0
                            if (Dest := Arenas[NextIdx]):
                                # ?? ??: ?? ???? ??? ??
                                TX := Dest.X - Dest.Half + HUB_SPAWN_IN
                                TY := Dest.Y - Dest.Half + HUB_SPAWN_IN
                                if (C.TeleportTo[vector3{X := TX, Y := TY, Z := 200.0}, IdentityRotation()]):
                                    set LastTeleport = Elapsed
                                    Print("[HUB] moved to {Dest.Name}")

    # ?? ??? ?? ???? ?? ??? (??? ??)
    PortalIndexAt(Arenas:[]arena_info, Pos:vector3)<decides><transacts>:int=
        var Found : int = -1
        for (I -> A : Arenas):
            PX := A.X
            PY := A.Y - A.Half + 700.0
            Dx := Pos.X - PX
            Dy := Pos.Y - PY
            if (Dx*Dx + Dy*Dy <= HUB_PORTAL_R * HUB_PORTAL_R, Found < 0):
                set Found = I
        Found >= 0
        Found
