# Plano Técnico — imersao-sac-agente-design

> Template de criação de criativos de anúncio (estático ou carrossel) usando IA, **operado dentro do Claude Code Desktop**. Aluno baixa a pasta, abre no Claude e conversa — o Claude conduz tudo.

---

## 1. Visão geral

**Não é um app web.** É um **projeto Claude Code** que transforma o Claude num agente especializado em criar criativos de anúncio para Meta Ads / Google Ads.

### Como o aluno usa
1. Instala Claude Code Desktop (Mac ou Windows)
2. Baixa esta pasta
3. Roda o setup uma vez (Python + Playwright + chave Gemini)
4. Abre a pasta no Claude Code
5. Manda uma mensagem tipo "quero criar um anúncio do meu curso"
6. Claude conduz por perguntas, gera os PNGs em `output/`

### O que o Claude faz internamente
- Lê `CLAUDE.md` ao abrir a pasta → sabe que é um agente de design
- Verifica setup (Python, Playwright, `.env`) — instala/orienta se faltar
- Carrega skills sob demanda (`.claude/skills/*`)
- Conversa: faz perguntas certas, sem jargão técnico
- Chama Gemini API via scripts Python (texto e imagem)
- Monta HTML do criativo a partir de templates
- Renderiza via Playwright em PNG 1080×1350 (carrossel) ou 1080×1080 / 1080×1350 / 1080×1920 (estático)
- Mostra o resultado ao aluno e permite ajustes iterativos

### Foco: anúncios (não conteúdo orgânico)
- Hook agressivo (parar scroll em 1s)
- CTA claro
- Variantes de copy (3 versões pra A/B test)
- Briefing focado em oferta, público, dor, transformação

---

## 2. Estrutura de arquivos

```
imersao-sac-agente-design/
├── CLAUDE.md                          # Entry point — instruções principais do agente
├── README.md                          # Setup pro aluno leigo
├── PLANO.md                           # Este arquivo
├── .env.example                       # GEMINI_API_KEY=
├── .gitignore                         # Ignora .env, output/, node_modules
│
├── .claude/
│   └── skills/
│       ├── verificar-setup/
│       │   └── SKILL.md               # Checa Python, Playwright, .env
│       ├── configurar-marca/
│       │   └── SKILL.md               # Briefing de marca + análise de imagens de referência
│       ├── criar-estatico/
│       │   └── SKILL.md               # Fluxo guiado de criativo único
│       └── criar-carrossel/
│           └── SKILL.md               # Fluxo guiado de carrossel
│
├── docs/
│   ├── design-system.md               # Tokens, fontes, padrões visuais
│   ├── prompts-gemini.md              # Prompts de copy para Gemini
│   └── exemplos-anuncios.md           # Exemplos de bons anúncios pra referência
│
├── templates/
│   ├── carousel-base.html             # HTML 420px do prompt original (carrossel)
│   ├── static-1x1.html                # 1080×1080
│   ├── static-4x5.html                # 1080×1350
│   └── static-9x16.html               # 1080×1920 (stories/reels)
│
├── scripts/
│   ├── requirements.txt               # google-genai, playwright, pillow
│   ├── gemini_text.py                 # Chama Gemini 2.5 Flash (copy + JSON)
│   ├── gemini_image.py                # Chama Gemini 2.5 Flash Image
│   ├── render_slides.py               # Playwright → PNG 1080×N
│   ├── derive_palette.py              # 1 cor primária → 6 tokens
│   └── analyze_references.py          # Analisa imagens de referência (multimodal Gemini)
│
├── brand/                             # Brand kit do aluno (gerado pelo skill)
│   ├── brand-kit.json                 # cor, fontes, handle, tom
│   ├── logo.png                       # opcional
│   └── references/                    # imagens de inspiração que o aluno enviou
│
├── assets/                            # Aluno coloca fotos do produto aqui
│
└── output/                            # PNGs gerados ficam aqui
    └── .gitkeep
```

---

## 3. Stack técnica

| Camada | Escolha | Por quê |
|---|---|---|
| Orquestração | Claude Code Desktop | É o "frontend" — o aluno interage por chat |
| Linguagem dos scripts | Python 3.10+ | google-genai SDK oficial é Python, Playwright Python é estável |
| IA texto | Gemini 2.5 Flash | Rápido, JSON estruturado via responseSchema, 1500 req/dia grátis |
| IA imagem | Gemini 2.5 Flash Image (Nano Banana) | Único Google que retorna imagem direta |
| Render | Playwright (Chromium headless) | Igual ao prompt original — exporta PNG fiel ao HTML |
| Templates | HTML + CSS puro | Aluno enxerga e edita facilmente |
| Cor utility | Python colorsys (built-in) | Sem dep extra pra derivar paleta |

**Dependências que o aluno precisa instalar:**
- Claude Code Desktop (já tem se está usando)
- Python 3.10+
- `pip install -r scripts/requirements.txt`
- `playwright install chromium`
- Chave Gemini em `.env`

---

## 4. Fluxos principais (skills)

### 4.1 verificar-setup
Roda quando o aluno abre o projeto pela primeira vez ou quando algum comando falha.

Checa em ordem:
1. `python3 --version` (≥ 3.10)
2. `pip show google-genai playwright` (instalados?)
3. `playwright install --dry-run chromium` (chromium instalado?)
4. `.env` existe e tem `GEMINI_API_KEY` válida?

Se algum falhar: pergunta se pode instalar (com permissão do aluno) ou mostra comando manual.

### 4.2 configurar-marca
Roda na primeira execução ou quando aluno pede pra mudar marca.

