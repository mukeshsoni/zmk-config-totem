#!/usr/bin/env python3

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KEYMAP_PATH = ROOT / "config" / "totem.keymap"
COMBOS_PATH = ROOT / "config" / "combos.dtsi"
OUTPUT_PATH = ROOT / "totem-layout-reference.txt"

LAYER_SPECS = [
    ("default_layer", "BASE (default, Colemak-DHm)"),
    ("nav_layer", "NAV"),
    ("sym_layer", "SYM"),
    ("num_layer", "NUM"),
    ("fun_layer", "FUN"),
    ("util_layer", "UTIL"),
]

POSITION_ORDER = [
    "LT4",
    "LT3",
    "LT2",
    "LT1",
    "LT0",
    "RT0",
    "RT1",
    "RT2",
    "RT3",
    "RT4",
    "LM4",
    "LM3",
    "LM2",
    "LM1",
    "LM0",
    "RM0",
    "RM1",
    "RM2",
    "RM3",
    "RM4",
    "LB5",
    "LB4",
    "LB3",
    "LB2",
    "LB1",
    "LB0",
    "RB0",
    "RB1",
    "RB2",
    "RB3",
    "RB4",
    "RB5",
    "LH2",
    "LH1",
    "LH0",
    "RH0",
    "RH1",
    "RH2",
]

BEHAVIOR_ARG_COUNTS = {
    "&kp": 1,
    "&hml": 2,
    "&hmr": 2,
    "&hmr_meh": 2,
    "&lt": 2,
    "&sk": 1,
    "&bt": 2,
}

KEY_LABELS = {
    "TAB": "Tab",
    "ESC": "Esc",
    "SPACE": "Spc",
    "RET": "Ent",
    "BSPC": "Bsp",
    "DEL": "Del",
    "HOME": "Home",
    "END": "End",
    "UP": "Up",
    "DOWN": "Down",
    "LEFT": "Left",
    "RIGHT": "Right",
    "PAGE_UP": "PgUp",
    "PAGE_DOWN": "PgDn",
    "LCTRL": "Ctrl",
    "RCTRL": "Ctrl",
    "LALT": "Alt",
    "RALT": "Alt",
    "LGUI": "Gui",
    "RGUI": "Gui",
    "LSHFT": "Shft",
    "RSHFT": "Shft",
    "SEMI": ";",
    "COMMA": ",",
    "DOT": ".",
    "QMARK": "?",
    "EXCL": "!",
    "AT": "@",
    "HASH": "#",
    "DLLR": "$",
    "PRCNT": "%",
    "CARET": "^",
    "AMPS": "&",
    "STAR": "*",
    "SQT": "'",
    "DQT": '"',
    "PIPE": "|",
    "MINUS": "-",
    "UNDER": "_",
    "EQUAL": "=",
    "PLUS": "+",
    "BSLH": "\\",
    "FSLH": "/",
    "LBRC": "{",
    "RBRC": "}",
    "LBKT": "[",
    "RBKT": "]",
    "LPAR": "(",
    "RPAR": ")",
    "LT": "<",
    "GT": ">",
    "TILDE": "~",
    "GRAVE": "`",
    "MEH": "Meh",
    "HYP": "Hyp",
    "C_MUTE": "Mute",
    "C_VOL_UP": "Vol+",
    "C_VOL_DN": "Vol-",
    "C_NEXT": "Next",
    "C_PP": "Play/P",
    "LG(X)": "Cut",
    "LG(C)": "Copy",
    "LG(V)": "Paste",
}


