# Sinnoh Visual + Playtest QA Harness

Automated visual QA and early-game playtest for the Sinnoh remake.
**Guardrails:** Emerald tileset PNGs only; Platinum *layout attrs* for reference
heatmaps (no ripped Nintendo images); no ROM/BIOS committed or downloaded.

## Quick start

```bash
# From repo root (needs pokeemerald.gba for mgba smoke; build with `make -j`)
python3 tools/qa/run_qa.py --out /tmp/sinnoh_qa

# Visual only (no emulator)
python3 tools/qa/run_qa.py --out /tmp/sinnoh_qa --skip-mgba

# Early-game route sim only
python3 tools/qa/early_game_playtest.py --out /tmp/sinnoh_qa/playtest
```

Outputs (not committed when large):

| Path | Contents |
|------|----------|
| `renders/` | Full top-down PNG per Sinnoh map (Emerald tiles) |
| `platinum_ref/` | Classified Platinum land heatmaps (collision/behavior) |
| `contact/` | Side-by-side Emerald vs Platinum reference sheets |
| `playtest/` | Route stop overlays + assertion report |
| `report.json` | Issues found + pass/fail summary |

## What it checks

1. **Visual renders** of every `LAND_TABLE` map + related interiors.
2. **Contact sheets** vs Platinum source layout attrs (walk/solid/water/path/tall).
3. **Auto-review** (reuses `visual_object_audit`, `collision_audit`,
   `city_door_warp_audit`): incomplete trees, grass-dominant paved cities,
   broken doors, trees inside buildings, walkable water, oversized sand/path.
4. **Early-game playtest (static)**: Twinleaf → Route201 → Verity → Sandgem →
   Route202 → Jubilife PC/Mart → Route203 → Oreburgh — door enterability,
   walk-into-solid/water asserts, catch-tutorial wiring.
5. **mGBA smoke**: boots `pokeemerald.gba` with HLE BIOS (no Nintendo BIOS)
   under `xvfb-run` / timeout; runs `make check TESTS=…` for catch-tutorial.

## CI / PR

Generated PNGs belong in CI artifacts or the PR description, **not** git
(unless tiny contact sheets). Keep `report.json` optional.
