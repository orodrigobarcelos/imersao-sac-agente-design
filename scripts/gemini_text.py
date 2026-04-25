#!/usr/bin/env python3
"""
Gera copy de anúncio (estático ou carrossel) via Gemini 2.5 Flash com responseSchema.

Uso:
  # Teste de chave (ping mínimo na API)
  python3 scripts/gemini_text.py --test

  # Carrossel completo (5-10 slides)
  python3 scripts/gemini_text.py \\
    --tipo carrossel --slides 7 \\
    --objetivo "captar lead" \\
    --produto "curso de inglês 60 dias" \\
    --publico "profissionais 25-45" \\
    --dor "perder oportunidades por não falar inglês" \\
    --transformacao "falar com confiança em reuniões" \\
    --cta "se inscrever" \\
    --tom "profissional e direto" \\
    > /tmp/copy.json

  # Estático (3 variantes de copy)
  python3 scripts/gemini_text.py \\
    --tipo estatico --formato 4x5 \\
    --objetivo "captar lead" \\
    --produto "curso de inglês 60 dias" \\
    --publico "profissionais 25-45" \\
    --cta "se inscrever" \\
    --variantes 3 \\
    > /tmp/copy-estatico.json
"""

import argparse
import json
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


# ---------- Schemas ----------

CAROUSEL_SCHEMA = {
    "type": "object",
    "properties": {
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["hero", "problem", "solution", "features", "details", "how_to", "cta"],
                    },
                    "tag": {"type": "string", "description": "Tag uppercase curta (ex: 'O PROBLEMA')"},
                    "headline": {"type": "string"},
                    "subheadline": {"type": "string"},
                    "body": {"type": "string"},
                    "items": {"type": "array", "items": {"type": "string"}},
                    "legacy_items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Lista curta de 2-5 termos (1-3 palavras cada) representando "
                            "ferramentas, métodos ou abordagens que o público vai ABANDONAR ao adotar "
                            "essa solução. Renderizado como pills riscadas. Use APENAS em slides 'problem' "
                            "quando a narrativa é 'esquece X, Y, Z — agora é assim'. "
                            "Exemplos: ['Photoshop', 'Canva', 'Figma'] ou ['Planilha manual', 'Email solto', 'Reuniões longas']."
                        ),
                    },
                    "features": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "icon": {"type": "string"},
                                "label": {"type": "string"},
                                "desc": {"type": "string"},
                            },
                            "required": ["label", "desc"],
                        },
                    },
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "desc": {"type": "string"},
                            },
                            "required": ["title", "desc"],
                        },
                    },
                    "quote": {"type": "string"},
                    "cta_text": {"type": "string"},
                    "image_prompt": {
                        "type": "string",
                        "description": "Descrição em inglês pra Gemini Image (ou null se slide não precisa)",
                    },
                },
                "required": ["type", "tag", "headline"],
            },
        },
        "caption": {"type": "string", "description": "Legenda pra publicar com o post"},
        "image_keywords": {
            "type": "object",
            "description": "Mapa slide_id → keyword curto pra busca/geração de imagem",
        },
    },
    "required": ["slides", "caption"],
}


STATIC_SCHEMA = {
    "type": "object",
    "properties": {
        "variants": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "style": {"type": "string", "enum": ["agressivo", "racional", "emocional"]},
                    "headline": {"type": "string"},
                    "subheadline": {"type": "string"},
                    "body": {"type": "string"},
                    "cta_text": {"type": "string"},
                },
                "required": ["style", "headline", "cta_text"],
            },
        },
        "caption": {"type": "string"},
        "image_prompt": {"type": "string"},
    },
    "required": ["variants", "caption"],
}


# ---------- Prompts ----------

