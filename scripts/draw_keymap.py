#!/usr/bin/env python3
"""Draw the keymap as an SVG, straight from the ZMK sources (stdlib only).

Parses config/definitions/keymap.dtsi (layers) and config/features/combos.dtsi
(combos), so the diagram cannot drift from the firmware.

Usage: scripts/draw_keymap.py [output.svg]   (default: docs/keymap.svg)
"""
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYMAP = ROOT / "config/definitions/keymap.dtsi"
COMBOS = ROOT / "config/features/combos.dtsi"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/keymap.svg"

# ── geometry ────────────────────────────────────────────────────────────────
KEY, PITCH, HALF_GAP = 52, 58, 40
STAGGER_L = [14, 5, 0, 5, 8]  # outer pinky → inner index
STAGGER_R = STAGGER_L[::-1]
PANEL_W = 10 * PITCH + HALF_GAP
PANEL_H = 4 * PITCH + 52
MARGIN = 28

# key order in a `bindings` list: three rows of (5 left, 5 right), then 4 thumbs
NAMES = (
    [f"LT{i}" for i in (4, 3, 2, 1, 0)] + [f"RT{i}" for i in range(5)]
    + [f"LM{i}" for i in (4, 3, 2, 1, 0)] + [f"RM{i}" for i in range(5)]
    + [f"LB{i}" for i in (4, 3, 2, 1, 0)] + [f"RB{i}" for i in range(5)]
    + ["TL1", "TL0", "TR0", "TR1"]
)


def key_xy(name):
    """Top-left corner of a key inside a panel (panel origin = 0,0)."""
    if name[0] == "T":  # thumbs sit under the inner two columns
        col = {"TL1": 3, "TL0": 4, "TR0": 5, "TR1": 6}[name]
        left = name[1] == "L"
        stagger = (STAGGER_L if left else STAGGER_R)[col if left else col - 5]
        x = col * PITCH + (0 if left else HALF_GAP)
        return x, 3 * PITCH + stagger + 6
    side, row, idx = name[0], "TMB".index(name[1]), int(name[2])
    if side == "L":
        col = 4 - idx
        return col * PITCH, row * PITCH + STAGGER_L[col]
    return 5 * PITCH + HALF_GAP + idx * PITCH, row * PITCH + STAGGER_R[idx]


# ── labels ──────────────────────────────────────────────────────────────────
LAYER_TITLES = {
    "colemak_layer": "Colemak (base)", "querty_layer": "QWERTY", "sym_num_layer": "Symbols / Numbers",
    "nav_layer": "Navigation", "function_layer": "Function", "media_layer": "Media / Bluetooth",
    "gaming_layer": "Gaming", "macro_layer": "Macro",
}
LAYER_ID = {"L_NAV": "Nav", "L_SYM_NUM": "Sym", "L_MEDIA": "Media", "L_FN": "Fn", "L_MACRO": "Macro",
            "L_GAME": "Game", "L_QWERTY": "Qwerty", "L_COLEMAK": "Colemak"}
KP = {
    "SPACE": "␣", "BSPC": "⌫", "BACKSPACE": "⌫", "DEL": "⌦", "TAB": "⇥", "RETURN": "⏎", "ESC": "Esc",
    "UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→", "PG_UP": "PgUp", "PG_DN": "PgDn", "HOME": "Home",
    "END": "End", "INS": "Ins", "CAPS": "Caps", "PSCRN": "PrtSc", "K_CMENU": "Menu", "SQT": "'",
    "COMMA": ",", "DOT": ".", "SLASH": "/", "SEMICOLON": ";", "LSHFT": "Shift", "LSHIFT": "Shift",
    "RSHIFT": "Shift", "LCTRL": "Ctrl", "RCTRL": "Ctrl", "LALT": "Alt", "RALT": "Alt", "LGUI": "Gui",
    "RGUI": "Gui", "K_PP": "⏯", "K_STOP": "⏹", "K_PREV": "⏮", "K_NEXT": "⏭", "K_VOL_UP": "Vol+",
    "K_VOL_DN": "Vol−", "K_MUTE": "Mute", "C_BRI_UP": "Bri+", "C_BRI_DN": "Bri−", "LBRC": "{", "RBRC": "}",
    "LBKT": "[", "RBKT": "]", "LPAR": "(", "RPAR": ")",
    **{f"N{i}": str(i) for i in range(10)},
}
MODS = {"LC": "Ctrl+", "LS": "Shift+", "LA": "Alt+", "LG": "Gui+", "RC": "Ctrl+", "RS": "Shift+"}
MOD_NAMES = {"LGUI": "Gui", "RGUI": "Gui", "LALT": "Alt", "RALT": "Alt", "LCTRL": "Ctrl", "RCTRL": "Ctrl",
             "LSHIFT": "Shift", "RSHIFT": "Shift"}
