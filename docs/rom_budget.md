# ROM space budget (Sinnoh remake)

Measured free space is **trailing `0xFF` padding** in the 32 MiB `pokeemerald.gba`.
Run after every milestone:

```bash
make -j$(nproc)
python3 tools/rom_space.py
python3 tools/rom_space.py --require-reserve
```

## Current free space (v0.7 / M20 complete)

| Metric | Value |
|--------|------:|
| ROM size | 32 MiB (33,554,432 bytes) |
| Free trailing 0xFF | **~5.88 MiB (6,160,744 bytes)** at branch start |
| Hard reserve (never spend) | **1.50 MiB (1,572,864 bytes)** |
| Spendable for M21→postgame | **~4.38 MiB** |

Update the “after milestone” rows below whenever `rom_space.py` is run.

## Rules

- Reuse Emerald tilesets, metatiles, music, and graphics. Prefer collision-stitched Platinum land data → Emerald metatiles (no DS asset rips).
- Do **not** add large new assets without logging their packed size here.
- If a milestone exceeds its allowance, recover space (unused Hoenn-only maps/scripts/assets that nothing references) **before** starting the next milestone.
- Never remove anything still referenced by the game or by tests.
- Keep ≥ **1.5 MiB** free at all times (`tools/rom_space.py --require-reserve`).

## Milestone allowances (spendable pool ≈ 4.38 MiB)

| Milestone | Scope (Platinum order) | Allowance | Notes |
|-----------|------------------------|----------:|-------|
| **M21** | Route 212 N/S, Great Marsh, HM Defog | **280 KiB** | Fen Badge already obtained |
| **M22** | Route 210 North, Celestic Town, HM Surf | **280 KiB** | Fog + Defog; Surf gift |
| **M23** | Route 218, Canalave approach, Iron Island, Byron Gym (Mine Badge) | **320 KiB** | Badge 6 |
| **M24** | Lake Valor / Galactic fallout, Hearthome Fantina if needed, Route 216–217 snow | **350 KiB** | Relic / story catch-up |
| **M25** | Snowpoint / Candice (Icicle Badge), Lake Acuity | **350 KiB** | Badge 7 |
| **M26** | Veilstone Galactic HQ rematch path, Spear Pillar approach | **400 KiB** | Story denser |
| **M27** | Distortion World | **450 KiB** | Large unique layout; keep lean |
| **M28** | Victory Road + League approach | **400 KiB** | |
| **M29** | Elite Four | **350 KiB** | Reuse League interiors |
| **M30** | Champion | **250 KiB** | |
| **Postgame stub** | Contest/rematch/stubs only | **150 KiB** | Short; no full Battle Frontier |
| **Contingency** | Overruns, QA fixes, small assets | **~750 KiB** | Buffer inside spendable |

Sum of milestone allowances ≈ 3.58 MiB; contingency fills the rest of the ~4.38 MiB spendable pool. The **1.5 MiB reserve is never allocated**.

## After-milestone ledger

| Checkpoint | Free 0xFF | Spendable (free − 1.5 MiB) | Notes |
|------------|----------:|---------------------------:|-------|
| v0.7 baseline | 6,160,744 (5.875 MiB) | ~4.38 MiB | Before M21 |
| After M21 | 6,119,168 (5.836 MiB) | ~4.41 MiB | Used ~41 KiB (under 280 KiB) |
| After M22 | 6,101,056 (5.818 MiB) | ~4.32 MiB | Used ~18 KiB (under 280 KiB) |
| After M23 | 6,080,464 (5.799 MiB) | ~4.37 MiB | Used ~20 KiB from M22 (under 320 KiB) |
| After M24 | 6,036,264 (5.757 MiB) | ~4.26 MiB | Used ~43 KiB from M23 (under 350 KiB) |
| After M25 | 6,008,756 (5.730 MiB) | ~4.23 MiB | Used ~27 KiB from M24 (under 350 KiB) |
| After M26 | 5,991,004 (5.713 MiB) | ~4.21 MiB | Used ~17 KiB from M25 (under 400 KiB) |
| After M27 | 5,911,792 (5.638 MiB) | ~4.14 MiB | Used ~77 KiB from M26 (under 450 KiB) |

## Large assets log

| Asset | Milestone | Approx. size | Why needed |
|-------|-----------|-------------:|------------|
| _(none yet)_ | | | Prefer Emerald reuse |

## Recovery ideas (only if over allowance)

- Drop unreferenced Hoenn town interiors / unused contest halls already mirrored by Sinnoh.
- Cull unused FRLG map groups if unreferenced by warps/tests.
- Prefer shared indoor layouts (`House1`, `Shop`, `PokemonCenter`) over unique footprints.

### Measured after M22

- Free trailing 0xFF: **6,101,056 bytes (5.818 MiB)**
- Delta from M21 (~6,119,168): ~18 KiB used — under M22 allowance.
- Maps: Route210_North, CelesticTown (+ houses/cave stub/PC); Surf HM via Celestic grandma (Defog-gated).

### Measured after M23

- Free trailing 0xFF: **6,080,464 bytes (5.799 MiB)**
- Delta from M22 (~6,101,056): ~20 KiB used — under M23 allowance.
- Maps: Route218, CanalaveCity, IronIsland (EXACT); Byron Gym (Mine Badge + TM Flash Cannon).

### Measured after M24

- Free trailing 0xFF: **6,036,264 bytes (5.757 MiB)**
- Maps: Route211_East, Route216, Route217, LakeValor_Drained (EXACT); Fantina already present.
- Snowpoint road soft-closed on Route 217.

### Measured after M25

- Free trailing 0xFF: **6,008,756 bytes (5.730 MiB)**
- SnowpointCity, AcuityLakefront, LakeAcuity EXACT; Candice Icicle Badge + TM Avalanche; Jupiter at Lake Acuity.

### Measured after M26

- Free trailing 0xFF: **5,991,004 bytes (5.713 MiB)**
- Galactic HQ rematch path + SpearPillar EXACT; Distortion gate closed for M27.