SYSTEM_PROMPT_CAROUSEL = """Você é um especialista em copywriting de anúncios de performance (Meta Ads, Google Ads).
Seu objetivo é gerar arcos narrativos persuasivos para carrosseis de anúncio em português brasileiro.

PRINCÍPIOS:
1. Hook tem 1 segundo — slide 1 PARA o scroll. Usa benefício forte, pergunta provocativa, ou desafia uma crença comum. Nunca descreve o produto no slide 1.
2. Mostra dor concreta, não features genéricas. "Pare de perder leads" > "CRM com 200 funcionalidades".
3. CTA específico. "Quero meu diagnóstico grátis" > "Saiba mais".
4. Carrossel tem ARCO. Cada slide abre gancho pro próximo. Não é lista solta.
5. Headline curta. 7-9 palavras é o sweet spot pra anúncio.
6. Linguagem do público. Se o público é leigo, evita jargão. Se é técnico, mostra domínio.

ESTRUTURA TÍPICA POR TIPO DE SLIDE:
- hero: headline + subheadline curta. Hook agressivo. image_prompt opcional.
- problem: headline + items (3-4 dores específicas). image_prompt opcional.
  * Opcional: legacy_items — 2 a 5 termos curtos (1-3 palavras) que o público vai
    DEIXAR PRA TRÁS. Renderizado como pills riscadas. Use SOMENTE quando a narrativa
    do briefing é claramente de pivot/substituição: "esquece X", "cansou de Y", "antes
    era Z, agora é assim", comparativo com concorrentes nomeados. NÃO use quando a
    dor é genérica sem ferramenta/método específico pra abandonar.
- solution: headline + body. quote (depoimento curto) opcional. image_prompt opcional.
- features: headline + features array (3-4 com icon char + label + desc curta).
- details: headline + body OU items. Aprofunda diferencial.
- how_to: headline + steps (3 passos numerados, title + desc curta).
- cta: headline + subheadline + cta_text. SEM swipe arrow visual (último slide).

Retorne APENAS JSON válido seguindo o schema. Não inclua texto fora do JSON.
"""


SYSTEM_PROMPT_STATIC = """Você é um especialista em copywriting de anúncios de performance.
Gere 3 variantes de copy para UM criativo estático (1 imagem, não-carrossel) em português.

VARIANTES OBRIGATÓRIAS:
1. AGRESSIVA — provocativa, desafia crença, pode usar negação ("Pare de...", "Você sabia que...")
2. RACIONAL — direta ao benefício, com dado/prova ("+2.000 alunos", "em 60 dias")
3. EMOCIONAL — apela a aspiração, identidade, desejo profundo

REGRAS:
- Headline: 7-9 palavras MAX. Curta e impactante.
- Subheadline: 1 linha de reforço (opcional).
- Body: 1-2 frases curtas (opcional).
- CTA específico — nunca "Saiba mais" genérico.

Retorne APENAS JSON válido seguindo o schema.
"""


def build_user_prompt_carousel(args) -> str:
    parts = [
        f"Crie um carrossel de anúncio com {args.slides} slides.",
        f"Objetivo: {args.objetivo}",
        f"Produto/serviço: {args.produto}",
        f"Público-alvo: {args.publico}",
    ]
    if args.dor:
        parts.append(f"Dor principal: {args.dor}")
    if args.transformacao:
        parts.append(f"Transformação prometida: {args.transformacao}")
    if args.prova_social:
        parts.append(f"Prova social: {args.prova_social}")
    if args.oferta:
        parts.append(f"Oferta: {args.oferta}")
    parts.append(f"CTA desejado: {args.cta}")
    if args.tom:
        parts.append(f"Tom de voz: {args.tom}")
    parts.append("\nGere o arco completo seguindo a estrutura típica.")
    return "\n".join(parts)


def build_user_prompt_static(args) -> str:
    parts = [
        f"Crie 3 variantes de copy para um anúncio estático {args.formato or '4x5'}.",
        f"Objetivo: {args.objetivo}",
        f"Produto/serviço: {args.produto}",
        f"Público-alvo: {args.publico}",
    ]
    if args.oferta:
        parts.append(f"Oferta: {args.oferta}")
    parts.append(f"CTA desejado: {args.cta}")
    if args.tom:
        parts.append(f"Tom de voz: {args.tom}")
    parts.append("\nGere as 3 variantes (agressiva, racional, emocional).")
    return "\n".join(parts)


