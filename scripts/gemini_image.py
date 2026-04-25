#!/usr/bin/env python3
"""
Gera imagem via Gemini 2.5 Flash Image (Nano Banana).

Uso:
  python3 scripts/gemini_image.py \\
    --prompt "professional in modern office, soft natural light" \\
    --aspect 4x5 \\
    --output assets/gerada-1.png

Aspect ratios suportados: 1x1, 4x5, 9x16, 16x9
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERRO: python-dotenv não instalado. Roda: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERRO: google-genai não instalado. Roda: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
# override=True garante que a chave do .env tenha prioridade sobre variáveis
# que possam estar no ambiente (ex: GEMINI_API_KEY de Cloud Workstation, gcloud, etc)
load_dotenv(PROJECT_ROOT / ".env", override=True)


ASPECT_HINTS = {
    "1x1": "square aspect ratio, 1:1 composition",
    "4x5": "vertical 4:5 aspect ratio, portrait composition",
    "9x16": "vertical 9:16 aspect ratio, full-height portrait composition",
    "16x9": "horizontal 16:9 aspect ratio, wide landscape composition",
}


def build_image_prompt(prompt: str, aspect: str, style: str | None) -> str:
    """Constrói o prompt final pra Gemini Image."""
    parts = [prompt]
    if style:
        parts.append(f"Style: {style}")
    parts.append(ASPECT_HINTS.get(aspect, ASPECT_HINTS["4x5"]))
    parts.append("high quality, professional photography, no text, no watermark, no logo")
    return ". ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Gera imagem via Gemini Image")
    parser.add_argument("--prompt", required=True, help="Descrição da imagem (em inglês funciona melhor)")
    parser.add_argument("--aspect", choices=list(ASPECT_HINTS.keys()), default="4x5", help="Aspect ratio")
    parser.add_argument("--style", help="Estilo (ex: 'editorial photography', 'flat illustration')")
    parser.add_argument("--output", required=True, help="Caminho de saída (.png ou .jpg)")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: GEMINI_API_KEY not set. Verifique .env na raiz do projeto.", file=sys.stderr)
        sys.exit(2)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    full_prompt = build_image_prompt(args.prompt, args.aspect, args.style)

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

    try:
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
        )
    except Exception as e:
        msg = str(e)
        if "401" in msg or "403" in msg:
            print("ERRO: chave Gemini inválida ou sem acesso ao modelo de imagem.", file=sys.stderr)
            sys.exit(3)
        if "429" in msg:
            print("ERRO: cota Gemini esgotada. Espera 24h ou aumenta limite no AI Studio.", file=sys.stderr)
            sys.exit(4)
        if "INVALID_ARGUMENT" in msg or "400" in msg:
            print("ERRO: prompt rejeitado pelo safety filter. Reescreva mais neutro (sem nomes próprios, sem contexto sensível).", file=sys.stderr)
            sys.exit(5)
        print(f"ERRO: {msg}", file=sys.stderr)
        sys.exit(1)

    # Extrai a imagem da resposta — vem em parts[].inline_data.data (bytes)
    image_bytes = None
    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                image_bytes = inline.data
                break
        if image_bytes:
            break

    if not image_bytes:
        print("ERRO: Gemini não retornou imagem. Verifique o prompt.", file=sys.stderr)
        sys.exit(6)

    # data já vem como bytes pelo SDK novo
    if isinstance(image_bytes, str):
        import base64
        image_bytes = base64.b64decode(image_bytes)

    output_path.write_bytes(image_bytes)
    print(f"OK: imagem salva em {output_path}")


if __name__ == "__main__":
    main()