**Caso A — aluno tem identidade visual definida:**
- Pergunta: cor primária (hex), fonte preferida (ou estilo), nome da marca, handle, tom de voz, logo (opcional)
- Salva em `brand/brand-kit.json`

**Caso B — aluno NÃO tem identidade definida:**
- Pergunta: "você tem imagens de design que goste? (anúncios, sites, posts) Pode anexar 2-5 referências"
- Aluno arrasta imagens no Claude Code Desktop
- Claude analisa visualmente (capacidade multimodal nativa) + opcionalmente roda `scripts/analyze_references.py` para extrair paleta dominante
- Sugere cor primária, mood (editorial/moderno/playful), tipografia, e justifica cada escolha
- Aluno aprova ou ajusta
- Salva em `brand/brand-kit.json`

**brand-kit.json:**
```json
{
  "name": "Acme Co",
  "handle": "@acme",
  "tone": "profissional e direto",
  "primary_color": "#6366f1",
  "heading_font": "Plus Jakarta Sans",
  "body_font": "Plus Jakarta Sans",
  "logo_path": "brand/logo.png",
  "tokens": {
    "BRAND_PRIMARY": "#6366f1",
    "BRAND_LIGHT": "#a5b4fc",
    "BRAND_DARK": "#3730a3",
    "LIGHT_BG": "#faf9f7",
    "LIGHT_BORDER": "#e8e5e0",
    "DARK_BG": "#1a1918"
  }
}
```

### 4.3 criar-estatico
Fluxo guiado:
1. Pergunta o objetivo do anúncio (curso, produto, lead, etc)
2. Pergunta público-alvo, oferta, CTA
3. Pergunta formato (1:1 feed, 4:5 mobile, 9:16 stories)
4. Chama `gemini_text.py` → 3 variantes de copy (headline + body + CTA)
5. Aluno escolhe variante
6. Pergunta sobre imagem: upload (`assets/`), gerar com IA (`gemini_image.py`) ou só fundo da marca
7. Monta HTML do template apropriado, substitui placeholders
8. Renderiza com `render_slides.py`
9. Mostra PNG → aluno aprova ou pede ajuste
10. Salva em `output/estatico-{timestamp}.png`

### 4.4 criar-carrossel
Mesmo fluxo, mas para 5–10 slides seguindo o arco do prompt original:
Hero → Problema → Solução → Features → Detalhes → How-to → CTA

1. Briefing completo (oferta, dor, transformação, prova social, CTA)
2. Pergunta quantidade de slides (default: 7)
3. Gemini gera arco completo via responseSchema
4. Por slide, pergunta se quer imagem (upload, IA ou pular)
5. Monta HTML 420×525 do template
6. Render Playwright → 7 PNGs 1080×1350
7. Empacota em ZIP em `output/carrossel-{timestamp}.zip`
8. Mostra resultado

---

## 5. Decisões técnicas chave

### 5.1 Por que Python e não Node?
- google-genai SDK oficial em Python é mais maduro
- Playwright Python tem melhor compatibilidade no Claude Code Bash
- Aluno provavelmente já vai precisar de Python pra outras coisas em IA

### 5.2 Por que Playwright e não html-to-image?
- O prompt original já especifica Playwright com `device_scale_factor=2.5714`
- Fidelidade superior em fonts/CSS complexo
- Sem browser do aluno envolvido — roda headless

### 5.3 Por que skills no `.claude/skills/`?
- Padrão Claude Code para fluxos invocáveis
- Cada skill tem instruções dedicadas (tabela de perguntas, prompts Gemini, validações)
- Carregadas sob demanda, não poluem CLAUDE.md principal

### 5.4 Por que `responseSchema` no Gemini?
- Garante JSON estruturado (sem precisar parsear texto)
- Reduz erros de "IA inventou campo"
- Validação automática

### 5.5 Por que .env com GEMINI_API_KEY direto?
- Mais simples pro aluno leigo (sem keychain, sem secret manager)
- `.gitignore` previne commit acidental
- README explica como pegar a chave

---

## 6. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Aluno não tem Python instalado | Skill verificar-setup detecta e mostra link de download |
| Playwright Chromium download lento (200MB) | README avisa que primeira instalação demora |
| Gemini retorna JSON malformado | responseSchema + retry 1x + fallback pra parser tolerante |
| Imagem AI não combina com produto real | UX padrão é upload do `assets/`; AI é fallback pra ilustração |
| Aluno sem chave Gemini | README com tutorial passo-a-passo do AI Studio |
| Aluno tem chave mas excedeu cota grátis | Mensagem clara: "cota Gemini esgotada, espera 24h ou aumenta limite" |
| Texto muito longo estoura layout | Script tem AUTOFIT (reduz fontSize iterativamente) |
| Aluno tem dúvida no meio do fluxo | Skills foram desenhados pra retomar de qualquer ponto |

---

## 7. Fases de build

| Fase | Entrega |
|---|---|
| **0** | Limpeza Next.js + reescrita do PLANO ✅ |
| **1** | CLAUDE.md principal |
| **2** | README.md (setup leigo-friendly) |
| **3** | Skills básicos: verificar-setup + configurar-marca |
| **4** | Skills criadores: criar-estatico + criar-carrossel |
| **5** | Templates HTML (carrossel + 3 estáticos) |
| **6** | Scripts Python (Gemini text/image + Playwright + paleta + análise referências) |
| **7** | Docs auxiliares (design-system + prompts-gemini) |
| **8** | Testes manuais + ajustes |

---

## 8. Próximos passos

Construir tudo de cima pra baixo, na ordem das fases. Validar com aluno-teste no fim.