# ---------- Client ----------

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: GEMINI_API_KEY not set. Verifique .env na raiz do projeto.", file=sys.stderr)
        sys.exit(2)
    return genai.Client(api_key=api_key)


def test_connection():
    """Ping mínimo na API. Retorna OK ou erro descritivo."""
    try:
        client = get_client()
        model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model,
            contents="diga apenas a palavra OK",
            config=types.GenerateContentConfig(max_output_tokens=10, temperature=0.0),
        )
        if response and response.text:
            print("OK")
            return 0
        print("ERRO: resposta vazia da API", file=sys.stderr)
        return 1
    except Exception as e:
        msg = str(e)
        if "401" in msg or "403" in msg or "API_KEY_INVALID" in msg:
            print("ERRO: chave Gemini inválida (401/403). Gere outra em https://aistudio.google.com/app/apikey", file=sys.stderr)
            return 3
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            print("ERRO: cota Gemini esgotada (429). Espera 24h ou aumenta o limite no AI Studio.", file=sys.stderr)
            return 4
        print(f"ERRO: {msg}", file=sys.stderr)
        return 1


def generate_with_retry(client, model: str, contents, system_instruction: str, schema: dict,
                        temperature: float = 0.8, retries: int = 1) -> dict:
    """Chama Gemini com responseSchema + retry simples."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=schema,
        temperature=temperature,
    )

    last_err = None
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            text = response.text
            if not text:
                raise RuntimeError("Resposta vazia do Gemini")
            return json.loads(text)
        except json.JSONDecodeError as e:
            last_err = f"JSON malformado: {e}"
            if attempt < retries:
                continue
        except Exception as e:
            last_err = str(e)
            if attempt < retries and ("500" in last_err or "503" in last_err):
                continue
            raise

    raise RuntimeError(f"Gemini falhou após {retries + 1} tentativas: {last_err}")


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(description="Gera copy de anúncio via Gemini")
    parser.add_argument("--test", action="store_true", help="Testa conexão e chave (ping mínimo)")
    parser.add_argument("--tipo", choices=["carrossel", "estatico"], help="Tipo de criativo")
    parser.add_argument("--slides", type=int, default=7, help="Número de slides (carrossel)")
    parser.add_argument("--variantes", type=int, default=3, help="Número de variantes de copy (estático)")
    parser.add_argument("--formato", choices=["1x1", "4x5", "9x16"], help="Formato (estático)")
    parser.add_argument("--objetivo", help="Objetivo do anúncio")
    parser.add_argument("--produto", help="Produto/serviço sendo anunciado")
    parser.add_argument("--publico", help="Público-alvo")
    parser.add_argument("--dor", help="Dor principal do público (carrossel)")
    parser.add_argument("--transformacao", help="Transformação prometida (carrossel)")
    parser.add_argument("--prova-social", dest="prova_social", help="Prova social")
    parser.add_argument("--oferta", help="Oferta concreta")
    parser.add_argument("--cta", help="Call to action")
    parser.add_argument("--tom", help="Tom de voz")
    parser.add_argument("--retry", type=int, default=1, help="Número de retries em caso de falha")
    args = parser.parse_args()

    if args.test:
        sys.exit(test_connection())

    if not args.tipo:
        parser.error("--tipo é obrigatório (carrossel | estatico)")

    required = ["objetivo", "produto", "publico", "cta"]
    missing = [f for f in required if not getattr(args, f)]
    if missing:
        parser.error(f"argumentos obrigatórios faltando: {missing}")

    client = get_client()
    model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")

    if args.tipo == "carrossel":
        if args.slides < 5 or args.slides > 10:
            parser.error("--slides deve estar entre 5 e 10")
        result = generate_with_retry(
            client=client,
            model=model,
            contents=build_user_prompt_carousel(args),
            system_instruction=SYSTEM_PROMPT_CAROUSEL,
            schema=CAROUSEL_SCHEMA,
            retries=args.retry,
        )
    else:  # estatico
        result = generate_with_retry(
            client=client,
            model=model,
            contents=build_user_prompt_static(args),
            system_instruction=SYSTEM_PROMPT_STATIC,
            schema=STATIC_SCHEMA,
            retries=args.retry,
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
