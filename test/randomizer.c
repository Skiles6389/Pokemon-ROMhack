#include "global.h"
#include "item.h"
#include "randomizer.h"
#include "test/test.h"
#include "constants/items.h"
#include "constants/species.h"

static void SetupRandomizer(u32 seed, u8 options)
{
    Randomizer_InitNewGameDefaults();
    Randomizer_SetSeed(seed);
    Randomizer_SetOptions(options);
}

TEST("Randomizer OFF leaves wild/trainer/item/starter remaps unchanged")
{
    SetupRandomizer(0xDEADBEEFu, 0);

    EXPECT_EQ(Randomizer_RemapWildSpecies(SPECIES_STARLY, 0), SPECIES_STARLY);
    EXPECT_EQ(Randomizer_RemapWildSpecies(SPECIES_BIDOOF, 3), SPECIES_BIDOOF);
    EXPECT_EQ(Randomizer_RemapTrainerSpecies(SPECIES_LUXRAY, 42, 0), SPECIES_LUXRAY);
    EXPECT_EQ(Randomizer_RemapTrainerSpecies(SPECIES_GARCHOMP, 99, 5), SPECIES_GARCHOMP);
    EXPECT_EQ(Randomizer_RemapStarterSpecies(SPECIES_TURTWIG), SPECIES_TURTWIG);
    EXPECT_EQ(Randomizer_RemapStarterSpecies(SPECIES_CHIMCHAR), SPECIES_CHIMCHAR);
    EXPECT_EQ(Randomizer_RemapStarterSpecies(SPECIES_PIPLUP), SPECIES_PIPLUP);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_POTION, RANDOMIZER_CTX_ITEM_BALL, 1), ITEM_POTION);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_GREAT_BALL, RANDOMIZER_CTX_HIDDEN_ITEM, 7), ITEM_GREAT_BALL);
}

TEST("Randomizer wild remap is deterministic for seed+slot")
{
    enum Species a, b, c;

    SetupRandomizer(0xC0FFEEu, RANDOMIZER_OPT_WILD);
    a = Randomizer_RemapWildSpecies(SPECIES_STARLY, 0);
    b = Randomizer_RemapWildSpecies(SPECIES_STARLY, 0);
    c = Randomizer_RemapWildSpecies(SPECIES_STARLY, 1);

    EXPECT_EQ(a, b);
    EXPECT(a != SPECIES_NONE && a != SPECIES_EGG);
    EXPECT(Randomizer_IsSpeciesAllowed(a));
    // Different slot keys should usually differ; allow rare collision but require allowed species.
    EXPECT(Randomizer_IsSpeciesAllowed(c));
}

TEST("Randomizer trainer remap is deterministic for trainerId+slot")
{
    enum Species a, b;

    SetupRandomizer(0xABCDEF01u, RANDOMIZER_OPT_TRAINERS);
    a = Randomizer_RemapTrainerSpecies(SPECIES_GARCHOMP, 1234, 0);
    b = Randomizer_RemapTrainerSpecies(SPECIES_GARCHOMP, 1234, 0);
    EXPECT_EQ(a, b);
    EXPECT(Randomizer_IsSpeciesAllowed(a));
}

TEST("Randomizer starter remap only touches Sinnoh starters")
{
    enum Species gift;

    SetupRandomizer(0x11111111u, RANDOMIZER_OPT_STARTERS);
    gift = Randomizer_RemapStarterSpecies(SPECIES_EEVEE);
    EXPECT_EQ(gift, SPECIES_EEVEE);

    EXPECT(Randomizer_IsSpeciesAllowed(Randomizer_RemapStarterSpecies(SPECIES_TURTWIG)));
    EXPECT(Randomizer_IsSpeciesAllowed(Randomizer_RemapStarterSpecies(SPECIES_CHIMCHAR)));
    EXPECT(Randomizer_IsSpeciesAllowed(Randomizer_RemapStarterSpecies(SPECIES_PIPLUP)));
}

TEST("Randomizer item exclusions keep key items, HMs, and important items")
{
    SetupRandomizer(0x22222222u, RANDOMIZER_OPT_ITEMS);

    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_BICYCLE, RANDOMIZER_CTX_FIND_ITEM, 1), ITEM_BICYCLE);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_TOWN_MAP, RANDOMIZER_CTX_FIND_ITEM, 2), ITEM_TOWN_MAP);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_HM01, RANDOMIZER_CTX_ITEM_BALL, 3), ITEM_HM01);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_HM03, RANDOMIZER_CTX_HIDDEN_ITEM, 4), ITEM_HM03);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_VS_SEEKER, RANDOMIZER_CTX_FIND_ITEM, 5), ITEM_VS_SEEKER);
    EXPECT_EQ(Randomizer_RemapFieldItem(ITEM_OAKS_PARCEL, RANDOMIZER_CTX_FIND_ITEM, 6), ITEM_OAKS_PARCEL);

    EXPECT(!Randomizer_IsItemAllowed(ITEM_BICYCLE));
    EXPECT(!Randomizer_IsItemAllowed(ITEM_HM01));
    EXPECT(!Randomizer_IsItemAllowed(ITEM_VS_SEEKER));
    EXPECT(Randomizer_IsItemAllowed(ITEM_POTION));
}

TEST("Randomizer field item remap is deterministic and never returns excluded items")
{
    enum Item a, b;
    u32 i;

    SetupRandomizer(0x33333333u, RANDOMIZER_OPT_ITEMS);
    a = Randomizer_RemapFieldItem(ITEM_POTION, RANDOMIZER_CTX_ITEM_BALL, 9);
    b = Randomizer_RemapFieldItem(ITEM_POTION, RANDOMIZER_CTX_ITEM_BALL, 9);
    EXPECT_EQ(a, b);
    EXPECT(Randomizer_IsItemAllowed(a));

    for (i = 0; i < 32; i++)
    {
        enum Item remapped = Randomizer_RemapFieldItem(ITEM_SUPER_POTION, RANDOMIZER_CTX_HIDDEN_ITEM, i);
        EXPECT(Randomizer_IsItemAllowed(remapped));
        EXPECT(remapped != ITEM_NONE);
    }
}

TEST("Randomizer species pool rejects NONE, Egg, and form-only ids")
{
    SetupRandomizer(0x44444444u, RANDOMIZER_OPT_WILD | RANDOMIZER_OPT_NO_LEGENDARIES);

    EXPECT(!Randomizer_IsSpeciesAllowed(SPECIES_NONE));
    EXPECT(!Randomizer_IsSpeciesAllowed(SPECIES_EGG));
    // Mega Charizard X is form-only when GET_BASE differs.
    if (GET_BASE_SPECIES_ID(SPECIES_CHARIZARD_MEGA_X) != SPECIES_CHARIZARD_MEGA_X)
        EXPECT(!Randomizer_IsSpeciesAllowed(SPECIES_CHARIZARD_MEGA_X));
}

TEST("Randomizer hash is stable for fixed seed and inputs")
{
    u32 h1, h2;

    SetupRandomizer(0x55AA55AAu, 0);
    h1 = Randomizer_Hash(RANDOMIZER_CTX_WILD, 0x1234);
    h2 = Randomizer_Hash(RANDOMIZER_CTX_WILD, 0x1234);
    EXPECT_EQ(h1, h2);
    EXPECT(h1 != Randomizer_Hash(RANDOMIZER_CTX_TRAINER, 0x1234));
}
