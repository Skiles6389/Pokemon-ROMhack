#ifndef GUARD_RANDOMIZER_H
#define GUARD_RANDOMIZER_H

#include "constants/items.h"
#include "constants/randomizer.h"
#include "constants/species.h"

// struct RandomizerSaveData lives in global.h (SaveBlock3).

void Randomizer_InitNewGameDefaults(void);
void Randomizer_SetOptions(u8 options);
void Randomizer_SetSeed(u32 seed);
u8 Randomizer_GetOptions(void);
u32 Randomizer_GetSeed(void);
bool32 Randomizer_IsEnabled(u8 optBit);

u32 Randomizer_Hash(u32 context, u32 key);
enum Species Randomizer_PickSpecies(u32 context, u32 key);
enum Item Randomizer_PickItem(u32 context, u32 key, enum Item original);

enum Species Randomizer_RemapWildSpecies(enum Species original, u32 slot);
enum Species Randomizer_RemapTrainerSpecies(enum Species original, u16 trainerId, u8 slot);
enum Species Randomizer_RemapStarterSpecies(enum Species original);
enum Item Randomizer_RemapFieldItem(enum Item original, u32 context, u32 key);

bool32 Randomizer_IsSpeciesAllowed(enum Species species);
bool32 Randomizer_IsItemAllowed(enum Item item);

void CB2_InitRandomizerMenu(void);
void Randomizer_RemapFindItemVar(void);

#endif // GUARD_RANDOMIZER_H
