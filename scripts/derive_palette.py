#!/usr/bin/env python3
"""
Deriva a paleta completa de 6 tokens a partir de uma cor primária.

Tokens gerados (seguem o prompt-base do projeto):
  BRAND_PRIMARY   = cor do usuário
  BRAND_LIGHT     = primary com lightness +20%
  BRAND_DARK      = primary com lightness -30%
  LIGHT_BG        = off-white tintado (warm/cool conforme primary)
  LIGHT_BORDER    = LIGHT_BG -5% lightness
  DARK_BG         = near-black tintado
  BRAND_GRADIENT  = linear-gradient(165deg, DARK 0%, PRIMARY 50%, LIGHT 100%)

Uso:
  python3 scripts/derive_palette.py --primary "#6366f1"
  python3 scripts/derive_palette.py --primary "#6366f1" --output brand/brand-kit.json --append
  python3 scripts/derive_palette.py --validate brand/brand-kit.json
"""

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """Converte #RRGGBB para tupla RGB normalizada (0-1)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        raise ValueError(f"Hex inválido: {hex_color}")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return r, g, b


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """Converte RGB normalizado (0-1) para #RRGGBB."""
    r = max(0, min(1, r))
    g = max(0, min(1, g))
    b = max(0, min(1, b))
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def adjust_lightness(hex_color: str, delta: float) -> str:
    """Ajusta a lightness (HLS) por um delta (-1 a 1)."""
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.02, min(0.98, l + delta))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(r, g, b)


def is_warm(hex_color: str) -> bool:
    """Verifica se a cor é warm (vermelho/laranja/amarelo) ou cool (azul/verde/roxo)."""
    r, g, b = hex_to_rgb(hex_color)
    h, _, _ = colorsys.rgb_to_hls(r, g, b)
    # Hue: 0=red, 1/6=yellow, 2/6=green, 3/6=cyan, 4/6=blue, 5/6=magenta
    # Warm: hue 0–1/6 (red-yellow) ou 5/6–1 (magenta-red)
    return h < 1 / 6 or h > 5 / 6


def derive_tokens(primary_hex: str) -> dict:
    """Gera os 6 tokens + gradient a partir de 1 cor primária."""
    if not re.match(r"^#?[0-9A-Fa-f]{3,6}$", primary_hex.strip()):
        raise ValueError(f"Cor primária inválida: {primary_hex}")

    primary = primary_hex if primary_hex.startswith("#") else f"#{primary_hex}"
    primary = primary.upper()

    light = adjust_lightness(primary, +0.20)
    dark = adjust_lightness(primary, -0.30)

    # LIGHT_BG: off-white tintado com a temperatura da primária
    if is_warm(primary):
        light_bg = "#FAF9F7"  # cream warm
        dark_bg = "#1A1918"  # near-black warm
    else:
        light_bg = "#F8F9FB"  # gray-white cool
        dark_bg = "#0F172A"  # near-black cool

    # LIGHT_BORDER: ~1 sombra mais escura que LIGHT_BG
    light_border = adjust_lightness(light_bg, -0.05)

    gradient = f"linear-gradient(165deg, {dark} 0%, {primary} 50%, {light} 100%)"

    return {
        "BRAND_PRIMARY": primary,
        "BRAND_LIGHT": light,
        "BRAND_DARK": dark,
        "LIGHT_BG": light_bg,
        "LIGHT_BORDER": light_border,
        "DARK_BG": dark_bg,
        "BRAND_GRADIENT": gradient,
    }


def validate_brand_kit(path: Path) -> bool:
    """Valida estrutura mínima do brand-kit.json."""
    if not path.exists():
        print(f"ERRO: arquivo {path} não existe", file=sys.stderr)
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERRO: JSON inválido em {path}: {e}", file=sys.stderr)
        return False

    # tokens é o único realmente obrigatório pra renderizar.
    # name/primary_color/handle/fontes são esperados num brand-kit "completo",
    # mas o arquivo pode estar parcial (ex: gerado isoladamente pelo derive_palette).
    if "tokens" not in data:
        print(f"ERRO: campo obrigatório 'tokens' faltando em {path}", file=sys.stderr)
        return False

    optional_fields = ["name", "primary_color", "handle", "heading_font", "body_font"]
    missing_optional = [f for f in optional_fields if f not in data]
    if missing_optional:
        print(f"AVISO: brand-kit parcial — campos esperados faltando: {missing_optional}", file=sys.stderr)

    required_tokens = ["BRAND_PRIMARY", "BRAND_LIGHT", "BRAND_DARK", "LIGHT_BG", "LIGHT_BORDER", "DARK_BG"]
    for t in required_tokens:
        if t not in data["tokens"]:
            print(f"ERRO: token '{t}' faltando em tokens", file=sys.stderr)
            return False
        val = data["tokens"][t]
        if not re.match(r"^#[0-9A-Fa-f]{6}$", val):
            print(f"ERRO: token '{t}' tem hex inválido: {val}", file=sys.stderr)
            return False

    print(f"OK: {path} válido")
    return True


def main():
    parser = argparse.ArgumentParser(description="Deriva paleta a partir de cor primária")
    parser.add_argument("--primary", help="Cor primária em hex (#RRGGBB)")
    parser.add_argument("--output", help="Caminho do brand-kit.json a salvar")
    parser.add_argument("--append", action="store_true",
                        help="Mescla tokens em brand-kit.json existente (preserva outros campos)")
    parser.add_argument("--validate", help="Valida um brand-kit.json existente")
    args = parser.parse_args()

    if args.validate:
        ok = validate_brand_kit(Path(args.validate))
        sys.exit(0 if ok else 1)

    if not args.primary:
        parser.error("--primary é obrigatório (ou use --validate)")

    tokens = derive_tokens(args.primary)

    if not args.output:
        # Apenas imprime no stdout
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.append and output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        existing["primary_color"] = tokens["BRAND_PRIMARY"]
        existing["tokens"] = tokens
        output_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        # Cria novo brand-kit mínimo
        data = {
            "primary_color": tokens["BRAND_PRIMARY"],
            "tokens": tokens,
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"OK: paleta salva em {output_path}")


if __name__ == "__main__":
    main()
