#include "global.h"
#include "randomizer.h"
#include "bg.h"
#include "gpu_regs.h"
#include "international_string_util.h"
#include "main.h"
#include "menu.h"
#include "overworld.h"
#include "palette.h"
#include "random.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "window.h"
#include "constants/rgb.h"
#include "constants/songs.h"

enum
{
    RMENU_WILD,
    RMENU_ITEMS,
    RMENU_TRAINERS,
    RMENU_STARTERS,
    RMENU_NO_LEGENDS,
    RMENU_CONFIRM,
    RMENU_COUNT,
};

enum
{
    WIN_HEADER,
    WIN_OPTIONS,
};

#define tSelection data[0]
#define tOptions data[1]

static void MainCB2(void);
static void Task_RandomizerMenuFadeIn(u8 taskId);
static void Task_RandomizerMenuInput(u8 taskId);
static void Task_RandomizerMenuFadeOut(u8 taskId);
static void DrawRandomizerMenu(u8 taskId);
static void HighlightSelection(u8 selection);

static const u16 sOptionMenuText_Pal[] = INCGFX_U16("graphics/interface/option_menu_text.pal", ".gbapal");

static const struct BgTemplate sBgTemplates[] =
{
    {
        .bg = 1,
        .charBaseIndex = 1,
        .mapBaseIndex = 30,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 1,
        .baseTile = 0
    },
    {
        .bg = 0,
        .charBaseIndex = 1,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0
    },
};

static const struct WindowTemplate sWindowTemplates[] =
{
    [WIN_HEADER] = {
        .bg = 1,
        .tilemapLeft = 2,
        .tilemapTop = 1,
        .width = 26,
        .height = 2,
        .paletteNum = 1,
        .baseBlock = 2
    },
    [WIN_OPTIONS] = {
        .bg = 0,
        .tilemapLeft = 2,
        .tilemapTop = 5,
        .width = 26,
        .height = 14,
        .paletteNum = 1,
        .baseBlock = 0x36
    },
    DUMMY_WIN_TEMPLATE
};

static const u8 sText_Header[] = _("RANDOMIZER OPTIONS");
static const u8 sText_Wild[] = _("WILD POKéMON");
static const u8 sText_Items[] = _("FIELD ITEMS");
static const u8 sText_Trainers[] = _("TRAINER TEAMS");
static const u8 sText_Starters[] = _("STARTERS");
static const u8 sText_NoLegends[] = _("BAN LEGENDARIES");
static const u8 sText_Confirm[] = _("CONFIRM");
static const u8 sText_On[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}ON");
static const u8 sText_Off[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}OFF");
static const u8 sText_Hint[] = _("Defaults OFF. A: toggle / confirm");

static const u8 *const sItemNames[RMENU_COUNT] =
{
    [RMENU_WILD] = sText_Wild,
    [RMENU_ITEMS] = sText_Items,
    [RMENU_TRAINERS] = sText_Trainers,
    [RMENU_STARTERS] = sText_Starters,
    [RMENU_NO_LEGENDS] = sText_NoLegends,
    [RMENU_CONFIRM] = sText_Confirm,
};

static const u8 sOptionBits[RMENU_COUNT] =
{
    [RMENU_WILD] = RANDOMIZER_OPT_WILD,
    [RMENU_ITEMS] = RANDOMIZER_OPT_ITEMS,
    [RMENU_TRAINERS] = RANDOMIZER_OPT_TRAINERS,
    [RMENU_STARTERS] = RANDOMIZER_OPT_STARTERS,
    [RMENU_NO_LEGENDS] = RANDOMIZER_OPT_NO_LEGENDARIES,
    [RMENU_CONFIRM] = 0,
};

