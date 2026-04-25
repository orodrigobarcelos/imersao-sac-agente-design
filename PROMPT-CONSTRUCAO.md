# 🛠️ Prompt de Construção — Agente Criativo de Design

> **Como usar este arquivo:** abra uma pasta vazia no Claude Code Desktop e cole o conteúdo da seção [📋 PROMPT (copiar e colar)](#-prompt-copiar-e-colar) na conversa. O Claude vai construir o projeto inteiro.

---

## O que esse prompt constrói

Um **template Claude Code** que transforma o Claude num agente especialista em criar criativos de anúncio (Meta Ads / Google Ads) — estáticos ou carrosséis — através de conversa, sem o usuário precisar abrir editor de imagem nem escrever código.

**Quem usa**: alunos leigos em design e terminal, dentro do Claude Code Desktop.

**Como funciona**: o aluno baixa a pasta, abre no Claude Code, manda "oi" → o Claude conduz onboarding (cria `.env`, instala dependências, configura marca), depois conversa sobre o anúncio (briefing → copy via Gemini → imagem via upload ou Gemini → render Playwright em PNG 1080×1350) e entrega arquivos prontos pra subir em campanhas pagas.

---

## 📋 PROMPT (copiar e colar)

Tudo abaixo, até o fim do bloco, é o que você cola na conversa do Claude Code:

````markdown
# Construir: Agente Criativo de Design (Imersão SAC)

Você vai construir um **projeto Claude Code completo** nesta pasta. O resultado será um template educacional que outros usuários (leigos em terminal e design) baixam, abrem no Claude Code Desktop e usam pra criar criativos de anúncio (estáticos ou carrosséis) conversando com o Claude.

Não é um app web. **É um projeto Claude Code estruturado** — composto por: um `CLAUDE.md` central, 4 skills em `.claude/skills/`, 5 scripts Python em `scripts/`, 4 templates HTML em `templates/`, docs auxiliares em `docs/`, e arquivos de configuração na raiz.

## Filosofia (sigo durante toda a construção)

1. **Português brasileiro** em toda comunicação com o usuário e nos arquivos `.md`
2. **Tom acessível** — sem jargão. O usuário final é leigo
3. **Claude conduz tudo** — o aluno não edita arquivos manualmente; o Claude usa as tools (Write/Edit) pra criar arquivos por ele
4. **Cross-platform** — funciona em Mac, Linux e Windows (com Git Bash)
5. **Sem dependências fora do necessário** — Python 3.10+, google-genai, playwright, python-dotenv, Pillow

## Stack

| Camada | Escolha |
|---|---|
| Orquestração | Claude Code Desktop (interface conversacional) |
| Linguagem dos scripts | Python 3.10+ |
| IA texto | Gemini 2.5 Flash via SDK `google-genai` (com `responseSchema` pra JSON estruturado) |
| IA imagem | Gemini 2.5 Flash Image (Nano Banana) |
| Render | Playwright (Chromium headless) |
| Templates | HTML + CSS + JS injetado |
| Persistência | Arquivos locais (`.env`, `brand/brand-kit.json`, `output/`) |

**Sem auth, sem banco, sem servidor web.** Tudo local.

## Estrutura de arquivos a criar

```
.
├── CLAUDE.md                          # Entry point — instruções do agente
├── COMECE-AQUI.md                     # Tutorial visual de 3 passos pro aluno
├── README.md                          # Tutorial detalhado (linka pro COMECE-AQUI)
├── PLANO.md                           # Plano técnico (referência interna)
├── PROMPT-CONSTRUCAO.md               # Este prompt, pra reconstrução futura
├── .env.example                       # Template GEMINI_API_KEY=
├── .gitignore                         # Protege .env, .venv, node_modules, output, brand
│
├── .claude/
│   └── skills/
│       ├── verificar-setup/SKILL.md   # Checa Python, Playwright, .env (cria .env se faltar)
│       ├── configurar-marca/SKILL.md  # Briefing de marca + análise de imagens de referência
│       ├── criar-estatico/SKILL.md    # Fluxo de criativo único (1:1, 4:5, 9:16)
│       └── criar-carrossel/SKILL.md   # Fluxo de carrossel (5-10 slides)
│
├── docs/
│   ├── design-system.md               # Tokens, fontes, layouts, componentes
│   └── prompts-gemini.md              # Princípios de copy + prompts de imagem
│
├── templates/
│   ├── carousel-base.html             # 420×525, com track horizontal de slides
│   ├── static-1x1.html                # Quadrado feed (renderiza 1080×1080)
│   ├── static-4x5.html                # Vertical mobile (renderiza 1080×1350)
│   └── static-9x16.html               # Stories/Reels (renderiza 1080×1920)
│
├── scripts/
│   ├── requirements.txt               # google-genai, playwright, python-dotenv, Pillow
│   ├── derive_palette.py              # 1 cor primária → 6 tokens de paleta
│   ├── gemini_text.py                 # Gera copy via Gemini (com --test pra ping)
│   ├── gemini_image.py                # Gera imagem via Gemini Image
│   ├── render_slides.py               # Playwright export → PNG 1080×N (+ ZIP)
│   └── analyze_references.py          # Extrai paleta dominante de imagens de referência
│
├── brand/                             # Vazia, com .gitkeep — vai receber brand-kit.json
├── assets/                            # Vazia, com .gitkeep — receberá fotos do aluno
└── output/                            # Vazia, com .gitkeep — receberá os PNGs/ZIPs gerados
```

---

## Especificação detalhada por arquivo

### 1. `CLAUDE.md` (entry point — Claude lê automaticamente ao abrir o projeto)

Define o comportamento do agente. Cobrir:

- **Português obrigatório** em toda comunicação
- **Uma pergunta por vez** — nunca questionário gigante
- **Seja proativo nos defaults** — se aluno disser "tanto faz", você escolhe
- **Mostre, não conte** — abre arquivos pra o aluno ver, em vez de descrever
- **Detecção de cenário** na primeira interação:
  - `.env` vazio → Onboarding Leigo (cria `.env` pelo aluno)
  - `.env` ok mas sem `brand/brand-kit.json` → invoca `configurar-marca`
  - Tudo pronto → cumprimenta curto e pergunta qual criativo criar
- **Mensagens-gatilho** que iniciam onboarding: "oi", "olá", "começar", "ajuda", "como funciona", "primeira vez", ou qualquer mensagem se for o primeiro turno
- **Onboarding Leigo (Seção 2.2)** — sequência:
  1. Boas-vindas curtas
  2. Pega chave Gemini no chat e cria `.env` via Write tool (formato: `GEMINI_API_KEY={CHAVE}\nGEMINI_TEXT_MODEL=gemini-2.5-flash\nGEMINI_IMAGE_MODEL=gemini-2.5-flash-image`)
  3. Invoca skill `verificar-setup` pra validar Python e instalar deps
  4. Invoca skill `configurar-marca` pra coletar identidade visual
  5. Pergunta tipo de criativo (estático ou carrossel)
- **Compatibilidade cross-shell (Seção 3.5)** — tabela com equivalentes Bash ↔ PowerShell pra `test -f`, `grep`, `mkdir -p`, `open`/`start`, `python3` vs `python`, ativação de venv. Diretriz: prefira chamar Python a improvisar shell — scripts em `scripts/` são cross-platform.
- **Quando invocar cada skill** — tabela de mapeamento situação → skill
- **Princípios de design pra anúncios** — hook em 1 segundo, mostra dor (não features), CTA específico, carrossel tem arco, imagem real > IA, 2-3 variantes pra A/B
- **Como executar scripts** — `python3 scripts/X.py --arg ...`, redirecionar JSON pra `/tmp/...` quando grande
- **Tratamento de erros comuns** — tabela: `ModuleNotFoundError`, `Executable doesn't exist` (Playwright), `GEMINI_API_KEY not set`, `429 RESOURCE_EXHAUSTED`, `400 INVALID_ARGUMENT` (safety filter)
- **Ética** — nunca expor a chave Gemini, nunca gerar copy enganosa, alertar sobre claims sem evidência

### 2. `COMECE-AQUI.md` (manual de bordo do aluno)

3 passos visuais SEM terminal:
1. Baixa o ZIP do GitHub (botão verde "Code" → Download ZIP → descompacta)
2. Instala Claude Code Desktop (link de download). **Se Windows**, instala também Git for Windows (https://git-scm.com/download/win) — explica por quê em 1 frase
3. Abre a pasta no Claude Code (arrasta ou File → Open Folder) e manda exatamente: `oi, vamos começar`

Inclui seção "Se algo der errado" orientando a colar o erro no chat. E seção sobre tempo (~10 min primeira vez) e custo (Claude Code: assinatura; Gemini: grátis até 1500 req/dia).

### 3. `README.md`

CTA grande no topo apontando pro `COMECE-AQUI.md`. Resto cobre:
- O que dá pra fazer (estático e carrossel)
- O que precisa instalar (Claude Code, Python, chave Gemini)
- Como usar com dicas: "Tem identidade visual? Diga logo. Não tem? Manda referências."
- Estrutura de pastas (alto nível)
- Problemas comuns

### 4. `PLANO.md`

Documento técnico interno descrevendo: visão geral, stack, arquitetura, decisões técnicas chave, fases de build. Útil pra quem quer entender ou contribuir.

### 5. `.env.example`

```
GEMINI_API_KEY=
GEMINI_TEXT_MODEL=gemini-2.5-flash
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
```

### 6. `.gitignore`

Bloqueia: `.env`, `.env.local`, `output/*` (mantendo `.gitkeep`), `brand/*` (mantendo `.gitkeep`), `assets/*` (mantendo `.gitkeep`), `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `*.egg-info/`, `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`, `*.log`, `node_modules/`, `app/`, `public/`, etc.

---

## Skills (4)

Cada skill é um arquivo `.claude/skills/<nome>/SKILL.md` com frontmatter YAML (name + description) seguido do corpo em markdown.

### Skill `verificar-setup`

**Description (pushy)**: "Valida e instala dependências do projeto (Python ≥3.10, google-genai, playwright, dotenv, Pillow, Chromium headless, .env com GEMINI_API_KEY). Use sempre que o aluno abrir o projeto pela primeira vez, mencionar erro tipo 'ModuleNotFoundError', 'Executable doesn't exist', 'GEMINI_API_KEY not set', 'command not found', ou disser 'tá dando erro', 'instala', 'configura'. Também invoque antes de qualquer skill criadora se setup ainda não foi validado nesta sessão."

**Fluxo**:
1. Detecta SO (`uname -s` ou fallback)
2. Verifica Python ≥ 3.10. Se faltar, orienta link de download (Mac: brew/python.org; Windows: python.org com ÊNFASE em "Add Python to PATH")
3. Verifica libs Python: `python3 -c "import google.genai, playwright, dotenv, PIL"`. Se falhar, roda `pip install -r scripts/requirements.txt`. Se der PEP 668 (Mac/Linux), cria venv: `python3 -m venv .venv && source .venv/bin/activate && pip install -r scripts/requirements.txt`
4. Verifica Chromium do Playwright. Se faltar: `playwright install chromium` (avisa que é ~200MB)
5. Verifica `.env`. Se ausente OU chave vazia: **PERGUNTA A CHAVE NO CHAT** (link pra https://aistudio.google.com/app/apikey, instruções passo-a-passo), valida formato (deve começar com `AIza`, ~39 chars), e usa **tool Write** pra criar `.env` com:
   ```
   GEMINI_API_KEY={chave}
   GEMINI_TEXT_MODEL=gemini-2.5-flash
   GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
   ```
6. Testa chave com `python3 scripts/gemini_text.py --test`
7. Confirma sucesso com checklist visual

**Política de segurança**: nunca rodar `cat .env` ou expor a chave. Pra validar usa `grep -E "^GEMINI_API_KEY=.+" .env > /dev/null` (não imprime valor). Pra testar usa o script que devolve `OK`/erro sem expor.

### Skill `configurar-marca`

**Description (pushy)**: "Conduz briefing de identidade visual da marca (cor primária, tipografia, logo, tom de voz, handle) e salva em brand/brand-kit.json. Suporta dois cenários — aluno com identidade definida (coleta direta) e aluno sem (analisa imagens visuais que ele arrasta no chat e sugere uma direção). Invoque sempre que brand/brand-kit.json não existir e o aluno quiser criar um criativo, ou quando ele disser 'configurar marca', 'mudar a marca', 'outra empresa', 'ainda não tenho identidade', 'me ajuda a definir o estilo', 'tenho referências mas não defini nada'."

**Fluxo**:
1. Pergunta inicial em 3 opções: tem tudo definido / mais ou menos / não tem nada

**Caminho A — tem identidade**:
- Coleta uma pergunta por vez: nome da marca, handle, cor primária (hex ou nome — se nome, escolhe um hex razoável e confirma), pareamento de fonte (oferece 7 opções: editorial_premium, modern_clean, warm_approachable, technical_sharp, bold_expressive, classic_trust, rounded_friendly), logo (upload ou pula), tom de voz
- Roda `python3 scripts/derive_palette.py --primary "{cor}" --output brand/brand-kit.json --append` pra gerar paleta
- Adiciona name/handle/fonts/tone ao JSON via Edit
- Mostra resumo

**Caminho B — sem identidade**:
- Pede 2-5 imagens de referência (anúncios, posts, sites que goste). Aluno arrasta no chat.
- Salva em `brand/references/`
- **Analisa visualmente via capacidade multimodal** + opcionalmente roda `python3 scripts/analyze_references.py --dir brand/references/` pra extrair paleta numérica
- Sintetiza padrão (cores, mood, tipografia, estética) e justifica
- Aluno aprova/ajusta/refaz
- Continua coletando nome/handle/tom como Caminho A
- Salva em brand/brand-kit.json

**Schema do brand-kit.json**:
```json
{
  "name": "...",
  "handle": "...",
  "tone": "...",
  "primary_color": "#hex",
  "heading_font": "...",
  "body_font": "...",
  "font_pairing_id": "...",
  "logo_path": "brand/logo.png" (opcional),
  "logo_initial": "A",
  "tokens": {
    "BRAND_PRIMARY", "BRAND_LIGHT", "BRAND_DARK",
    "LIGHT_BG", "LIGHT_BORDER", "DARK_BG", "BRAND_GRADIENT"
  },
  "references": ["brand/references/ref-1.jpg", ...] (opcional),
  "created_at": "ISO8601"
}
```

### Skill `criar-estatico`

**Description (pushy)**: "Cria um criativo de anúncio único (uma imagem só, não-carrossel) em PNG pronto pra Meta Ads / Google Ads, nos formatos 1:1 (1080×1080), 4:5 (1080×1350) ou 9:16 (1080×1920). Conduz briefing focado em conversão (objetivo, oferta, público, CTA), gera 3 variantes de copy via Gemini para A/B test, lida com a imagem (upload ou geração via Gemini Image), monta o HTML e renderiza via Playwright. Use quando o aluno disser 'criar criativo único', 'anúncio de 1 imagem', 'imagem estática', 'criativo pra Stories', 'ad de uma foto só'. Se ele falar de carrossel ou múltiplos slides, use criar-carrossel."

**Fluxo**:
1. Briefing (uma pergunta por vez): objetivo (vender/lead/promoção/evento), o que é, público, oferta, CTA, formato (1:1/4:5/9:16 — recomenda 4:5)
2. Roda `python3 scripts/gemini_text.py --tipo estatico --formato 4x5 --objetivo ... --produto ... --publico ... --oferta ... --cta ... --tom ... --variantes 3 > /tmp/copy.json`
3. Mostra as 3 variantes (agressiva/racional/emocional) ao aluno e ele escolhe
4. Imagem: upload (`assets/`), Gemini AI (`gemini_image.py --aspect 4x5 --output assets/...`), ou só fundo gradient da marca
5. Render: `python3 scripts/render_slides.py --template templates/static-4x5.html --brand brand/brand-kit.json --copy /tmp/copy.json --variant 1 --image assets/... --output output/estatico-{ts}.png`
6. Tenta abrir automaticamente (`open` Mac, `start` Windows, `xdg-open` Linux)
7. Aceita ajustes iterativos (refazer copy, trocar imagem, mudar fundo, criar variantes A/B)

### Skill `criar-carrossel`

**Description (pushy)**: "Cria um carrossel de anúncio (5-10 slides em sequência) com arco narrativo persuasivo — Hero → Problema → Solução → Features → Detalhes → How-to → CTA. Cada slide vira um PNG 1080×1350px, empacotado em ZIP. Conduz briefing focado em conversão, gera todo o arco via Gemini com responseSchema, lida com imagens slide-a-slide (upload, IA ou só fundo), monta HTML 420×525 e renderiza com Playwright (pixelRatio 2.5714). Use quando o aluno disser 'carrossel', 'vários slides', 'sequência de imagens', 'anúncio de carrossel', 'criar narrativa'."

**Fluxo**:
1. Briefing (uma pergunta por vez): objetivo, o que é, público, dor, transformação, prova social, oferta, CTA, número de slides (default 7)
2. Roda `python3 scripts/gemini_text.py --tipo carrossel --slides 7 ... > /tmp/carrossel.json`
3. Mostra arco completo ao aluno (sem imagens ainda) — aceita ajustes pontuais por slide
4. Imagens: por slide, pergunta upload/IA/sem
5. Render: `python3 scripts/render_slides.py --template templates/carousel-base.html --brand ... --copy ... --output-dir output/carrossel-{ts}/ --zip`
6. Tenta abrir a pasta automaticamente
7. Aceita ajustes (refazer slide específico, reordenar, criar variante completa)

**Componentes opcionais**:
- **Pills riscadas (`legacy_items`)**: o Gemini decide sozinho usar quando a narrativa do briefing tem pivot ("esquece X, Y, Z"). Pra cursos genéricos, omite. Renderizado como pills com `text-decoration: line-through` no slide de problema.
- **Watermark**: logo da marca em opacity 0.05–0.10 nos slides hero/cta/solution. Auto-renderiza se `brand-kit.json` tem `logo_path` apontando pra arquivo válido. Sem logo, sem watermark.

---

## Scripts Python (5)

### `scripts/requirements.txt`
```
google-genai>=0.3.0
playwright>=1.45.0
python-dotenv>=1.0.0
Pillow>=10.0.0
```

### `scripts/derive_palette.py`

CLI que recebe `--primary "#hex"` e gera os 6 tokens de paleta via `colorsys` (built-in Python, sem dep extra).

**Lógica**:
- `BRAND_PRIMARY` = cor do usuário
- `BRAND_LIGHT` = primary com `lightness +0.20` (HLS)
- `BRAND_DARK` = primary com `lightness -0.30`
- Detecta temperatura (warm: hue 0–60° ou 300–360°; cool: 60–300°)
- Warm → `LIGHT_BG=#FAF9F7`, `DARK_BG=#1A1918`
- Cool → `LIGHT_BG=#F8F9FB`, `DARK_BG=#0F172A`
- `LIGHT_BORDER` = LIGHT_BG com `lightness -0.05`
- `BRAND_GRADIENT` = `linear-gradient(165deg, BRAND_DARK 0%, BRAND_PRIMARY 50%, BRAND_LIGHT 100%)`

**Args**: `--primary` (obrigatório), `--output` (path do JSON), `--append` (mescla em JSON existente preservando outros campos), `--validate` (valida arquivo existente — exige `tokens` mas avisa se faltam name/handle/fontes).

### `scripts/gemini_text.py`

Gera copy de anúncio via Gemini 2.5 Flash com `responseSchema` (JSON garantido).

**Args**:
- `--test` — ping mínimo (retorna `OK` ou erro descritivo)
- `--tipo` — `carrossel` | `estatico`
- `--slides` — 5 a 10 (carrossel)
- `--variantes` — 3 (estático)
- `--formato` — `1x1` | `4x5` | `9x16` (estático)
- `--objetivo`, `--produto`, `--publico`, `--dor`, `--transformacao`, `--prova-social`, `--oferta`, `--cta`, `--tom` — campos do briefing

**Schemas**:

Carrossel:
```json
{
  "slides": [
    {
      "type": "hero|problem|solution|features|details|how_to|cta",
      "tag": "string uppercase curta",
      "headline": "string",
      "subheadline": "string?",
      "body": "string?",
      "items": ["string"]?,
      "legacy_items": ["string"]?,  // pills riscadas — só em problem
      "features": [{"icon": "char", "label": "string", "desc": "string"}]?,
      "steps": [{"title": "string", "desc": "string"}]?,
      "quote": "string?",
      "cta_text": "string?",
      "image_prompt": "string em inglês ou null"
    }
  ],
  "caption": "string",
  "image_keywords": {"slide1": "string"}
}
```

Estático:
```json
{
  "variants": [
    {
      "style": "agressivo|racional|emocional",
      "headline": "string",
      "subheadline": "string?",
      "body": "string?",
      "cta_text": "string"
    }
  ],
  "caption": "string",
  "image_prompt": "string?"
}
```

**System prompts** (em português):
- Carrossel: hook em 1s, dor concreta, CTA específico, arco, headline curta. Estrutura por tipo de slide. **legacy_items**: usar APENAS quando briefing menciona pivot/substituição (esquece X), comparativo com concorrentes nomeados ou "cansou de Y". NÃO usar quando dor é genérica.
- Estático: 3 variantes obrigatórias (agressiva/racional/emocional). Headline 7-9 palavras max. CTA específico. JSON estrito.

**Detalhes de implementação**:
- `load_dotenv(PROJECT_ROOT / ".env", override=True)` — `override=True` é CRÍTICO porque o ambiente do usuário pode ter `GEMINI_API_KEY` de outras integrações (Cloud Workstation, gcloud) que sobrescreveriam a chave do .env
- Cliente: `genai.Client(api_key=os.getenv("GEMINI_API_KEY"))`
- `response_mime_type="application/json"` + `response_schema=SCHEMA` no `GenerateContentConfig`
- Retry simples (1 tentativa) em 500/503
- Tratamento de erros: 401/403 (chave inválida → exit 3), 429 (cota → exit 4), genérico → exit 1
- `--test` faz `generate_content` com prompt mínimo "diga apenas a palavra OK"

### `scripts/gemini_image.py`

Gera imagem via Gemini 2.5 Flash Image (Nano Banana).

**Args**: `--prompt` (obrigatório), `--aspect` (`1x1`|`4x5`|`9x16`|`16x9`), `--style` (opcional, ex: "editorial photography"), `--output` (path).

**Notas**:
- Modelo Gemini Image só retorna 1024×1024 hoje. O aspect ratio entra como dica no prompt; o crop final é feito pelo CSS no template (object-fit: cover).
- Resposta vem em `parts[].inline_data.data` (bytes ou base64). Suporta ambos.
- `load_dotenv(..., override=True)` igual ao gemini_text
- Tratamento de erro de safety filter (400 INVALID_ARGUMENT): exit 5 com instrução de reescrever prompt mais neutro

### `scripts/render_slides.py`

Render Playwright HTML → PNG.

**Layout fixo (do prompt-base do projeto)**:
- Viewport: 420 × N (525 pra carrossel/4:5, 420 pra 1:1, 747 pra 9:16)
- `device_scale_factor = 1080 / 420 = 2.5714` → output em 1080×N

**Funções**:
- `encode_image_base64(path)` — embute imagens como data URI. Detecta MIME por extensão e fallback por header. Suporta PNG/JPG/SVG/WebP/GIF. Crítico pra imagens externas funcionarem no headless browser.
- `replace_placeholders(html, mapping)` — substitui `{{KEY}}` → `value` via Python `.replace()`. **NUNCA via shell** (heredoc, sed, awk corrompem `$`, crases, dígitos).
- `build_brand_mapping(brand)` — gera dict de placeholders globais: BRAND_NAME, BRAND_HANDLE, LOGO_INITIAL, LOGO_DATA_URI (se brand.logo_path existe, embute), BRAND_PRIMARY, BRAND_LIGHT, BRAND_DARK, LIGHT_BG, LIGHT_BORDER, DARK_BG, BRAND_GRADIENT, HEADING_FONT, BODY_FONT
- `render_html_to_png(html, output, slide_height, wait_fonts_ms=3000)` — Playwright launch chromium, set_content, evaluate `document.fonts.ready`, wait_for_timeout, screenshot com clip exato
- `render_carousel(html, output_dir, total_slides, slide_height=525)` — esconde IG frame chrome (`.ig-header`, `.ig-dots`, `.ig-actions`, `.ig-caption` se existirem), itera os slides movendo `.carousel-track` com `transform: translateX(-i * 420px)` + `transition: none`, screenshot por slide
- Estático: substitui placeholders incluindo HEADLINE/SUBHEADLINE/BODY_TEXT/CTA_TEXT/IMAGE_SRC (base64) e renderiza
- Carrossel: serializa slides como JSON e injeta em `{{SLIDES_DATA_JSON}}` (com `</` escapado pra evitar quebra), o template renderiza via JS no client. Após render, gera `README.txt` com caption e empacota tudo em ZIP.

**Args**: `--template`, `--brand`, `--copy`, `--variant` (estático), `--image` (estático), `--images` (carrossel — JSON de slide_id → path), `--output` (estático), `--output-dir` (carrossel), `--zip` (flag), `--wait-fonts` (ms).

### `scripts/analyze_references.py`

Extrai paleta dominante de imagens via k-means simples sobre pixels (Pillow).

**Args**: `--dir` ou `--files`, `--top` (default 5), `--output` (JSON).

**Lógica**:
- Quantiza pixels em buckets (default 32)
- Filtra grayscale (variação RGB < 12) e extremos (avg < 30 ou > 235) — pretos/brancos puros geralmente são fundo, não cor de marca
- Conta frequência, retorna top N por imagem + agregado
- Sugere `primary_color` = cor agregada dominante

---

## Templates HTML (4)

### Princípios comuns

- Carrega Google Fonts no `<head>` (Plus Jakarta Sans, Playfair, DM Sans, Lora, Nunito Sans, Space Grotesk, Fraunces, Outfit, Libre Baskerville, Work Sans, Bricolage Grotesque, Inter)
- Layout em **420px de largura** (renderiza 1080px via device_scale_factor)
- CSS com variáveis: `--brand-primary`, `--brand-light`, `--brand-dark`, `--light-bg`, `--light-border`, `--dark-bg`, `--brand-gradient`, `--heading-font`, `--body-font`
- Placeholders `{{KEY}}` substituídos pelo render_slides.py em Python

### `templates/carousel-base.html`

420×525, com `.carousel-track` flex horizontal e slides empilhados.

**CSS necessário**:
- `.slide.bg-light` (LIGHT_BG, texto preto)
- `.slide.bg-dark` (DARK_BG, texto branco)
- `.slide.bg-gradient` (BRAND_GRADIENT, texto branco)
- `.slide-content` (padding 36px lateral, 52px bottom pra clear progress bar)
- Justify-center pra hero/cta/solution; justify-end pra problem/features/etc
- `.tag` (10px uppercase letter-spacing 2px, cor adapta ao bg)
- `.heading` (heading-font, 30px weight 600, line-height 1.12)
- `.subheading` (body-font, 14px, opacity 0.78)
- `.body-text`, `.hero-image`, `.logo-lockup`, `.logo-circle`, `.brand-name`
- `.items-list` com `::before` content "—"
- **`.legacy-pills` + `.pill`**: flex wrap, gap 8px, pill com border-radius 24px, padding 6px 14px, fonte 11.5px weight 500, `text-decoration: line-through`. Adapta cor pra bg claro/escuro.
- `.features-list` / `.feature-row` / `.feature-icon` (16px, BRAND_PRIMARY)
- `.steps-list` / `.step-row` / `.step-num` (heading-font 24px weight 300, BRAND_PRIMARY)
- `.quote-box` (rgba(0,0,0,0.18), border-radius 10px, texto itálico)
- `.cta-button` (LIGHT_BG bg, BRAND_DARK text, border-radius 28px, padding 12-13px × 24px)
- `.progress-bar` (absolute bottom, 16px 28px 20px, track 3px, fill BRAND_PRIMARY ou white conforme bg)
- `.swipe-arrow` (right 0, 40px wide, gradient fade, chevron SVG, opacity 0.6)
- **`.watermark`**: position absolute, right -30px bottom -30px, 220px square, opacity 0.05–0.10 conforme bg, z-index 0. `.slide-content` recebe z-index 1 pra ficar acima.

**JS injetado no body**:
- Lê `SLIDES_DATA = {{SLIDES_DATA_JSON}}`, `TOTAL = {{TOTAL_SLIDES}}`, `BRAND_NAME`, `BRAND_INITIAL`, `BRAND_LOGO_DATA_URI`
- `WATERMARK_TYPES = new Set(['hero', 'cta', 'solution'])`
- Função `bgClassFor(type, index)` mapeia: hero→light, problem→dark, solution→gradient, features→light, details→dark, how_to→light, cta→gradient. Default alternância.
- Função `renderSlideBody(slide)` switch por type — incluir caso `problem` que renderiza pills (`legacy_items`) ANTES dos items
- Função `renderSlide` — adiciona `<div class="watermark">...</div>` se `BRAND_LOGO_DATA_URI` está presente E `WATERMARK_TYPES.has(slide.type)`
- Último slide (`index === total - 1`) NÃO recebe swipe-arrow
- Progress bar: width `((index + 1) / total) * 100%`, counter `(index + 1)/total`

### `templates/static-4x5.html` (recomendado/default)

420×525, fundo gradient por padrão (sem imagem) ou DARK_BG (com imagem).

**Layout**:
- Top: logo lockup, tag "ANÚNCIO", headline grande, subheadline, body
- Bottom: CTA pill alinhado à esquerda + handle abaixo
- Se `IMAGE_SRC` preenchida: imagem ocupa topo (260px de altura) com gradient fade pro DARK_BG; senão, padding maior e justify-center

**JS** (no final do body): se `imgSrc` não-vazio, mostra `.ad-image-wrapper` e adiciona classe `.has-image` ao `.ad`. Esconde subheadline/body se vazios.

### `templates/static-1x1.html`

420×420 (renderiza 1080×1080). Layout grid 2 colunas: imagem esquerda 50%, conteúdo direita 50% (com imagem); ou conteúdo full width centrado (sem imagem).

### `templates/static-9x16.html`

420×747 (renderiza 1080×1920). Imagem fullbleed com overlay gradient escuro do bottom; conteúdo distribuído verticalmente (top: logo; middle: tag/headline/subheadline; bottom: CTA + handle).

---

## Documentação auxiliar

### `docs/design-system.md`

Cobrir: tokens (regras de derivação), pareamentos de fonte (7 IDs com Google Fonts), escala de tamanho, layout 420×525 e por que essa largura, padding padrão, elementos sempre presentes (progress bar e swipe arrow), componentes reutilizáveis (tag, CTA button, logo lockup, quote box, feature row, step row, **strikethrough pills**, **watermark**), anti-padrões (não usar #FFFFFF/#000000 puros, não usar headlines longas, não usar CTAs genéricos), acessibilidade básica.

### `docs/prompts-gemini.md`

Cobrir: 6 leis de headline de anúncio, 3 variantes obrigatórias (agressiva/racional/emocional), arco de carrossel 7-slide com função de cada slide, **tabela "quando usar legacy_items"**, prompts de imagem (estrutura, estilos, iluminação, o que sempre/nunca incluir, fallbacks pra safety filter), caption (princípios), tom de voz (4 estilos com exemplos), cuidados éticos (sem promessas garantidas, sem termos médicos, sem antes/depois sem disclaimer).

---

## Decisões técnicas críticas (não mudar)

1. **Layout 420px com `device_scale_factor=2.5714`** — render Playwright em 420px e escala. NÃO mudar pra 1080px direto (reflow do CSS quebra tudo). Vem do prompt-base do projeto.

2. **`load_dotenv(..., override=True)`** — sem isso, `GEMINI_API_KEY` no ambiente da shell sobrescreve a do `.env`. Bug confirmado na implementação inicial.

3. **Substituição de placeholders SEMPRE em Python**, nunca shell — heredocs, sed, awk corrompem `$`, crases e dígitos no HTML.

4. **`responseSchema` no Gemini** — garante JSON estruturado, dispensa parsing manual.

5. **Imagens embutidas em base64** no HTML antes do render — paths relativos podem falhar no headless browser.

6. **`document.fonts.ready` + 3s buffer** antes do screenshot — sem isso, fontes web carregam após captura.

7. **PEP 668 esperado em Mac/Linux com Python do Homebrew** — solução é venv (`python3 -m venv .venv && source .venv/bin/activate && pip install ...`). Documentado no skill `verificar-setup`.

8. **Skill que cria `.env` pro aluno** (Write tool) — leigo não consegue criar arquivo oculto manualmente. Esse fluxo é o que torna o projeto realmente friendly pra leigo.

9. **Pills riscadas com `legacy_items`** — Gemini decide sozinho via system prompt quando usar. Pra briefing com pivot ("substitui Photoshop") usa; pra dor genérica ("não falo inglês") omite.

10. **Watermark condicional** — só renderiza se `brand-kit.json` tem `logo_path` válido. Suporta SVG/PNG/JPG/WebP via mimetype detection.

---

## Validação esperada (depois de construir)

Tudo deve passar:

```bash
# 1. Sintaxe Python
python3 -c "import ast; [ast.parse(open(f).read(), filename=f) for f in ['scripts/derive_palette.py', 'scripts/gemini_text.py', 'scripts/gemini_image.py', 'scripts/render_slides.py', 'scripts/analyze_references.py']]"

# 2. Paleta gerada corretamente
python3 scripts/derive_palette.py --primary "#6366F1"
# (deve retornar JSON com 6 tokens + gradient)

python3 scripts/derive_palette.py --primary "#E55934"
# (cor warm — LIGHT_BG deve ser #FAF9F7, DARK_BG #1A1918)

# 3. Validação de brand-kit
python3 scripts/derive_palette.py --primary "#6366F1" --output /tmp/test.json
python3 scripts/derive_palette.py --validate /tmp/test.json
# (deve dar OK com aviso de campos opcionais faltando)

# 4. Com chave Gemini configurada:
python3 scripts/gemini_text.py --test          # → OK
python3 scripts/gemini_text.py --tipo carrossel --slides 7 --objetivo "lead" --produto "X" --publico "Y" --cta "Z"  # → JSON válido
python3 scripts/gemini_image.py --prompt "..." --aspect 4x5 --output /tmp/img.png  # → PNG criado

# 5. Com chave + Playwright + brand-kit:
python3 scripts/render_slides.py --template templates/carousel-base.html --brand brand/brand-kit.json --copy /tmp/copy.json --output-dir /tmp/test/ --zip
# → 7 PNGs 1080×1350 + ZIP
```

E o fluxo conversacional ponta-a-ponta dentro do Claude Code:
1. Aluno manda "oi"
2. Claude detecta primeira vez, conduz onboarding
3. Pega chave Gemini no chat → Claude cria `.env` via Write
4. Instala dependências (com permissão)
5. Configura marca (briefing direto OU análise de refs)
6. Cria primeiro carrossel
7. PNGs aparecem em `output/`

---

## Como construir

Vai sequencialmente, um arquivo por vez. **Pra cada arquivo, use o conhecimento da especificação acima** — não tem como faltar contexto. Quando terminar tudo:

1. Valida sintaxe Python (comando 1 acima)
2. Mostra a árvore final ao usuário
3. Pergunta se ele quer testar end-to-end (precisa de chave Gemini)

Se algo for ambíguo, NÃO chuta — pergunta ao usuário. Se algum arquivo passar de 500 linhas, considera dividir em referências (`docs/` ou referências dentro do skill).

**Comece agora.**
````

---

## 🧪 Como testar este prompt

1. Crie uma pasta vazia
2. Abra no Claude Code Desktop
3. Cola o conteúdo dentro do bloco ` ```` ` acima na conversa (ou escreva "execute o PROMPT-CONSTRUCAO.md" se este arquivo já estiver na pasta)
4. Confirma cada passo
5. No fim, valida com os comandos da seção "Validação esperada"

Se o resultado não bater 1:1 com o repo original, ajusta o prompt — provavelmente faltou alguma instrução crítica.

---

## 📦 O que o prompt entrega

- ✅ Projeto Claude Code completo com `CLAUDE.md` + 4 skills + 5 scripts + 4 templates + 2 docs
- ✅ Onboarding leigo automático (Claude cria `.env` pelo aluno)
- ✅ Cross-platform (Mac/Linux/Windows com Git Bash)
- ✅ Geração de copy estruturada via Gemini 2.5 Flash + responseSchema
- ✅ Geração de imagem via Gemini 2.5 Flash Image
- ✅ Render Playwright em 1080×1350 via device_scale_factor 2.5714
- ✅ Pills riscadas + watermark condicionais
- ✅ Fluxo de marca com análise de imagens de referência (capacidade multimodal)
- ✅ Documentação interna (design system + princípios de copy)
