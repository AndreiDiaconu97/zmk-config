/*                KEY POSITIONS
  ╭─────────────────────╮ ╭─────────────────────╮
  │ LT4 LT3 LT2 LT1 LT0 │ │ RT0 RT1 RT2 RT3 RT4 │
  │ LM4 LM3 LM2 LM1 LM0 │ │ RM0 RM1 RM2 RM3 RM4 │
  │ LB4 LB3 LB2 LB1 LB0 │ │ RB0 RB1 RB2 RB3 RB4 │
  ╰───────────╮ TL1 TL0 │ │ TR0 TR1 ╭───────────╯
              ╰─────────╯ ╰─────────╯            */

#pragma once

#define LT4 0
#define LT3 1
#define LT2 2
#define LT1 3
#define LT0 4

#define RT0 5
#define RT1 6
#define RT2 7
#define RT3 8
#define RT4 9

#define LM4 10
#define LM3 11
#define LM2 12
#define LM1 13
#define LM0 14

#define RM0 15
#define RM1 16
#define RM2 17
#define RM3 18
#define RM4 19

#define LB4 20
#define LB3 21
#define LB2 22
#define LB1 23
#define LB0 24

#define RB0 25
#define RB1 26
#define RB2 27
#define RB3 28
#define RB4 29

#define TL1 30
#define TL0 31
#define TR0 32
#define TR1 33

#define KEYS_L LT4 LT3 LT2 LT1 LT0 LM4 LM3 LM2 LM1 LM0 LB4 LB3 LB2 LB1 LB0
#define KEYS_R RT0 RT1 RT2 RT3 RT4 RM0 RM1 RM2 RM3 RM4 RB0 RB1 RB2 RB3 RB4
#define THUMBS TL1 TL0 TR0 TR1
#define ALL_KEYS KEYS_L KEYS_R THUMBS

// Layers
#define COLEMAK 0
#define QWERTY 1
#define SYM_NUM 2
#define NAV 3
#define FUNCT 4
#define BLT 5
#define GAME 6
#define MACRO_LAYER 7
//#define MOUSE 6

#define TYPING COLEMAK QWERTY
#define ALL 0xff

// Keys
#define XXX &none
#define ___ &trans

// #define BACK LG(LBKT)
// #define PREV_TAB LC(LS(TAB))
// #define NEXT_TAB RC(TAB)
// #define FWRD LG(RBKT)

#include "behaviors.h"
#include "../features/behaviors.dtsi"
#include "../features/adaptive_keys.dtsi"
// #include "../features/mouse.dtsi"
#include "../features/combos.dtsi"
#include "../features/symbols.dtsi"
#include "../features/macros.dtsi"
// #include "../features/leader.dtsi"
#include "keymap.dtsi"

#include "../features/secrets.dtsi"