static void VBlankCB(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void MainCB2(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

void CB2_InitRandomizerMenu(void)
{
    switch (gMain.state)
    {
    default:
    case 0:
        SetVBlankCallback(NULL);
        gMain.state++;
        break;
    case 1:
        DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, (void *)OAM, OAM_SIZE);
        DmaClear16(3, (void *)PLTT, PLTT_SIZE);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sBgTemplates, ARRAY_COUNT(sBgTemplates));
        ChangeBgX(0, 0, BG_COORD_SET);
        ChangeBgY(0, 0, BG_COORD_SET);
        ChangeBgX(1, 0, BG_COORD_SET);
        ChangeBgY(1, 0, BG_COORD_SET);
        InitWindows(sWindowTemplates);
        DeactivateAllTextPrinters();
        SetGpuReg(REG_OFFSET_WIN0H, 0);
        SetGpuReg(REG_OFFSET_WIN0V, 0);
        SetGpuReg(REG_OFFSET_WININ, WININ_WIN0_BG0);
        SetGpuReg(REG_OFFSET_WINOUT, WINOUT_WIN01_BG0 | WINOUT_WIN01_BG1 | WINOUT_WIN01_CLR);
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG0 | BLDCNT_EFFECT_DARKEN);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 4);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_WIN0_ON | DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);
        ShowBg(0);
        ShowBg(1);
        gMain.state++;
        break;
    case 2:
        ResetPaletteFade();
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        gMain.state++;
        break;
    case 3:
        LoadBgTiles(1, GetWindowFrameTilesPal(gSaveBlock2Ptr->optionsWindowFrameType)->tiles, 0x120, 0x1A2);
        LoadPalette(sOptionMenuText_Pal, BG_PLTT_ID(1), sizeof(sOptionMenuText_Pal));
        LoadPalette(GetWindowFrameTilesPal(gSaveBlock2Ptr->optionsWindowFrameType)->pal, BG_PLTT_ID(7), PLTT_SIZE_4BPP);
        gMain.state++;
        break;
    case 4:
        PutWindowTilemap(WIN_HEADER);
        DrawStdWindowFrame(WIN_HEADER, FALSE);
        FillWindowPixelBuffer(WIN_HEADER, PIXEL_FILL(1));
        AddTextPrinterParameterized(WIN_HEADER, FONT_NORMAL, sText_Header, 8, 1, TEXT_SKIP_DRAW, NULL);
        CopyWindowToVram(WIN_HEADER, COPYWIN_FULL);
        gMain.state++;
        break;
    case 5:
    {
        u8 taskId;
        PutWindowTilemap(WIN_OPTIONS);
        DrawStdWindowFrame(WIN_OPTIONS, FALSE);
        taskId = CreateTask(Task_RandomizerMenuFadeIn, 0);
        gTasks[taskId].tSelection = 0;
        gTasks[taskId].tOptions = 0;
        DrawRandomizerMenu(taskId);
        HighlightSelection(0);
        CopyWindowToVram(WIN_OPTIONS, COPYWIN_FULL);
        gMain.state++;
        break;
    }
    case 6:
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetVBlankCallback(VBlankCB);
        SetMainCallback2(MainCB2);
        return;
    }
}

static void HighlightSelection(u8 selection)
{
    SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(40 + selection * 16, 56 + selection * 16));
    SetGpuReg(REG_OFFSET_WIN0H, WIN_RANGE(16, 224));
}

static void DrawOnOff(u8 y, bool32 on)
{
    AddTextPrinterParameterized(WIN_OPTIONS, FONT_NORMAL, on ? sText_On : sText_Off, 160, y, TEXT_SKIP_DRAW, NULL);
}

static void DrawRandomizerMenu(u8 taskId)
{
    u8 options = gTasks[taskId].tOptions;
    u32 i;

    FillWindowPixelBuffer(WIN_OPTIONS, PIXEL_FILL(1));
    for (i = 0; i < RMENU_COUNT; i++)
    {
        u8 y = i * 16;
        AddTextPrinterParameterized(WIN_OPTIONS, FONT_NORMAL, sItemNames[i], 8, y, TEXT_SKIP_DRAW, NULL);
        if (i != RMENU_CONFIRM)
            DrawOnOff(y, (options & sOptionBits[i]) != 0);
    }
    AddTextPrinterParameterized(WIN_OPTIONS, FONT_SMALL, sText_Hint, 8, RMENU_COUNT * 16, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(WIN_OPTIONS, COPYWIN_GFX);
}

static void Task_RandomizerMenuFadeIn(u8 taskId)
{
    if (!gPaletteFade.active)
        gTasks[taskId].func = Task_RandomizerMenuInput;
}

static void Task_RandomizerMenuInput(u8 taskId)
{
    u8 selection = gTasks[taskId].tSelection;
    u8 options = gTasks[taskId].tOptions;

    if (JOY_NEW(DPAD_UP))
    {
        selection = (selection == 0) ? (RMENU_COUNT - 1) : (selection - 1);
        gTasks[taskId].tSelection = selection;
        HighlightSelection(selection);
        PlaySE(SE_SELECT);
    }
    else if (JOY_NEW(DPAD_DOWN))
    {
        selection = (selection + 1) % RMENU_COUNT;
        gTasks[taskId].tSelection = selection;
        HighlightSelection(selection);
        PlaySE(SE_SELECT);
    }
    else if (JOY_NEW(DPAD_LEFT | DPAD_RIGHT | A_BUTTON))
    {
        if (selection == RMENU_CONFIRM)
        {
            if (JOY_NEW(A_BUTTON))
            {
                PlaySE(SE_SELECT);
                Randomizer_SetOptions(options);
                Randomizer_SetSeed(Random32() ^ (gMain.vblankCounter1 * 0x1000193u));
                BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
                gTasks[taskId].func = Task_RandomizerMenuFadeOut;
            }
        }
        else
        {
            options ^= sOptionBits[selection];
            gTasks[taskId].tOptions = options;
            DrawRandomizerMenu(taskId);
            PlaySE(SE_SELECT);
        }
    }
}

static void Task_RandomizerMenuFadeOut(u8 taskId)
{
    if (!gPaletteFade.active)
    {
        DestroyTask(taskId);
        FreeAllWindowBuffers();
        SetMainCallback2(CB2_ContinueNewGameFromRandomizer);
    }
}
