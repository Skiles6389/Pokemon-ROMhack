// A minimal Poketch for the Sinnoh demo: opened from the start menu once the player has
// it. Apps are plain message boxes so it needs no new graphics.
#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "rtc.h"
#include "string_util.h"
#include "text.h"
#include "constants/battle.h"

static const u8 sText_Morning[] = _("Morning");
static const u8 sText_Day[] = _("Day");
static const u8 sText_Evening[] = _("Evening");
static const u8 sText_Night[] = _("Night");
static const u8 sText_Colon[] = _(":");
static const u8 sText_Space[] = _(" ");
static const u8 sText_Slash[] = _("/");
static const u8 sText_NewLine[] = _("\n");
static const u8 sText_NewPage[] = _("\p");
static const u8 sText_Egg[] = _("EGG");
static const u8 sText_Ok[] = _("OK");
static const u8 sText_Fainted[] = _("FNT");
static const u8 sText_Sleep[] = _("SLP");
static const u8 sText_Poison[] = _("PSN");
static const u8 sText_Burn[] = _("BRN");
static const u8 sText_Freeze[] = _("FRZ");
static const u8 sText_Paralysis[] = _("PAR");
static const u8 sText_NoMons[] = _("No POKéMON with you.");

// STR_VAR_1 = "HH:MM", STR_VAR_2 = time of day.
void Poketch_BufferTime(void)
{
    const u8 *period;

    RtcCalcLocalTime();
    ConvertIntToDecimalStringN(gStringVar1, gLocalTime.hours, STR_CONV_MODE_LEADING_ZEROS, 2);
    StringAppend(gStringVar1, sText_Colon);
    ConvertIntToDecimalStringN(gStringVar3, gLocalTime.minutes, STR_CONV_MODE_LEADING_ZEROS, 2);
    StringAppend(gStringVar1, gStringVar3);

    switch (GetTimeOfDay())
    {
    case TIME_MORNING: period = sText_Morning; break;
    case TIME_EVENING: period = sText_Evening; break;
    case TIME_NIGHT:   period = sText_Night; break;
    default:           period = sText_Day; break;
    }
    StringCopy(gStringVar2, period);
}

static const u8 *StatusText(struct Pokemon *mon)
{
    u32 status = GetMonData(mon, MON_DATA_STATUS);

    if (GetMonData(mon, MON_DATA_HP) == 0)
        return sText_Fainted;
    if (status & STATUS1_SLEEP)
        return sText_Sleep;
    if (status & STATUS1_PSN_ANY)
        return sText_Poison;
    if (status & STATUS1_BURN)
        return sText_Burn;
    if (status & STATUS1_ICY_ANY)
        return sText_Freeze;
    if (status & STATUS1_PARALYSIS)
        return sText_Paralysis;
    return sText_Ok;
}

// gStringVar4 = one line per party member: name, HP/max HP, status; two per page.
void Poketch_BufferParty(void)
{
    u32 i, shown = 0;
    u8 num[8];

    gStringVar4[0] = EOS;
    for (i = 0; i < PARTY_SIZE; i++)
    {
        struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][i];

        if (GetMonData(mon, MON_DATA_SPECIES) == SPECIES_NONE)
            continue;
        if (shown != 0)
            StringAppend(gStringVar4, (shown % 2) ? sText_NewLine : sText_NewPage);
        shown++;
        if (GetMonData(mon, MON_DATA_IS_EGG))
        {
            StringAppend(gStringVar4, sText_Egg);
            continue;
        }
        GetMonData(mon, MON_DATA_NICKNAME, gStringVar3);
        StringGet_Nickname(gStringVar3);
        StringAppend(gStringVar4, gStringVar3);
        StringAppend(gStringVar4, sText_Space);
        ConvertIntToDecimalStringN(num, GetMonData(mon, MON_DATA_HP), STR_CONV_MODE_LEFT_ALIGN, 3);
        StringAppend(gStringVar4, num);
        StringAppend(gStringVar4, sText_Slash);
        ConvertIntToDecimalStringN(num, GetMonData(mon, MON_DATA_MAX_HP), STR_CONV_MODE_LEFT_ALIGN, 3);
        StringAppend(gStringVar4, num);
        StringAppend(gStringVar4, sText_Space);
        StringAppend(gStringVar4, StatusText(mon));
    }
    if (shown == 0)
        StringCopy(gStringVar4, sText_NoMons);
}
