#!/usr/bin/env python3
"""
Renderiza HTML de criativo (estático ou carrossel) em PNG 1080×N usando Playwright.

Mantém o layout em 420px (igual ao prompt-base) e usa device_scale_factor=2.5714 pra
escalar pra 1080px sem reflowar a layout.

Uso:
  # Estático (1 imagem só)
  python3 scripts/render_slides.py \\
    --template templates/static-4x5.html \\
    --brand brand/brand-kit.json \\
    --copy /tmp/copy-estatico.json \\
    --variant 1 \\
    --image assets/foto.jpg \\
    --output output/estatico-{ts}.png

  # Carrossel (várias imagens + zip)
  python3 scripts/render_slides.py \\
    --template templates/carousel-base.html \\
    --brand brand/brand-kit.json \\
    --copy /tmp/copy-carrossel.json \\
    --images /tmp/carrossel-images.json \\
    --output-dir output/carrossel-{ts}/ \\
    --zip
"""

import argparse
import base64
import json
import mimetypes
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERRO: Playwright não instalado. Roda: pip install -r scripts/requirements.txt && playwright install chromium", file=sys.stderr)
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Layout fixo (vem do prompt-base — não mudar)
VIEW_W = 420
SLIDE_HEIGHT_BY_FORMAT = {
    "carousel": 525,   # 4:5
    "static-1x1": 420,  # 1:1
    "static-4x5": 525,  # 4:5
    "static-9x16": 747,  # 9:16
}
TARGET_W = 1080  # output Instagram
SCALE = TARGET_W / VIEW_W  # ≈ 2.5714


# ---------- Utils ----------

def encode_image_base64(path: Path) -> str:
    """Lê imagem e retorna data URI base64 (com mime correto)."""
    if not path.exists():
        raise FileNotFoundError(f"Imagem não existe: {path}")

    mime, _ = mimetypes.guess_type(str(path))
    if not mime or not mime.startswith("image/"):
        # Fallback: detecta pelo header
        header = path.read_bytes()[:12]
        if header.startswith(b"\xff\xd8"):
            mime = "image/jpeg"
        elif header.startswith(b"\x89PNG"):
            mime = "image/png"
        elif header[:6] in (b"GIF87a", b"GIF89a"):
            mime = "image/gif"
        elif header[8:12] == b"WEBP":
            mime = "image/webp"
        else:
            mime = "image/png"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def detect_format(template_path: Path) -> str:
    """Detecta formato pelo nome do template."""
    name = template_path.stem
    if "carousel" in name:
        return "carousel"
    if "1x1" in name:
        return "static-1x1"
    if "9x16" in name:
        return "static-9x16"
    return "static-4x5"


def replace_placeholders(html: str, mapping: dict) -> str:
    """Substitui {{KEY}} → value de forma segura (sem regex que acidenta)."""
    out = html
    for key, val in mapping.items():
        token = "{{" + key + "}}"
        out = out.replace(token, "" if val is None else str(val))
    return out


def build_brand_mapping(brand: dict) -> dict:
    """Mapping de placeholders globais (cores, fontes, marca, logo opcional)."""
    tokens = brand.get("tokens", {})

    # Watermark: se aluno forneceu logo_path válido, embute em base64
    # pro template usar como marca d'água sutil de fundo. Caso contrário, fica vazio
    # (template não renderiza o watermark).
    logo_data_uri = ""
    logo_path_str = brand.get("logo_path")
    if logo_path_str:
        logo_path = Path(logo_path_str)
        if not logo_path.is_absolute():
            logo_path = PROJECT_ROOT / logo_path
        if logo_path.exists() and logo_path.is_file():
            try:
                logo_data_uri = encode_image_base64(logo_path)
            except Exception as e:
                print(f"AVISO: não foi possível embedar logo de {logo_path}: {e}", file=sys.stderr)

    return {
        "BRAND_NAME": brand.get("name", ""),
        "BRAND_HANDLE": brand.get("handle", ""),
        "LOGO_INITIAL": (brand.get("name") or "·")[:1].upper(),
        "LOGO_DATA_URI": logo_data_uri,
        "BRAND_PRIMARY": tokens.get("BRAND_PRIMARY", "#6366F1"),
        "BRAND_LIGHT": tokens.get("BRAND_LIGHT", "#A5B4FC"),
        "BRAND_DARK": tokens.get("BRAND_DARK", "#3730A3"),
        "LIGHT_BG": tokens.get("LIGHT_BG", "#FAF9F7"),
        "LIGHT_BORDER": tokens.get("LIGHT_BORDER", "#E8E5E0"),
        "DARK_BG": tokens.get("DARK_BG", "#1A1918"),
        "BRAND_GRADIENT": tokens.get("BRAND_GRADIENT", "linear-gradient(165deg, #3730A3 0%, #6366F1 50%, #A5B4FC 100%)"),
        "HEADING_FONT": brand.get("heading_font", "Plus Jakarta Sans"),
        "BODY_FONT": brand.get("body_font", "Plus Jakarta Sans"),
    }


