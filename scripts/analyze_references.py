#!/usr/bin/env python3
"""
Extrai cores dominantes de imagens de referência via k-means simples sobre os pixels.
Útil quando o aluno não tem identidade visual e enviou prints/anúncios que gosta.

Uso:
  python3 scripts/analyze_references.py --dir brand/references/ --output /tmp/palette.json
  python3 scripts/analyze_references.py --files img1.jpg img2.png --top 5

A ideia não é substituir o olho do Claude (que vê as imagens via multimodal direto),
e sim oferecer um número confiável das 5 cores dominantes pra ajudar a sugerir uma cor primária.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image
except ImportError:
    print("ERRO: Pillow não instalado. Roda: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def quantize_pixel(r: int, g: int, b: int, bins: int = 32) -> Tuple[int, int, int]:
    """Reduz precisão de cor para agrupar pixels parecidos.
    bins=32 → cores se agrupam em buckets de 8 (256/32) pra cada canal.
    """
    bucket = 256 // bins
    return (
        (r // bucket) * bucket + bucket // 2,
        (g // bucket) * bucket + bucket // 2,
        (b // bucket) * bucket + bucket // 2,
    )


def is_grayscale(r: int, g: int, b: int, threshold: int = 12) -> bool:
    """Considera grayscale se os 3 canais variam menos que threshold."""
    return abs(r - g) < threshold and abs(g - b) < threshold and abs(r - b) < threshold


def is_extreme(r: int, g: int, b: int, dark: int = 30, light: int = 235) -> bool:
    """Filtra pretos absolutos e brancos absolutos (geralmente fundo, não cor de marca)."""
    avg = (r + g + b) / 3
    return avg < dark or avg > light


def extract_dominant_colors(image_path: Path, top_n: int = 5,
                            ignore_grayscale: bool = True,
                            ignore_extremes: bool = True,
                            sample_size: int = 50_000) -> List[dict]:
    """Extrai as top_n cores dominantes da imagem.
    Retorna lista ordenada por frequência: [{ "hex": "#...", "count": N, "ratio": 0.XX }, ...]
    """
    img = Image.open(image_path).convert("RGB")

    # Reduz pra ficar rápido em imagens grandes
    img.thumbnail((400, 400))

    pixels = list(img.getdata())

    # Amostragem pra evitar processar milhões de pixels em imagens grandes
    if len(pixels) > sample_size:
        step = len(pixels) // sample_size
        pixels = pixels[::step]

    # Quantiza, filtra e conta
    counter: Counter = Counter()
    for r, g, b in pixels:
        if ignore_extremes and is_extreme(r, g, b):
            continue
        if ignore_grayscale and is_grayscale(r, g, b):
            continue
        counter[quantize_pixel(r, g, b)] += 1

    if not counter:
        return []

    total = sum(counter.values())
    dominant = counter.most_common(top_n)

    result = []
    for (r, g, b), count in dominant:
        result.append({
            "hex": "#{:02X}{:02X}{:02X}".format(r, g, b),
            "count": count,
            "ratio": round(count / total, 3),
        })

    return result


def collect_image_files(dir_path: Path | None, file_paths: List[str] | None) -> List[Path]:
    """Coleta lista de imagens de --dir ou --files."""
    files: List[Path] = []
    if file_paths:
        files.extend(Path(f) for f in file_paths)
    if dir_path:
        if not dir_path.is_dir():
            print(f"ERRO: diretório {dir_path} não existe", file=sys.stderr)
            sys.exit(1)
        for p in sorted(dir_path.iterdir()):
            if p.suffix.lower() in SUPPORTED_EXTS:
                files.append(p)

    valid = [f for f in files if f.exists() and f.suffix.lower() in SUPPORTED_EXTS]
    if not valid:
        print("ERRO: nenhuma imagem válida encontrada", file=sys.stderr)
        sys.exit(1)
    return valid


def main():
    parser = argparse.ArgumentParser(description="Analisa imagens de referência e extrai paleta dominante")
    parser.add_argument("--dir", help="Diretório com imagens (analisa todas)")
    parser.add_argument("--files", nargs="+", help="Caminhos individuais")
    parser.add_argument("--top", type=int, default=5, help="Top N cores por imagem")
    parser.add_argument("--output", help="Salva resultado em JSON (default: stdout)")
    parser.add_argument("--include-grayscale", action="store_true",
                        help="Inclui pretos/brancos/cinzas (default: ignora)")
    args = parser.parse_args()

    if not args.dir and not args.files:
        parser.error("--dir ou --files é obrigatório")

    files = collect_image_files(Path(args.dir) if args.dir else None, args.files)

    results = {}
    aggregate: Counter = Counter()

    for f in files:
        try:
            colors = extract_dominant_colors(
                f,
                top_n=args.top,
                ignore_grayscale=not args.include_grayscale,
            )
            results[str(f)] = colors
            for c in colors:
                aggregate[c["hex"]] += c["count"]
        except Exception as e:
            print(f"AVISO: falha ao analisar {f}: {e}", file=sys.stderr)
            results[str(f)] = []

    # Cores agregadas (entre todas as imagens)
    aggregate_total = sum(aggregate.values()) or 1
    aggregate_top = [
        {"hex": hex_val, "count": count, "ratio": round(count / aggregate_total, 3)}
        for hex_val, count in aggregate.most_common(args.top * 2)
    ]

    output = {
        "per_image": results,
        "aggregate": aggregate_top,
        "suggestion": {
            "primary_color": aggregate_top[0]["hex"] if aggregate_top else None,
            "rationale": "Cor dominante agregada entre as referências, ignorando pretos/brancos/cinzas (que geralmente são fundo).",
        },
    }

    payload = json.dumps(output, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"OK: análise salva em {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
