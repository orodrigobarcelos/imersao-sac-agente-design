---
name: criar-estatico
description: Cria um criativo de anúncio único (uma imagem só, não-carrossel) em PNG pronto pra Meta Ads / Google Ads, nos formatos 1:1 (1080×1080 quadrado feed), 4:5 (1080×1350 vertical mobile) ou 9:16 (1080×1920 Stories/Reels). Conduz briefing focado em conversão (objetivo, oferta, público, CTA), gera 3 variantes de copy via Gemini para A/B test, lida com a imagem (upload do aluno ou geração via Gemini Image), monta o HTML e renderiza via Playwright. Use quando o aluno disser frases tipo "criar criativo único", "anúncio de 1 imagem", "imagem estática", "post estático pra anúncio", "criativo pra Stories", "ad de uma foto só", "criar anúncio simples", "não quero carrossel só uma imagem", ou quando o briefing dele claramente é de uma peça única. Se ele falar de carrossel ou múltiplos slides, use criar-carrossel em vez desta.
---

# Skill: criar-estatico

Cria um criativo de anúncio único (não-carrossel) em PNG pronto pra subir no Meta Ads.

## Pré-requisitos

Antes de invocar, garanta que:
1. Setup foi validado (`verificar-setup`)
2. `brand/brand-kit.json` existe (se não, invoque `configurar-marca` antes)

## Quando invocar

Aluno disse algo como:
- "criar criativo único"
- "anúncio de 1 imagem"
- "imagem estática"
- "post estático"
- "criativo pra Stories"

## Fluxo passo-a-passo

### Passo 1 — Briefing do anúncio

Faça perguntas, **uma por vez**, com sugestões:

1. **Objetivo**
   > "Pra que serve esse anúncio?
   > 1. Vender produto/serviço
   > 2. Capturar lead (email, WhatsApp)
   > 3. Anunciar promoção/desconto
   > 4. Promover evento / aula gratuita
   > 5. Outro (descreva)"

2. **O que está sendo anunciado**
   > "Me conta em 1-2 frases o que é. Pode ser:
   > - Produto: nome, o que faz, pra quem
   > - Serviço/curso: tema, transformação prometida
   > - Evento: tipo, data, gancho"

3. **Público-alvo**
   > "Quem é o público? (ex: 'mulheres 30-45 que querem emagrecer', 'donos de pequenos negócios que vendem online')"

4. **Oferta / proposta**
   > "Tem alguma oferta específica? (preço, bônus, garantia, desconto, frete grátis, etc) Pode pular se não tiver."

5. **CTA — o que a pessoa faz quando clica**
   > "O que você quer que a pessoa faça depois de clicar?
   > 1. Comprar agora
   > 2. Se inscrever / cadastrar
   > 3. Falar no WhatsApp
   > 4. Baixar material grátis
   > 5. Saber mais (genérico — só use se nenhum dos outros)"

6. **Formato**
   > "Qual formato pra esse anúncio?
   > 1. **Quadrado (1:1)** — feed Instagram/Facebook (1080×1080)
   > 2. **Vertical (4:5)** — feed mobile, mais espaço (1080×1350) ⭐ recomendado
   > 3. **Stories/Reels (9:16)** — telas verticais (1080×1920)"

### Passo 2 — Gera copy via Gemini

Carrega o brand kit e dispara o script:

```bash
python3 scripts/gemini_text.py \
  --tipo estatico \
  --formato 4x5 \
  --objetivo "captar lead" \
  --produto "curso de inglês online em 60 dias" \
  --publico "profissionais 25-45 que precisam falar inglês no trabalho" \
  --oferta "primeira aula grátis" \
  --cta "se inscrever" \
  --tom "profissional e direto" \
  --variantes 3 \
  > /tmp/copy-estatico.json
```

O script retorna 3 variantes:

```json
{
  "variants": [
    {
      "style": "agressivo",
      "headline": "Pare de perder oportunidades por causa do inglês",
      "subheadline": "Em 60 dias falando com confiança",
      "body": "Método validado por +2.000 alunos.",
      "cta_text": "Quero minha aula grátis"
    },
    {
      "style": "racional",
      "headline": "Aprenda inglês em 60 dias com método validado",
      "subheadline": "Aulas práticas focadas no trabalho",
      "body": "+2.000 alunos transformados.",
      "cta_text": "Pegar aula grátis"
    },
    {
      "style": "emocional",
      "headline": "Você merece ser ouvido em qualquer reunião",
      "subheadline": "60 dias até falar inglês com confiança",
      "body": "Mais de 2.000 pessoas já chegaram lá.",
      "cta_text": "Começar aula grátis"
    }
  ]
}
```

### Passo 3 — Mostra as 3 variantes ao aluno

> "Gerei 3 variações de copy. Qual combina mais?
>
> **1. Agressiva** — *"Pare de perder oportunidades por causa do inglês"*
> Subhead: Em 60 dias falando com confiança
> CTA: Quero minha aula grátis
>
> **2. Racional** — *"Aprenda inglês em 60 dias com método validado"*
> Subhead: Aulas práticas focadas no trabalho
> CTA: Pegar aula grátis
>
> **3. Emocional** — *"Você merece ser ouvido em qualquer reunião"*
> Subhead: 60 dias até falar inglês com confiança
> CTA: Começar aula grátis
>
> Qual quer usar? (1, 2 ou 3 — ou pode pedir pra refazer com algum ajuste)"

### Passo 4 — Imagem do criativo

