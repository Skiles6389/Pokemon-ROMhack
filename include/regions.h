#ifndef GUARD_REGIONS_H
#define GUARD_REGIONS_H

#include "global.h"
#include "constants/regions.h"

enum KantoSubRegion GetKantoSubregion(u32 mapSecId);

static inline enum Region GetRegionForSectionId(u32 sectionId)
{
    if (sectionId >= KANTO_MAPSEC_START && sectionId < MAPSEC_SPECIAL_AREA)
        return REGION_KANTO;
    return REGION_HOENN;
}

// The Sinnoh demo maps (Twinleaf Town -> Valley Windworks) use the Platinum soundtrack.
static inline bool32 IsSinnohMapSec(u32 sectionId)
{
    return sectionId >= MAPSEC_TWINLEAF_TOWN && sectionId <= MAPSEC_VEILSTONE_GATE;
}

static inline bool32 IsPlayerInSinnoh(void)
{
    return IsSinnohMapSec(gMapHeader.regionMapSectionId);
}

static inline enum Region GetCurrentRegion(void)
{
    return GetRegionForSectionId(gMapHeader.regionMapSectionId);
}

#endif // GUARD_REGIONS_H
