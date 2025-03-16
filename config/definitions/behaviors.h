/* Generic behavior configuration macro for ZMK hold–tap (or similar) behaviors.
 *
 * Parameters:
 *   LABEL             - Name 
 *   FLAVOR            - ["hold-preferred", "balanced", "tap-preferred", "tap-unless-interrupted"]
 *   TAPPING_TERM_MS   - Tapping term (e.g., <TAPPING_TERM_MS>)
 *   QUICK_TAP_MS      - Quick tap timeout (e.g., <QUICK_TAP_MS>)
 *   REQUIRE_IDLE_MS   - Required prior idle time (e.g., <REQUIRE_PRIOR_IDLE_MS>)
 *   BINDINGS          - (e.g., <&kp>, <&kp>, <&sk>, <&mo>)
 *   TRIGGER_KEYS      - The key positions that trigger the hold (e.g., <KEYS_R THUMBS>)
 */
#define HOLD_TAP(                                         \
  LABEL,                                                  \
  FLAVOR,                                                 \
  TAPPING_TERM_MS,                                        \
  QUICK_TAP_MS,                                           \
  REQUIRE_IDLE_MS,                                        \
  BIND_1,                                                 \
  BIND_2,                                                 \
  TRIGGER_KEYS,                                           \
  ...                                                     \
)                                                         \
  /omit-if-no-ref/ LABEL: LABEL {                         \
    compatible                 = "zmk,behavior-hold-tap"; \
    #binding-cells             = <2>;                     \
    flavor                     = FLAVOR;                  \
    tapping-term-ms            = <TAPPING_TERM_MS>;       \
    quick-tap-ms               = <QUICK_TAP_MS>;          \
    require-prior-idle-ms      = <REQUIRE_IDLE_MS>;       \
    bindings                   = <BIND_1>, <BIND_2>;      \
    hold-trigger-key-positions = TRIGGER_KEYS;            \
    __VA_ARGS__                                           \
  };
//NOTE: __VA_ARGS__:
// - hold-trigger-on-release; // works with hold-trigger-key-positions, waits second key release 

#define STICKY_KEY(                         \
  LABEL,                                    \
  BINDING,                                  \
  RELEASE_AFTER_MS,                         \
  ...                                       \
)                                           \
  /omit-if-no-ref/ LABEL: LABEL {           \
    compatible = "zmk,behavior-sticky-key"; \
    #binding-cells = <1>;                   \
    bindings = <BINDING>;                   \
    release-after-ms = <RELEASE_AFTER_MS>;  \
    __VA_ARGS__                             \
  };
//NOTE: __VA_ARGS__:
// - quick-release;                       // no double capitalization when rolling keys
// - /delete-property/ ignore-modifiers;  // avoids combining modifiers
// - lazy;                                // activate sticky key just before the next key press


#define TAP_DANCE(                          \
  LABEL,                                    \
  TAPPING_TERM_MS,                          \
  ...                                       \
)                                           \
  /omit-if-no-ref/ LABEL: LABEL {           \
    compatible = "zmk,behavior-tap-dance";  \
    #binding-cells = <0>;                   \
    tapping-term-ms = <TAPPING_TERM_MS>;    \
    bindings = __VA_ARGS__;                 \
  };

#define MACRO(NAME, WAIT_MS, TAP_MS, ...)   \
  NAME: NAME {                              \
    compatible = "zmk,behavior-macro";      \
    #binding-cells = <0>;                   \
    wait-ms = <WAIT_MS>;                    \
    tap-ms = <TAP_MS>;                      \
    bindings = __VA_ARGS__;                 \
  };

#define MOD_MORPH(NAME, UNSHIFTED, SHIFTED, MODS, KEEP_MODS)  \
  NAME: NAME {                                                \
    compatible = "zmk,behavior-mod-morph";                    \
    #binding-cells = <0>;                                     \
    bindings = <UNSHIFTED>, <SHIFTED>;                        \
    mods = <MODS>;                                            \
    keep-mods = <KEEP_MODS>;                                  \
  };
//NOTE: KEEP_MODS=0 by default

//#define TURBO_SYMBOL(NAME, BINDINGS, WAIT_MS) \
//  NAME: NAME { \
//    compatible = "zmk,behavior-turbo-key"; \
//    label = ZMK_MACRO_STRINGIFY(NAME); \
//    #binding-cells = <0>; \
//    wait-ms = <WAIT_MS>; \
//    bindings = <BINDINGS>; \
//  };
