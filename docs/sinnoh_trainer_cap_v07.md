# Sinnoh trainer flag cap (v0.7)

## Cap

| Symbol | Value | Role |
|--------|------:|------|
| `TRAINER_FLAGS_START` | `0x500` | First defeated-trainer flag |
| `MAX_TRAINERS_COUNT_EMERALD` | **1024** | Flag allocation ceiling |
| `TRAINERS_COUNT_EMERALD` | **882** | `gTrainers` / party table length |
| `TRAINER_FLAGS_END` | `0x8FF` | Last trainer flag |
| `SYSTEM_FLAGS` | `0x900` | First system flag (shifts with the cap) |

## Why 1024 is safe

- Each trainer ID uses one bit in `SaveBlock1.flags`.
- Raising `MAX_TRAINERS_COUNT` by N grows `FLAGS_COUNT` by N and `NUM_FLAG_BYTES` by ~N/8.
- Measured at MAX=864: `sizeof(SaveBlock1)=15568`, sector budget `4*3968=15872`, **free 304 bytes**.
- Measured at MAX=1024: `sizeof(SaveBlock1)=15588` (`NUM_FLAG_BYTES` 300→320), **free 284 bytes**.
- `STATIC_ASSERT` in `src/save.c` (`SaveBlock1FreeSpace`) enforces the sector budget at compile time.
- Trainer IDs and `TRAINER_PARTNER(p) = MAX + p` remain within `u16`.
- Rematch / Vs. Seeker / Trainer Hill tables are separate enums and do not index `MAX_TRAINERS_COUNT`.

Do not raise the cap without re-checking `sizeof(struct SaveBlock1)` against `SECTOR_DATA_SIZE * 4`.

## v0.7 trainer IDs in use

- `TRAINER_VETERAN_GRANT` = 864
- `TRAINER_HIKER_ALEXANDER` = 865
- `TRAINER_JOGGER_RAUL` = 866
- `TRAINER_POKE_KID_DANIELLE` = 867
- `TRAINER_NINJA_BOY_FABIAN` = 870
- `TRAINER_NINJA_BOY_BRENNAN` = 871
- `TRAINER_NINJA_BOY_BRUCE` = 873
- `TRAINER_ACE_TRAINER_MAYA` = 875
- `TRAINER_PI_CARLOS` = 876
- `TRAINER_GALACTIC_GRUNT_LAKE_VERITY_1` = 878
- `TRAINER_GALACTIC_GRUNT_LAKE_VERITY_3` = 879
- `TRAINER_GALACTIC_GRUNT_LAKE_VERITY_2` = 880
- `TRAINER_GALACTIC_GRUNT_LAKE_VERITY_4` = 881

Holes in 868–877 are unused reserved slots under TRAINERS_COUNT=882; safe for flags.