Pergunta:

> "Sobre a imagem, qual desses?
> 1. **Tenho foto pra usar** (do produto, sua, do resultado) — me passa o caminho ou arrasta aqui
> 2. **Gera com IA** — descrevo o que quero e o Gemini cria
> 3. **Sem imagem** — só fundo da marca + texto"

#### Opção 1 — Upload
- Aluno passa caminho ou arrasta
- Salva em `assets/` se ainda não tá lá
- Lê dimensões via `python3 -c "from PIL import Image; print(Image.open('...').size)"` pra avisar se a foto for muito pequena (<800px do lado menor)

#### Opção 2 — Gerar com Gemini

Pergunta o que ilustrar:
> "Descreve a cena que você quer. Tipo: 'pessoa sorrindo no laptop em escritório moderno', 'frutas frescas em tigela rústica de madeira'"

Roda:

```bash
python3 scripts/gemini_image.py \
  --prompt "professional in modern office, smiling, looking at laptop, soft natural light" \
  --aspect 4x5 \
  --style "editorial photography" \
  --output assets/gerada-{timestamp}.png
```

Mostra ao aluno e pergunta se aprova ou regenera.

#### Opção 3 — Sem imagem
Usa o gradient da marca (BRAND_GRADIENT) ou DARK_BG sólido.

### Passo 5 — Monta o HTML

Carrega o template apropriado de `templates/static-{1x1|4x5|9x16}.html` e substitui placeholders:

- `{{BRAND_NAME}}`, `{{BRAND_HANDLE}}`, `{{LOGO_INITIAL}}`
- `{{BRAND_PRIMARY}}`, `{{BRAND_LIGHT}}`, `{{BRAND_DARK}}`, `{{LIGHT_BG}}`, `{{DARK_BG}}`, `{{BRAND_GRADIENT}}`
- `{{HEADING_FONT}}`, `{{BODY_FONT}}`
- `{{HEADLINE}}`, `{{SUBHEADLINE}}`, `{{BODY_TEXT}}`, `{{CTA_TEXT}}`
- `{{IMAGE_SRC}}` — caminho local ou base64 da imagem (ou string vazia se sem imagem)

Salva em `/tmp/render-estatico-{ts}.html` (não polui o projeto do aluno).

Use Python para fazer a substituição. Não tente substituir placeholders via `sed`, `awk` ou heredocs do shell — o shell interpreta `$`, crases e dígitos dentro do HTML como variáveis e corrompe o conteúdo silenciosamente (problema conhecido do projeto-base). O `render_slides.py` faz tudo em Python, isolado:

```bash
python3 scripts/render_slides.py \
  --template templates/static-4x5.html \
  --brand brand/brand-kit.json \
  --copy /tmp/copy-estatico.json \
  --variant 1 \
  --image assets/gerada-2026-04-24.png \
  --output output/estatico-{ts}.png
```

O script `render_slides.py` faz a substituição internamente em Python e renderiza com Playwright.

### Passo 6 — Mostra o resultado e aceita ajustes

Tenta abrir automaticamente:

```bash
# Mac:
open output/estatico-{ts}.png
# Windows:
start output/estatico-{ts}.png
# Linux:
xdg-open output/estatico-{ts}.png
```

Pergunta:

> "Pronto! Salvei em `output/estatico-2026-04-24-2300.png` (formato 4:5, 1080×1350px). Tá bom assim ou quer ajustar algo?
>
> Posso:
> - Refazer a copy (outra variação ou estilo)
> - Trocar a imagem
> - Mudar a cor de fundo (claro/escuro/gradient)
> - Ajustar tamanho da headline
> - Criar versões A/B (mesmo design, copy diferente)"

## Regras importantes

1. **NUNCA gere shell scripts pra fazer substituição em HTML.** Sempre use o script Python `render_slides.py`. Variáveis do shell corrompem caracteres `$`, backticks e números.

2. **Sempre embute imagens externas em base64** dentro do HTML antes de renderizar (o script já faz isso). Caminho relativo pode falhar dependendo de onde o headless browser executa.

3. **Aguarda fontes carregarem.** O `render_slides.py` já espera `document.fonts.ready` + 3s de buffer.

4. **Texto longo vira problema.** Se a headline tem >50 caracteres, alerta o aluno: "essa headline tá longa pra anúncio, recomendo cortar pra 7-9 palavras". Se ele insistir, o template aplica autofit (reduz fontSize).

5. **Trate a chave Gemini como senha.** Não rode `cat .env`, não inclua o conteúdo dela em mensagens, não logue cabeçalhos `Authorization`. Se precisar validar a chave, use o script (`gemini_text.py --test`) que devolve só `OK` ou erro descritivo. Vazar a chave compromete a conta do aluno e a cota grátis dele.

## Erros comuns

| Erro | Fix |
|---|---|
| Gemini retornou variante sem `cta_text` | Roda de novo (1 retry); se persistir, pede `--variantes 1` e usa parser tolerante |
| Imagem upload não existe | Pede caminho de novo; oferece listar `assets/` |
| Playwright timeout no render | Aumenta `--wait 5000` no script |
| HTML renderizou com fonte errada | Verifica que `<link>` Google Fonts carregou; pode ser conexão lenta — tenta de novo |

## Quando NÃO invocar

- Aluno quer carrossel → invoca `criar-carrossel`
- Setup ainda não validado → invoca `verificar-setup` antes
- Brand kit não existe → invoca `configurar-marca` antes