MC = {"excl": "!", "at": "@", "hash": "#", "dllr": "$", "prcnt": "%", "caret": "^", "amps": "&", "star": "*",
      "qmark": "?", "grave": "`", "dqt": '"', "minus": "-", "plus": "+", "tilde": "~", "pipe": "|",
      "equal": "=", "lt": "<", "gt": ">", "under": "_"}
SHIFT_MORPH = {"comma": (",", ";"), "dot": (".", ":"), "slash": ("/", "\\")}


def kp_label(code):
    if code == "LS(TAB)":
        return "⇤"
    m = re.fullmatch(r"(\w\w)\((.+)\)", code)
    if m and m[1] in MODS:
        return MODS[m[1]] + kp_label(m[2])
    return KP.get(code, code.title() if len(code) > 1 else code)


def hold_label(code):
    m = re.fullmatch(r"(\w\w)\((.+)\)", code)
    if m and m[1] in MODS:
        return MODS[m[1]].rstrip("+") + "+" + hold_label(m[2])
    return MOD_NAMES.get(code, code)


def label(tokens):
    """tokens = ['&hrml', 'LGUI', 'A'] → dict(main, sub, cls)."""
    b, a = tokens[0], tokens[1:]
    if b in ("none", "&none"):
        return dict(main="", sub="", cls="none")
    if b == "trans":
        return dict(main="▽", sub="", cls="trans")
    name = b.lstrip("&")
    if name == "kp":
        return dict(main=kp_label(a[0]), sub="", cls="mod" if a[0] in MOD_NAMES or a[0].endswith("SHIFT") else "key")
    if name in ("hrml", "hrmr"):
        return dict(main=kp_label(a[1]), sub=hold_label(a[0]), cls="hrm")
    if name == "callum_mod":
        return dict(main=hold_label(a[0]), sub="sticky/hold", cls="mod")
    if name == "lt_repeat":
        return dict(main="Repeat", sub=f"hold {LAYER_ID[a[0]]}", cls="layer")
    if name == "mo_sl":
        return dict(main=LAYER_ID[a[0]], sub="sticky/hold", cls="layer")
    if name == "mo_bal":
        return dict(main=kp_label(a[1]), sub=f"hold {LAYER_ID[a[0]]}", cls="layer")
    if name == "magic_shift":
        return dict(main="Shift", sub="sticky/caps", cls="mod")
    if name == "mo":
        return dict(main=LAYER_ID[a[0]], sub="hold", cls="layer")
    if name == "tog":
        return dict(main=LAYER_ID[a[0]], sub="toggle", cls="layer")
    if name.startswith("mc_pwd"):
        return dict(main="pwd", sub=name.removeprefix("mc_pwd_"), cls="sys")
    if name.startswith("mc_"):
        return dict(main=MC.get(name[3:], name[3:]), sub="", cls="key")
    if name.startswith("sh_") and name[3:] in SHIFT_MORPH:
        base, shifted = SHIFT_MORPH[name[3:]]
        return dict(main=base, sub=f"⇧ {shifted}", cls="key")
    if name == "bt":
        return dict(main="BT clr" if a[0] == "BT_CLR" else f"BT {a[1]}", sub="", cls="sys")
    if name == "out":
        return dict(main=a[0].removeprefix("OUT_"), sub="output", cls="sys")
    if name == "bootloader":
        return dict(main="Boot", sub="loader", cls="sys")
    if name == "sys_reset":
        return dict(main="Reset", sub="", cls="sys")
    return dict(main=name, sub=" ".join(a), cls="key")


# ── parsing ─────────────────────────────────────────────────────────────────
def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


HRM_MODS = {"hrml": ["LGUI", "LALT", "LCTRL", "LSHIFT"], "hrmr": ["RSHIFT", "RCTRL", "RALT", "RGUI"]}


