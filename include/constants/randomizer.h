#ifndef GUARD_CONSTANTS_RANDOMIZER_H
#define GUARD_CONSTANTS_RANDOMIZER_H

// Bitfield stored in SaveBlock3.randomizer.options
#define RANDOMIZER_OPT_WILD            (1 << 0)
#define RANDOMIZER_OPT_ITEMS           (1 << 1)
#define RANDOMIZER_OPT_TRAINERS        (1 << 2)
#define RANDOMIZER_OPT_STARTERS        (1 << 3)
#define RANDOMIZER_OPT_NO_LEGENDARIES  (1 << 4)

// Hash contexts — keep stable; changing them reshuffles existing saves.
#define RANDOMIZER_CTX_WILD            1
#define RANDOMIZER_CTX_TRAINER         2
#define RANDOMIZER_CTX_ITEM_BALL       3
#define RANDOMIZER_CTX_HIDDEN_ITEM     4
#define RANDOMIZER_CTX_FIND_ITEM       5
#define RANDOMIZER_CTX_STARTER         6
#define RANDOMIZER_CTX_STATIC_GIFT     7

#endif // GUARD_CONSTANTS_RANDOMIZER_H
