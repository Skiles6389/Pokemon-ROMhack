#include "global.h"
#include "test/test.h"
#include "battle.h"
#include "battle_setup.h"
#include "event_data.h"
#include "pokemon.h"
#include "constants/battle.h"
#include "constants/species.h"
#include "constants/vars.h"

TEST("IsRoute202CatchTutorial is true only during the catch demo state")
{
    VarSet(VAR_ROUTE202_STATE, 0);
    EXPECT(!IsRoute202CatchTutorial());
    VarSet(VAR_ROUTE202_STATE, 1);
    EXPECT(IsRoute202CatchTutorial());
    VarSet(VAR_ROUTE202_STATE, 2);
    EXPECT(!IsRoute202CatchTutorial());
}

TEST("Route 202 catch tutorial opponent is a fixed Bidoof (immune to wild remap)")
{
    ZeroEnemyPartyMons();
    CreateMaleMon(&gParties[B_TRAINER_OPPONENT_A][0], SPECIES_BIDOOF, 5);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_OPPONENT_A][0], MON_DATA_SPECIES), SPECIES_BIDOOF);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_OPPONENT_A][0], MON_DATA_LEVEL), 5);
    EXPECT(GetMonData(&gParties[B_TRAINER_OPPONENT_A][0], MON_DATA_HP) > 0);
}

TEST("CATCH_TUTORIAL battle type flag is the Wally/Old Man scripted catch bit")
{
    EXPECT(BATTLE_TYPE_CATCH_TUTORIAL != 0);
    gBattleTypeFlags = BATTLE_TYPE_CATCH_TUTORIAL;
    EXPECT(gBattleTypeFlags & BATTLE_TYPE_CATCH_TUTORIAL);
}
