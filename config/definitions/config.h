// Layers
#define BASE 0
#define QWERTY 1
#define NAV 2
#define HUB 3
#define BLT 4
#define GAME 5
#define GAMET 6
#define SYM_NUM 7
#define FUNCT 8
#define MOUSE 9

#define NO_GAME_AND_MOUSE BASE QWERTY NAV SYM_NUM FUNCT HUB BLT GAMET
#define NO_GAME_AND_NO_GAMET_AND_MOUSE BASE QWERTY NAV SYM_NUM FUNCT HUB BLT
#define NO_MOUSE BASE QWERTY NAV SYM_NUM FUNCT HUB BLT GAME
#define NO_GAME BASE QWERTY NAV SYM_NUM FUNCT HUB BLT MOUSE
#define NO_FUNCT BASE QWERTY NAV SYM_NUM HUB BLT GAME MOUSE
#define ALL 0xff

// Keys
#define XXX &none
#define ___ &trans

#define CUT LC(X)
#define COPY LC(INS)
#define PASTE LS(INS)
// #define BACK LG(LBKT)
// #define PREV_TAB LC(LS(TAB))
// #define NEXT_TAB RC(TAB)
// #define FWRD LG(RBKT)

&caps_word {
  /delete-property/ ignore-modifiers;
  continue-list = <UNDERSCORE MINUS BSPC DEL N1 N2 N3 N4 N5 N6 N7 N8 N9 N0>;
};

/*                KEY POSITIONS

  ╭─────────────────────╮ ╭─────────────────────╮
  │ LTP LTR LTM LTI LTC │ │ RTC RTI RTM RTR RTP │
  │ LHP LHR LHM LHI LHC │ │ RHC RHI RHM RHR RHP │
  │ LBP LBR LBM LBI LBC │ │ RBC RBI RBM RBR RBP │
  ╰───────────╮ TLL TLR │ │ TRL TRR ╭───────────╯
              ╰─────────╯ ╰─────────╯
  ╭─────────────────────╮ ╭─────────────────────╮
  │  0   1   2   3   4  │ │   5   6   7   8   9 │
  │ 10  11  12  13  14  │ │  15  16  17  18  19 │
  │ 20  21  22  23  24  │ │  25  26  27  28  29 │
  ╰───────────╮ 30  31  │ │  32  33 ╭───────────╯
              ╰─────────╯ ╰─────────╯            */

#define KEYS_L 0 1 2 3 4 10 11 12 13 14 20 21 22 23 24
#define KEYS_R 5 6 7 8 9 15 16 17 18 19 25 26 27 28 29
#define THUMBS 30 31 32 33

#define LTP 0   // left-top row
#define LTR 1
#define LTM 2
#define LTI 3
#define LTC 4

#define RTC 5   // right-top row
#define RTI 6
#define RTM 7
#define RTR 8
#define RTP 9

#define LHP 10  // left-middle row
#define LHR 11
#define LHM 12
#define LHI 13
#define LHC 14

#define RHC 15  // right-middle row
#define RHI 16
#define RHM 17
#define RHR 18
#define RHP 19

#define LBP 20  // left-bottom row
#define LBR 21
#define LBM 22
#define LBI 23
#define LBC 24

#define RBC 25  // right-bottom row
#define RBI 26
#define RBM 27
#define RBR 28
#define RBP 29

#define TLL 30 // left thumb keys
#define TLR 31

#define TRL 32  // right thumb keys
#define TRR 33
