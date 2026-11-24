# Sinnoh trainer flag cap (v0.7)

## Cap

| Symbol | Value | Role |
|--------|------:|------|
| `TRAINER_FLAGS_START` | `0x500` | First defeated-trainer flag |
| `MAX_TRAINERS_COUNT_EMERALD` | **1024** | Flag allocation ceiling |
| `TRAINERS_COUNT_EMERALD` | live (`max ID + 1`) | `gTrainers` / party table length |
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