def expand(text):
    """Expand the keymap's convenience macros into plain `&behavior args` bindings."""
    def hrm(kind, upper):
        def sub(m):
            keys = [k.strip() for k in m[1].split(",")]
            return " ".join(f"&{kind} {mod} {k}" for mod, k in zip(HRM_MODS[kind], keys))
        return sub
    text = re.sub(r"HRML\(([^)]*)\)", hrm("hrml", True), text)
    text = re.sub(r"HRMR\(([^)]*)\)", hrm("hrmr", True), text)
    text = re.sub(r"\bNK\((\w+)\)", r"&callum_mod \1 \1", text)
    text = re.sub(r"\bLT_REPEAT\((\w+)\)", r"&lt_repeat \1 0", text)
    text = re.sub(r"\bMO_SL\((\w+)\)", r"&mo_sl \1 \1", text)
    text = re.sub(r"\bMO_MACRO\((\w+)\)", r"&mo_bal L_MACRO \1", text)
    text = text.replace("MAGIC_SHIFT", "&magic_shift LSHFT 0")
    return text


def split_bindings(text):
    out = []
    for tok in re.findall(r"&?\w+(?:\([^)]*\))?", text):
        if tok.startswith("&"):
            out.append([tok])
        elif tok in ("XXX", "___"):
            out.append(["none" if tok == "XXX" else "trans"])
        else:
            out[-1].append(tok)
    return out


def parse_layers():
    text = strip_comments(KEYMAP.read_text())
    layers = []
    for name, body in re.findall(r"(\w+_layer)\s*\{\s*bindings\s*=\s*<(.*?)>;", text, flags=re.S):
        bindings = split_bindings(expand(body))
        assert len(bindings) == len(NAMES), f"{name}: {len(bindings)} bindings, expected {len(NAMES)}"
        layers.append((name, dict(zip(NAMES, map(label, bindings)))))
    return layers