# ---------- Render ----------

def render_html_to_png(html: str, output: Path, slide_height: int, wait_fonts_ms: int = 3000):
    """Renderiza um HTML único pra um PNG 1080×N."""
    output.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": VIEW_W, "height": slide_height},
            device_scale_factor=SCALE,
        )
        page = context.new_page()
        page.set_content(html, wait_until="networkidle")

        # Espera fontes carregarem
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(wait_fonts_ms)

        page.screenshot(
            path=str(output),
            clip={"x": 0, "y": 0, "width": VIEW_W, "height": slide_height},
            omit_background=False,
        )

        context.close()
        browser.close()


def render_carousel(html: str, output_dir: Path, total_slides: int,
                    slide_height: int = 525, wait_fonts_ms: int = 3000):
    """Renderiza carrossel — move o track CSS slide-a-slide e screenshota.
    O HTML deve ter `.carousel-track` com slides empilhados horizontalmente,
    cada um com 420px de largura.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": VIEW_W, "height": slide_height},
            device_scale_factor=SCALE,
        )
        page = context.new_page()
        page.set_content(html, wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(wait_fonts_ms)

        # Esconde chrome de preview (header IG, dots, caption se houver)
        page.evaluate("""(h) => {
            document.querySelectorAll('.ig-header,.ig-dots,.ig-actions,.ig-caption')
                .forEach(el => el.style.display = 'none');
            const frame = document.querySelector('.ig-frame');
            if (frame) {
                frame.style.cssText = 'width:420px;height:auto;max-width:none;border-radius:0;box-shadow:none;overflow:hidden;margin:0;';
            }
            const viewport = document.querySelector('.carousel-viewport');
            if (viewport) {
                viewport.style.cssText = 'width:420px;height:' + h + 'px;aspect-ratio:unset;overflow:hidden;cursor:default;';
            }
            document.body.style.cssText = 'padding:0;margin:0;display:block;overflow:hidden;background:transparent;';
        }""", slide_height)

        for i in range(total_slides):
            page.evaluate(f"""(idx) => {{
                const track = document.querySelector('.carousel-track');
                if (track) {{
                    track.style.transition = 'none';
                    track.style.transform = 'translateX(' + (-idx * {VIEW_W}) + 'px)';
                }}
            }}""", i)
            page.wait_for_timeout(400)

            slide_path = output_dir / f"slide-{i + 1:02d}.png"
            page.screenshot(
                path=str(slide_path),
                clip={"x": 0, "y": 0, "width": VIEW_W, "height": slide_height},
                omit_background=False,
            )
            print(f"OK: slide {i + 1}/{total_slides} → {slide_path.name}")

        context.close()
        browser.close()


# ---------- Main flows ----------

def render_static(template_path: Path, brand: dict, copy_data: dict,
                  variant_idx: int, image_path: Optional[Path], output: Path,
                  wait_fonts_ms: int):
    """Renderiza um criativo estático único."""
    html = template_path.read_text(encoding="utf-8")

    variants = copy_data.get("variants", [])
    if not variants or variant_idx < 1 or variant_idx > len(variants):
        raise ValueError(f"variant_idx {variant_idx} inválido (variantes disponíveis: {len(variants)})")
    variant = variants[variant_idx - 1]

    image_data_uri = encode_image_base64(image_path) if image_path else ""

    mapping = {
        **build_brand_mapping(brand),
        "HEADLINE": variant.get("headline", ""),
        "SUBHEADLINE": variant.get("subheadline", ""),
        "BODY_TEXT": variant.get("body", ""),
        "CTA_TEXT": variant.get("cta_text", ""),
        "IMAGE_SRC": image_data_uri,
    }

    final_html = replace_placeholders(html, mapping)

    fmt = detect_format(template_path)
    slide_height = SLIDE_HEIGHT_BY_FORMAT.get(fmt, 525)

    render_html_to_png(final_html, output, slide_height=slide_height, wait_fonts_ms=wait_fonts_ms)
    print(f"OK: criativo salvo em {output}")


def render_carousel_flow(template_path: Path, brand: dict, copy_data: dict,
                         images_map: dict, output_dir: Path, zip_output: bool,
                         wait_fonts_ms: int):
    """Renderiza carrossel completo (todos os slides + ZIP opcional)."""
    html = template_path.read_text(encoding="utf-8")

    slides = copy_data.get("slides", [])
    if not slides:
        raise ValueError("copy_data.slides está vazio")

    # Mapeia imagens em base64
    images_b64 = {}
    for slide_id, img_path in images_map.items():
        if img_path:
            try:
                images_b64[slide_id] = encode_image_base64(Path(img_path))
            except FileNotFoundError as e:
                print(f"AVISO: {e}", file=sys.stderr)
                images_b64[slide_id] = ""

    # Construir mapping global + slides serializados como JSON injetado no HTML
    # O template carousel-base.html lê window.__SLIDES_DATA__ via <script>
    slides_payload = []
    for i, slide in enumerate(slides):
        slide_id = f"slide{i + 1}"
        slides_payload.append({
            **slide,
            "slide_id": slide_id,
            "image_data": images_b64.get(slide_id, ""),
            "index": i,
            "total": len(slides),
        })

    mapping = {
        **build_brand_mapping(brand),
        "TOTAL_SLIDES": str(len(slides)),
        "SLIDES_DATA_JSON": json.dumps(slides_payload, ensure_ascii=False).replace("</", "<\\/"),
        "CAPTION": copy_data.get("caption", ""),
    }

    final_html = replace_placeholders(html, mapping)

    output_dir.mkdir(parents=True, exist_ok=True)
    render_carousel(final_html, output_dir, total_slides=len(slides), wait_fonts_ms=wait_fonts_ms)

    # README com caption
    readme_text = (
        "Carrossel gerado pelo agente de design — Imersão SAC\n"
        f"Gerado em: {datetime.now().isoformat()}\n"
        f"Slides: {len(slides)}\n\n"
        "Caption pra publicar:\n"
        "─────────────────\n"
        f"{copy_data.get('caption', '')}\n"
    )
    (output_dir / "README.txt").write_text(readme_text, encoding="utf-8")

    if zip_output:
        zip_path = output_dir.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(output_dir.iterdir()):
                if f.is_file():
                    zf.write(f, arcname=f.name)
        print(f"OK: ZIP salvo em {zip_path}")


def main():
    parser = argparse.ArgumentParser(description="Renderiza criativos (estático/carrossel) via Playwright")
    parser.add_argument("--template", required=True, help="Caminho do template HTML")
    parser.add_argument("--brand", required=True, help="Caminho do brand-kit.json")
    parser.add_argument("--copy", required=True, help="Caminho do JSON de copy")
    parser.add_argument("--variant", type=int, default=1, help="Índice da variante (1-based, estático)")
    parser.add_argument("--image", help="Caminho da imagem (estático)")
    parser.add_argument("--images", help="Caminho do JSON {slide_id: path} (carrossel)")
    parser.add_argument("--output", help="Caminho de saída PNG (estático)")
    parser.add_argument("--output-dir", help="Diretório de saída (carrossel)")
    parser.add_argument("--zip", action="store_true", help="Empacota carrossel em ZIP")
    parser.add_argument("--wait-fonts", type=int, default=3000, help="Tempo de espera por fontes (ms)")
    args = parser.parse_args()

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"ERRO: template não existe: {template_path}", file=sys.stderr)
        sys.exit(1)

    brand = json.loads(Path(args.brand).read_text(encoding="utf-8"))
    copy_data = json.loads(Path(args.copy).read_text(encoding="utf-8"))

    fmt = detect_format(template_path)
    is_carousel = fmt == "carousel"

    if is_carousel:
        if not args.output_dir:
            parser.error("--output-dir é obrigatório para carrossel")
        images_map = {}
        if args.images:
            images_map = json.loads(Path(args.images).read_text(encoding="utf-8"))
        render_carousel_flow(
            template_path=template_path,
            brand=brand,
            copy_data=copy_data,
            images_map=images_map,
            output_dir=Path(args.output_dir),
            zip_output=args.zip,
            wait_fonts_ms=args.wait_fonts,
        )
    else:
        if not args.output:
            parser.error("--output é obrigatório para estático")
        render_static(
            template_path=template_path,
            brand=brand,
            copy_data=copy_data,
            variant_idx=args.variant,
            image_path=Path(args.image) if args.image else None,
            output=Path(args.output),
            wait_fonts_ms=args.wait_fonts,
        )


if __name__ == "__main__":
    main()
