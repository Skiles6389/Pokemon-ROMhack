# mapgrid — ASCII map compiler

Author outdoor maps as plain-text `.grid` files under `maps_src/`, then compile
to Emerald `map.bin` + `map.json` events.

```bash
make mapgrid
# or
python3 tools/mapgrid/compile_maps.py
python3 tools/mapgrid/compile_maps.py maps_src/VerityLakefront.grid --check
```

`make` / `make rom` do **not** depend on mapgrid — compiled outputs are committed.

## Legend (see `legend.json`)

| Char | Meaning |
|------|---------|
| `T` | Tree (2×2 autotiled stamps; orphans → rock) |
| `.` | Grass |
| `,` | Tall grass / shaded gap |
| `=` | Dirt path (3×3 autotiled) |
| `:` | Sand |
| `~` | Water (surfable) |
| `L` | South ledge |
| `F` | Fence / brown ledge |
| `f` | Flowers |
| `S` | Sign (emits bg event; `@sign` scripts in order) |
| `W` | Warp (`@warp` dests in order) |
| `R` `#` | Rock / solid |
| `_` | Paved/grass |
| `P`/`V`/… | Stamp door anchors (`@stamp CHAR NAME DEST_MAP ID`) |

## Header directives

```
@name MapName
@layout LAYOUT_MAP_NAME
@width 32
@height 18
@primary gTileset_General
@secondary gTileset_Petalburg
@connection right MAP_ROUTE201 -11
@stamp P PLAYER_HOUSE MAP_FOO 0
@warp MAP_BAR 0
@sign MapName_EventScript_Sign
@grid
...rows...
```
