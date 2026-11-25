#include "global.h"
#include "randomizer.h"
#include "event_data.h"
#include "item.h"
#include "overworld.h"
#include "pokemon.h"
#include "random.h"
#include "constants/items.h"
#include "constants/maps.h"
#include "constants/species.h"

#define RANDOMIZER_REJECT_TRIES 96

void Randomizer_InitNewGameDefaults(void)
{
    gSaveBlock3Ptr->randomizer.seed = 0;
    gSaveBlock3Ptr->randomizer.options = 0;
}

void Randomizer_SetOptions(u8 options)
{
    gSaveBlock3Ptr->randomizer.options = options;
}

void Randomizer_SetSeed(u32 seed)
{
    // Never leave seed at 0 — hash mixes poorly with all-zero.
    gSaveBlock3Ptr->randomizer.seed = seed ? seed : 0xA5A5A5A5u;
}

u8 Randomizer_GetOptions(void)
{
    return gSaveBlock3Ptr->randomizer.options;
}

u32 Randomizer_GetSeed(void)
{
    return gSaveBlock3Ptr->randomizer.seed;
}

bool32 Randomizer_IsEnabled(u8 optBit)
{
    return (gSaveBlock3Ptr->randomizer.options & optBit) != 0;
}

u32 Randomizer_Hash(u32 context, u32 key)
{
    u32 h = gSaveBlock3Ptr->randomizer.seed;
    h ^= context * 0x9E3779B9u;
    h ^= key * 0x85EBCA6Bu;
    h ^= h >> 16;
    h *= 0x7FEB352Du;
    h ^= h >> 15;
    h *= 0x846CA68Bu;
    h ^= h >> 16;
    return h;
}

bool32 Randomizer_IsSpeciesAllowed(enum Species species)
{
    const struct SpeciesInfo *info;

    if (species == SPECIES_NONE || species == SPECIES_EGG || species >= NUM_SPECIES)
        return FALSE;
    if (!IsSpeciesEnabled(species))
        return FALSE;
    // Base forms only — skip regional/battle/mega/gmax/etc. form ids.
    if (GET_BASE_SPECIES_ID(species) != species)
        return FALSE;

    info = &gSpeciesInfo[species];
    if (info->isMegaEvolution || info->isPrimalReversion || info->isUltraBurst
        || info->isGigantamax || info->isTeraForm || info->isTotem)
        return FALSE;

    if (Randomizer_IsEnabled(RANDOMIZER_OPT_NO_LEGENDARIES))
    {
        if (info->isRestrictedLegendary || info->isSubLegendary || info->isMythical
            || info->isUltraBeast || info->isParadox)
            return FALSE;
    }

    return TRUE;
}

bool32 Randomizer_IsItemAllowed(enum Item item)
{
    if (item == ITEM_NONE || item >= ITEMS_COUNT)
        return FALSE;
    // Key items, HMs (price 0 TMs/HMs), and important/story items stay fixed.
    if (GetItemPocket(item) == POCKET_KEY_ITEMS)
        return FALSE;
    if (GetItemImportance(item) != 0)
        return FALSE;
    if (GetItemPocket(item) == POCKET_TM_HM && GetItemPrice(item) == 0)
        return FALSE;
    return TRUE;
}

enum Species Randomizer_PickSpecies(u32 context, u32 key)
{
    u32 h = Randomizer_Hash(context, key);
    u32 i;

    for (i = 0; i < RANDOMIZER_REJECT_TRIES; i++)
    {
        enum Species candidate = (enum Species)((h % (NUM_SPECIES - 1)) + 1);
        if (Randomizer_IsSpeciesAllowed(candidate))
            return candidate;
        h = h * 1664525u + 1013904223u + i;
    }

    // Extremely unlikely fallback — keep a safe early-game mon.
    return SPECIES_STARLY;
}

enum Item Randomizer_PickItem(u32 context, u32 key, enum Item original)
{
    u32 h;
    u32 i;

    if (!Randomizer_IsItemAllowed(original))
        return original;

    h = Randomizer_Hash(context, key);
    for (i = 0; i < RANDOMIZER_REJECT_TRIES; i++)
    {
        enum Item candidate = (enum Item)((h % (ITEMS_COUNT - 1)) + 1);
        if (Randomizer_IsItemAllowed(candidate))
            return candidate;
        h = h * 1664525u + 1013904223u + i;
    }
    return original;
}

static u32 CurrentMapKey(void)
{
    return ((u32)gSaveBlock1Ptr->location.mapGroup << 16) | gSaveBlock1Ptr->location.mapNum;
}

enum Species Randomizer_RemapWildSpecies(enum Species original, u32 slot)
{
    if (!Randomizer_IsEnabled(RANDOMIZER_OPT_WILD))
        return original;
    if (original == SPECIES_NONE || original == SPECIES_EGG)
        return original;
    return Randomizer_PickSpecies(RANDOMIZER_CTX_WILD, CurrentMapKey() ^ (slot * 0x10001u));
}

enum Species Randomizer_RemapTrainerSpecies(enum Species original, u16 trainerId, u8 slot)
{
    if (!Randomizer_IsEnabled(RANDOMIZER_OPT_TRAINERS))
        return original;
    if (original == SPECIES_NONE || original == SPECIES_EGG)
        return original;
    return Randomizer_PickSpecies(RANDOMIZER_CTX_TRAINER, ((u32)trainerId << 8) | slot);
}

enum Species Randomizer_RemapStarterSpecies(enum Species original)
{
    u32 slot;

    if (!Randomizer_IsEnabled(RANDOMIZER_OPT_STARTERS))
        return original;

    if (original == SPECIES_TURTWIG)
        slot = 0;
    else if (original == SPECIES_CHIMCHAR)
        slot = 1;
    else if (original == SPECIES_PIPLUP)
        slot = 2;
    else
        return original;

    return Randomizer_PickSpecies(RANDOMIZER_CTX_STARTER, slot);
}

enum Item Randomizer_RemapFieldItem(enum Item original, u32 context, u32 key)
{
    if (!Randomizer_IsEnabled(RANDOMIZER_OPT_ITEMS))
        return original;
    return Randomizer_PickItem(context, key, original);
}

// Script special: remap VAR_0x8000 (finditem ITEMID) when field-item randomizer is on.
void Randomizer_RemapFindItemVar(void)
{
    enum Item original = (enum Item)gSpecialVar_0x8000;
    gSpecialVar_0x8000 = Randomizer_RemapFieldItem(
        original,
        RANDOMIZER_CTX_FIND_ITEM,
        CurrentMapKey() ^ original);
}

// Script special: VAR_0x8004 = base starter species → VAR_0x8005 = remapped (or same).
void Randomizer_PreviewStarterSpecies(void)
{
    gSpecialVar_0x8005 = Randomizer_RemapStarterSpecies((enum Species)gSpecialVar_0x8004);
}