@dataclass
class Combo:
    output: str
    positions: list[str]
    layers: str
    term: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_line_comments(text: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


def split_tokens(bindings_blob: str) -> list[str]:
    no_comments = strip_line_comments(bindings_blob)
    return re.findall(r"\S+", no_comments)


def normalize_keycode(code: str) -> str:
    if re.fullmatch(r"N[0-9]", code):
        return code[1:]
    if re.fullmatch(r"F[0-9]{1,2}", code):
        return code
    if re.fullmatch(r"[A-Z]", code):
        return code
    return KEY_LABELS.get(code, code)


def parse_binding_groups(tokens: list[str], expected: int = 38) -> list[list[str]]:
    groups: list[list[str]] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("&"):
            if token == "&bt":
                if i + 1 >= len(tokens):
                    raise ValueError("Incomplete &bt binding")
                argc = 2 if tokens[i + 1] == "BT_SEL" else 1
            else:
                argc = BEHAVIOR_ARG_COUNTS.get(token, 0)
            group = tokens[i : i + 1 + argc]
            i += 1 + argc
        else:
            group = [token]
            i += 1
        groups.append(group)

    if len(groups) != expected:
        raise ValueError(f"Expected {expected} bindings, got {len(groups)}")

    return groups


def extract_layer_bindings(keymap_text: str, layer_name: str) -> list[list[str]]:
    start = keymap_text.find(f"{layer_name} {{")
    if start == -1:
        raise ValueError(f"Layer '{layer_name}' not found")

    bindings_start = keymap_text.find("bindings = <", start)
    if bindings_start == -1:
        raise ValueError(f"Layer '{layer_name}' does not contain bindings")

    content_start = bindings_start + len("bindings = <")
    content_end = keymap_text.find(">;", content_start)
    if content_end == -1:
        raise ValueError(f"Layer '{layer_name}' bindings are not terminated")

    blob = keymap_text[content_start:content_end]
    return parse_binding_groups(split_tokens(blob))


def render_binding(group: list[str]) -> str:
    head = group[0]

    if head in {"___", "&trans"}:
        return "TRNS"

    if head == "BACK":
        return "Back"
    if head == "FWD":
        return "Fwd"
    if head == "&dot_morph":
        return "./:"
    if head == "&qexcl":
        return "?/!"
    if head == "&comma_morph":
        return ",/;"
    if head == "&sleep_hyper_z":
        return "Sleep"

    if head == "&kp":
        return normalize_keycode(group[1])

    if head in {"&hml", "&hmr"}:
        hold = normalize_keycode(group[1])
        tap = normalize_keycode(group[2])
        return f"{tap}/{hold}"

    if head == "&hmr_meh":
        return ",/;/Meh"

    if head == "&lt":
        layer = group[1]
        tap = normalize_keycode(group[2])
        return f"{tap}/{layer}"

    if head == "&sk":
        key = normalize_keycode(group[1])
        if key == "Shft":
            return "OShft"
        return f"OS-{key}"

    if head == "&bt":
        if group[1] == "BT_SEL":
            return f"BT{group[2]}"
        if group[1] == "BT_CLR":
            return "BTCLR"
        return " ".join(group[1:])

    if head.startswith("&"):
        return head[1:]

    return head


def combo_output_label(binding_expr: str) -> str:
    binding_expr = binding_expr.strip()
    if binding_expr.startswith("&kp "):
        return normalize_keycode(binding_expr[4:].strip())
    if binding_expr == "&caps_word":
        return "Caps Word"
    return binding_expr.removeprefix("&")


def parse_macro_calls(text: str, macro_name: str) -> list[str]:
    calls: list[str] = []
    marker = f"{macro_name}("
    i = 0
    while True:
        start = text.find(marker, i)
        if start == -1:
            break
        cursor = start + len(marker)
        depth = 1
        while cursor < len(text) and depth > 0:
            ch = text[cursor]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            cursor += 1
        calls.append(text[start + len(marker) : cursor - 1])
        i = cursor
    return calls


def split_macro_args(arg_blob: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in arg_blob:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1

        if ch == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue

        current.append(ch)

    last = "".join(current).strip()
    if last:
        args.append(last)
    return args


def parse_combos(combos_text: str) -> tuple[list[Combo], str, str, str]:
    fast_match = re.search(r"#define\s+COMBO_TERM_FAST\s+(\d+)", combos_text)
    slow_match = re.search(r"#define\s+COMBO_TERM_SLOW\s+(\d+)", combos_text)
    idle_match = re.search(r"require-prior-idle-ms\s*=\s*<(\d+)>", combos_text)

    fast_term = fast_match.group(1) if fast_match else "?"
    slow_term = slow_match.group(1) if slow_match else "?"
    idle = idle_match.group(1) if idle_match else "?"

    no_comments = strip_line_comments(combos_text)
    combos: list[Combo] = []
    for call in parse_macro_calls(no_comments, "ZMK_COMBO"):
        args = split_macro_args(call)
        if len(args) != 5:
            continue
        binding_expr = args[1]
        positions = args[2].split()
        layers = " ".join(args[3].split())
        term = args[4].strip()
        combos.append(
            Combo(
                output=combo_output_label(binding_expr),
                positions=positions,
                layers=layers,
                term=term,
            )
        )

    return combos, fast_term, slow_term, idle


def tap_key_from_binding(group: list[str]) -> str:
    head = group[0]
    if head == "&kp":
        return normalize_keycode(group[1])
    if head in {"&hml", "&hmr"}:
        return normalize_keycode(group[2])
    if head == "&hmr_meh":
        return ","
    if head == "&dot_morph":
        return "."
    if head == "&qexcl":
        return "?"
    if head == "&comma_morph":
        return ","
    if head == "___" or head == "&trans":
        return "TRNS"
    if head == "BACK":
        return "Back"
    if head == "FWD":
        return "Fwd"
    return render_binding(group)


def format_row(labels: list[str], width: int) -> str:
    return " ".join(f"[ {label:<{width}} ]" for label in labels)


def classify_combo(positions: list[str]) -> str:
    sides = {
        "L" if p.startswith("L") else "R" if p.startswith("R") else "X"
        for p in positions
    }
    if len(sides) > 1:
        return "Cross-hand combos"

    side = "Left" if "L" in sides else "Right"
    rows = {p[1] for p in positions if len(p) > 1}
    is_vertical = rows in ({"T", "M"}, {"M", "B"})
    direction = "vertical" if is_vertical else "horizontal"
    return f"{side} hand {direction} combos"


def render_layout_section(title: str, labels: list[str], width: int) -> list[str]:
    gap = " " * 27
    lines = [title, "-" * len(title)]
    lines.append(format_row(labels[0:5], width) + gap + format_row(labels[5:10], width))
    lines.append(
        format_row(labels[10:15], width) + gap + format_row(labels[15:20], width)
    )
    lines.append(
        format_row(labels[20:26], width) + "       " + format_row(labels[26:32], width)
    )
    lines.append(
        " " * 13
        + format_row(labels[32:35], width)
        + gap
        + format_row(labels[35:38], width)
    )
    return lines


def generate() -> str:
    keymap_text = read_text(KEYMAP_PATH)
    combos_text = read_text(COMBOS_PATH)

    layer_labels: dict[str, list[str]] = {}
    all_labels: list[str] = []
    for layer_name, _ in LAYER_SPECS:
        groups = extract_layer_bindings(keymap_text, layer_name)
        labels = [render_binding(group) for group in groups]
        layer_labels[layer_name] = labels
        all_labels.extend(labels)

    width = max(4, min(10, max(len(label) for label in all_labels)))

    base_groups = extract_layer_bindings(keymap_text, "default_layer")
    base_position_map = {
        pos: tap_key_from_binding(group)
        for pos, group in zip(POSITION_ORDER, base_groups)
    }

    combos, fast_term, slow_term, idle = parse_combos(combos_text)
    categories = {
        "Left hand vertical combos": [],
        "Left hand horizontal combos": [],
        "Right hand vertical combos": [],
        "Right hand horizontal combos": [],
        "Cross-hand combos": [],
    }

    active_layers = ""
    for combo in combos:
        if not active_layers:
            active_layers = combo.layers.replace(" ", ", ")

        keys = [base_position_map.get(pos, pos) for pos in combo.positions]
        description = f"- {keys[0]} + {keys[1]} -> {combo.output}"

        category = classify_combo(combo.positions)
        categories.setdefault(category, []).append(description)

    out: list[str] = [
        "TOTEM KEYBOARD REFERENCE (PRINTABLE)",
        "===================================",
        "",
        "Source files:",
        "- config/totem.keymap",
        "- config/combos.dtsi",
        "",
        "Board shape: 5 + 5 columns, 3 rows, 3 thumb keys per side (38 keys total)",
        "Legend: TRNS=transparent, OShft=one-shot shift, X/Y=tap/hold behavior",
        "",
    ]

    for idx, (layer_name, title) in enumerate(LAYER_SPECS):
        out.extend(render_layout_section(title, layer_labels[layer_name], width))
        if idx != len(LAYER_SPECS) - 1:
            out.append("")
            out.append("")

    out.extend(
        [
            "",
            "",
            f"COMBOS (active on {active_layers})",
            "-" * (20 + len(active_layers)),
            "Timing:",
            f"- FAST combo term: {fast_term} ms",
            f"- SLOW combo term: {slow_term} ms",
            f"- require-prior-idle-ms: {idle}",
            "",
        ]
    )

    for heading in [
        "Left hand vertical combos",
        "Left hand horizontal combos",
        "Right hand vertical combos",
        "Right hand horizontal combos",
        "Cross-hand combos",
    ]:
        items = categories.get(heading, [])
        if not items:
            continue
        out.append(f"{heading}:")
        out.extend(items)
        out.append("")

    while out and out[-1] == "":
        out.pop()

    return "\n".join(out) + "\n"


def main() -> None:
    OUTPUT_PATH.write_text(generate(), encoding="utf-8")


if __name__ == "__main__":
    main()