def split_top(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return parts + [cur.strip()]


def parse_combos():
    text = strip_comments(COMBOS.read_text())
    combos = []
    for m in re.finditer(r"^\s*COMBO\((.*)\)\s*$", text, flags=re.M):
        name, binding, keys, layers, *_ = split_top(m[1])
        combos.append(dict(name=name, binding=label(binding.split()), keys=keys.split(), layers=layers.split()))
    return combos


# ── drawing ─────────────────────────────────────────────────────────────────
def font_size(text):
    n = len(text)
    return 17 if n <= 1 else 14 if n <= 3 else 11 if n <= 5 else 9


def draw_key(name, lab, ox, oy):
    x, y = key_xy(name)
    x, y = ox + x, oy + y
    cls = lab["cls"]
    s = f'<rect class="k {cls}" x="{x}" y="{y}" width="{KEY}" height="{KEY}" rx="7"/>'
    if lab["main"]:
        dy = -3 if lab["sub"] else 5
        s += (f'<text class="t" x="{x + KEY / 2}" y="{y + KEY / 2 + dy}" text-anchor="middle" '
              f'font-size="{font_size(lab["main"])}">{escape(lab["main"])}</text>')
    if lab["sub"]:
        size = 8 if len(lab["sub"]) <= 9 else 6.5
        s += (f'<text class="m" x="{x + KEY / 2}" y="{y + KEY - 8}" text-anchor="middle" '
              f'font-size="{size}">{escape(lab["sub"])}</text>')
    return s


def draw_panel(title, keys, ox, oy):
    s = f'<text class="h" x="{ox}" y="{oy - 10}">{escape(title)}</text>'
    return s + "".join(draw_key(n, keys[n], ox, oy) for n in NAMES)


def chip(x, y, text, w=26):
    return (f'<rect class="k" x="{x}" y="{y}" width="{w}" height="20" rx="5"/>'
            f'<text class="t" x="{x + w / 2}" y="{y + 14}" text-anchor="middle" font-size="{11 if len(text) < 4 else 8}">'
            f'{escape(text[:5])}</text>')


def draw_combo_table(combos, layers, ox, oy, width, cols=3):
    """One row per combo: key chips (letters of the layer it fires on) → resulting action."""
    s = f'<text class="h" x="{ox}" y="{oy - 10}">Combos</text>'
    col_w, row_h = width / cols, 28
    per_col = -(-len(combos) // cols)
    for i, c in enumerate(combos):
        x, y = ox + (i // per_col) * col_w, oy + (i % per_col) * row_h
        layer = layers["gaming_layer"] if c["layers"] == ["L_GAME"] else layers["colemak_layer"]
        for k in c["keys"]:
            s += chip(x, y, layer[k]["main"])
            x += 30
        text = (c["binding"]["main"] or "none").replace("⏎", "Enter")
        if c["binding"]["cls"] == "hrm":
            text += f' (hold {c["binding"]["sub"]})'
        tag = "" if c["layers"] == ["TYPING"] else f'[{LAYER_ID.get(c["layers"][0], c["layers"][0])}] '
        s += (f'<text class="m" x="{x}" y="{y + 14}" font-size="11">→</text>'
              f'<text class="t" x="{x + 16}" y="{y + 14}" font-size="11">{escape(tag + text)}</text>')
    return s


LIGHT = dict(bg="#ffffff", key="#f3f4f6", line="#d1d5db", text="#111827", muted="#6b7280", mod="#dbeafe",
             layer="#fef3c7", sys="#fee2e2", pill="#bbf7d0", accent="#2563eb")
DARK = dict(bg="#0d1117", key="#1c232d", line="#394352", text="#e5e7eb", muted="#9ca3af", mod="#1e3a5f",
            layer="#4a3a12", sys="#4a1d24", pill="#14532d", accent="#60a5fa")


def css(c):
    """Plain per-theme rules (no CSS variables: librsvg and some viewers ignore them)."""
    return (
        f".bg{{fill:{c['bg']}}}.k{{fill:{c['key']};stroke:{c['line']};stroke-width:1}}"
        f".k.mod{{fill:{c['mod']}}}.k.layer{{fill:{c['layer']}}}.k.sys{{fill:{c['sys']}}}"
        f".k.none{{fill:none;stroke-dasharray:2 3}}.k.trans{{fill:none;stroke-dasharray:4 3}}"
        f".k.ghost{{fill:none}}.t{{fill:{c['text']}}}.m,.note,.ghost+text{{fill:{c['muted']}}}"
        f".h{{fill:{c['text']}}}.cl{{stroke:{c['accent']}}}.pill{{fill:{c['pill']};stroke:{c['accent']}}}"
    )


STYLE = (
    "text{font-family:'JetBrains Mono','DejaVu Sans Mono',monospace}.h{font-size:15px;font-weight:700}"
    ".note{font-size:11px}.cl{stroke-width:1.5;opacity:.55}.pill{stroke-width:1}"
    + css(LIGHT) + "@media (prefers-color-scheme:dark){" + css(DARK) + "}"
)


def main():
    layers = parse_layers()
    combos = parse_combos()
    base = dict(layers)["colemak_layer"]
    cols, panel_gap = 2, 48
    width = MARGIN * 2 + cols * PANEL_W + (cols - 1) * panel_gap
    panels = [(LAYER_TITLES.get(n, n), k) for n, k in layers]
    rows = -(-len(panels) // cols)
    row_h = PANEL_H + 40
    height = MARGIN * 2 + rows * row_h + 24 + 16 + 7 * 28 + 30
    body = []
    for i, (title, keys) in enumerate(panels):
        ox = MARGIN + (i % cols) * (PANEL_W + panel_gap)
        oy = MARGIN + 24 + (i // cols) * row_h
        body.append(draw_panel(title, keys, ox, oy))
    combos = [c for c in combos if c["binding"]["cls"] != "none"]
    ty = MARGIN + 24 + rows * row_h + 16
    body.append(draw_combo_table(combos, dict(layers), MARGIN, ty, width - 2 * MARGIN))
    legend = ("Blue: modifier · Amber: layer · Red: system/BT/secret · Small caption = hold action (tap = big label) "
              "· Combos list the base-layer letters · Generated by scripts/draw_keymap.py")
    body.append(f'<text class="note" x="{MARGIN}" y="{height - 12}">{escape(legend)}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
           f'<style>{STYLE}</style><rect class="bg" width="100%" height="100%"/>' + "".join(body) + "</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(layers)} layers, {len(combos)} combos)")


if __name__ == "__main__":
    main()
