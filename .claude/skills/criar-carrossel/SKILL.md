---
name: criar-carrossel
description: Cria um carrossel de anúncio (5 a 10 slides em sequência) com arco narrativo persuasivo - Hero → Problema → Solução → Features/Detalhes → How-to → CTA. Cada slide vira um PNG 1080×1350px pronto pra subir no Meta Ads, empacotado em ZIP. Conduz briefing focado em conversão (oferta, dor, transformação, prova social, CTA), gera todo o arco de copy via Gemini com responseSchema, lida com imagens slide-a-slide (upload, geração via Gemini Image ou só fundo da marca), monta o HTML 420×525px do prompt-base e renderiza via Playwright com pixelRatio 2.5714. Use quando o aluno disser "carrossel", "vários slides", "sequência de imagens", "post de múltiplas fotos", "anúncio de carrossel", "slides em sequência", "criar uma narrativa", "vou contar uma história", "anúncio com vários frames", ou quando o briefing dele claramente precisar de mais de uma imagem pra contar a oferta. Se ele falar de uma imagem só, use criar-estatico em vez desta.
---

# Skill: criar-carrossel

Cria um carrossel de anúncio em formato 4:5 (1080×1350) seguindo o arco narrativo do projeto-base. O resultado é um ZIP com 5-10 PNGs prontos pra subir no Meta Ads.

## Pré-requisitos

Antes de invocar, garanta:
1. Setup foi validado nesta sessão (`verificar-setup`). Se não, invoque antes.
2. `brand/brand-kit.json` existe e tá preenchido. Se não, invoque `configurar-marca` antes.

Esses passos não são burocracia — são pra evitar erro confuso no meio do fluxo (Python sem dependências, brand kit faltando colorindo o slide errado).

## Quando invocar

Aluno disse algo como:
- "criar carrossel"
- "anúncio com vários slides"
- "sequência de imagens"
- "vários frames de anúncio"
- "post de múltiplas fotos"
- "vou contar uma história em slides"

## Fluxo passo-a-passo

### Passo 1 — Briefing focado em conversão

Faça as perguntas **uma de cada vez**, com sugestões. Não jogue um questionário gigante.

1. **Objetivo**
   > "Pra que serve esse carrossel?
   > 1. Vender produto/serviço (carrinho aberto)
   > 2. Capturar lead (email, WhatsApp, formulário)
   > 3. Anunciar lançamento / pré-venda
   > 4. Promover evento ou aula gratuita
   > 5. Outro (descreva)"

2. **O que está sendo anunciado**
   > "Me conta em 2-3 frases o que é. Ideal incluir: o que oferece, pra quem, e qual transformação promete."

3. **Público-alvo**
   > "Quem é o público? Quanto mais específico, melhor a copy. Tipo: 'mulheres 30-45 que querem emagrecer mas não têm tempo pra academia' é bem melhor que 'pessoas que querem emagrecer'."

4. **A dor / problema**
   > "Qual a dor principal que esse público tem? O que tira o sono dessa pessoa hoje, antes de comprar de você?"

5. **A transformação prometida**
   > "Como a vida dele muda depois de comprar? Foca no resultado prático, não na feature do produto."

6. **Prova social (opcional)**
   > "Tem prova social? Número de clientes, depoimentos, resultado mensurável, certificação. Pode pular se não tiver."

7. **Oferta concreta**
   > "Tem oferta específica? Preço, bônus, garantia, desconto, parcelamento. Pode pular se não tiver."

8. **CTA**
   > "O que você quer que a pessoa faça depois do último slide?
   > 1. Comprar agora (link na bio / site)
   > 2. Se inscrever / cadastrar
   > 3. Falar no WhatsApp
   > 4. Baixar material grátis
   > 5. Saber mais (genérico — só use se nada acima encaixa)"

9. **Quantidade de slides**
   > "Quantos slides? O ideal pra anúncio são **7** (Hero → Problema → Solução → Features → Detalhes → How-to → CTA). Mas pode ser de 5 a 10. Te recomendo 7."

### Passo 2 — Gera o arco completo via Gemini

Dispara o script com todo o briefing:

```bash
python3 scripts/gemini_text.py \
  --tipo carrossel \
  --slides 7 \
  --objetivo "captar lead" \
  --produto "curso de inglês online em 60 dias" \
  --publico "profissionais 25-45 que precisam falar inglês no trabalho" \
  --dor "perder oportunidades por não falar inglês" \
  --transformacao "falar com confiança em reuniões e entrevistas" \
  --prova-social "+2.000 alunos transformados" \
  --oferta "primeira aula grátis + ebook de fluência" \
  --cta "se inscrever" \
  --tom "profissional e direto" \
  > /tmp/carrossel-{ts}.json
```

O script retorna JSON estruturado (responseSchema do Gemini, garantindo formato):

```json
{
  "slides": [
    {
      "type": "hero",
      "tag": "ANÚNCIO",
      "headline": "Pare de perder oportunidades por causa do inglês",
      "subheadline": "Em 60 dias falando com confiança",
      "image_prompt": "professional in modern office, confident posture"
    },
    {
      "type": "problem",
      "tag": "O PROBLEMA",
      "headline": "Você sabe o que vai dizer, mas trava",
      "items": [
        "Perde a vez nas reuniões",
        "Evita entrevistas em multinacionais",
        "Sente que tá sempre 'atrás' dos colegas"
      ],
      "image_prompt": "frustrated person in front of laptop"
    },
    {
      "type": "solution",
      "tag": "A SOLUÇÃO",
      "headline": "Método focado em conversação real do trabalho",
      "body": "Aulas práticas com situações que você vive todo dia",
      "quote": "'Em 30 dias eu já tava fazendo reunião em inglês.' — Carla, gerente de marketing",
      "image_prompt": null
    },
    { "type": "features", "tag": "O QUE VOCÊ GANHA", "headline": "Tudo incluído", "features": [
      { "icon": "▶", "label": "60 horas de aulas", "desc": "Acesso vitalício" },
      { "icon": "✦", "label": "Comunidade ativa", "desc": "Pratica com outros alunos" },
      { "icon": "◆", "label": "Mentorias mensais", "desc": "Ao vivo com professor nativo" }
    ] },
    { "type": "details", "tag": "COMO FUNCIONA", "headline": "Aprende no seu ritmo", "items": ["..."], "image_prompt": "..." },
    { "type": "how_to", "tag": "PASSO A PASSO", "headline": "Em 3 passos simples", "steps": [
      { "title": "Inscreva-se", "desc": "Acessa a primeira aula grátis" },
      { "title": "Estude no seu ritmo", "desc": "Conteúdo destravado por nível" },
      { "title": "Pratique com a comunidade", "desc": "Encontros semanais ao vivo" }
    ] },
    {
      "type": "cta",
      "tag": "COMECE AGORA",
      "headline": "Sua primeira aula é grátis",
      "subheadline": "Sem cartão. Sem compromisso.",
      "cta_text": "Quero minha aula grátis"
    }
  ],
  "caption": "Cansou de travar nas reuniões em inglês? Em 60 dias você fala com confiança...",
  "image_keywords": {
    "slide1": "professional confident office",
    "slide2": "frustrated laptop work",
    "slide5": "studying laptop home"
  }
}
```

### Passo 3 — Mostra o arco ao aluno (sem imagens ainda)

Apresenta de forma legível:

> "Esse é o arco que o Gemini gerou. Dá uma olhada e me fala o que ajustar:
>
> **Slide 1 (Hero)** — *"Pare de perder oportunidades por causa do inglês"*
> Em 60 dias falando com confiança
>
> **Slide 2 (Problema)** — *"Você sabe o que vai dizer, mas trava"*
> • Perde a vez nas reuniões
> • Evita entrevistas em multinacionais
> • Sente que tá sempre 'atrás' dos colegas
>
> **Slide 3 (Solução)** — *"Método focado em conversação real do trabalho"*
> ...
>
> **Slide 7 (CTA)** — *"Sua primeira aula é grátis"*
> CTA: "Quero minha aula grátis"
>
> Tá bom assim ou quer ajustar algum slide específico? Posso reescrever só o que você apontar."

Aceita ajustes pontuais ("refaz o slide 2 mais agressivo", "muda a headline do hero pra ficar pergunta") sem regenerar tudo.

### Passo 4 — Imagens slide-a-slide

Pergunta o critério geral:

> "Sobre as imagens dos slides:
> 1. **Tenho fotos pra usar** — me passa as fotos que você tem (do produto, suas, do resultado) e eu encaixo nos slides certos
> 2. **Gera tudo com IA** — uso o image_prompt de cada slide e gero ilustrações via Gemini
> 3. **Misto** — você manda fotos pra alguns slides, IA cobre o resto
> 4. **Sem imagens** — só fundos da marca (gradient/sólido) com o texto"

#### Para cada slide que precisa de imagem AI:

```bash
python3 scripts/gemini_image.py \
  --prompt "professional confident in modern office, soft natural light, editorial photography" \
  --aspect 4x5 \
  --output assets/carousel-{ts}-slide-1.png
```

Mostra a imagem gerada ao aluno antes de prosseguir. Se não gostar, regera com prompt ajustado (não regera todas — só a que ele rejeitou).

#### Para uploads:

- Aluno arrasta foto no chat ou passa caminho
- Salva em `assets/` se ainda não tá lá
- Confere dimensões (`PIL.Image.open(...).size`) — se for menor que 800×1000px, alerta sobre qualidade na hora de exportar

### Passo 5 — Monta o HTML do carrossel

Carrega `templates/carousel-base.html` (já tem a estrutura 420×525 com 7 slides + progress bar + swipe arrow do prompt original).

Toda substituição é feita pelo script Python — não tente substituir placeholders via `sed`, `awk` ou heredocs do shell. O shell interpreta `$`, crases e dígitos dentro do HTML como variáveis e corrompe o conteúdo silenciosamente (problema conhecido do projeto-base). O `render_slides.py` faz tudo em Python:

```bash
python3 scripts/render_slides.py \
  --template templates/carousel-base.html \
  --brand brand/brand-kit.json \
  --copy /tmp/carrossel-{ts}.json \
  --images /tmp/carrossel-{ts}-images.json \
  --output-dir output/carrossel-{ts}/ \
  --zip
```

O script:
1. Lê brand-kit + copy + mapa de imagens
2. Embute imagens em base64 no HTML (evita problemas de path no headless browser)
3. Substitui todos placeholders
4. Lança Playwright com `viewport=420×525`, `device_scale_factor=2.5714`
5. Espera `document.fonts.ready` + 3s de buffer
6. Para cada slide, move o track CSS (`transform: translateX(-i*420)`) e screenshota com `clip` exato
7. Salva PNGs 1080×1350 em `output/carrossel-{ts}/slide-1.png` ... `slide-N.png`
8. Empacota em `output/carrossel-{ts}.zip` com README dentro

### Passo 6 — Mostra o resultado e aceita ajustes

Tenta abrir a pasta de output:

```bash
# Mac
open output/carrossel-{ts}/
# Windows
explorer output\carrossel-{ts}\
# Linux
xdg-open output/carrossel-{ts}/
```

Pergunta:

> "Pronto! Salvei o carrossel em `output/carrossel-2026-04-24-2300/` com 7 PNGs em 1080×1350 e um ZIP empacotado. Tá bom assim?
>
> Posso ajustar:
> - **Texto de algum slide específico** (ex: 'refaz a headline do slide 1')
> - **Imagem de algum slide** (regerar com outro prompt ou trocar por upload)
> - **Reordenar slides** (ex: 'troca o slide 3 com o 4')
> - **Variantes da mesma estrutura** (mesma narrativa, copy diferente — útil pra A/B test)
> - **Trocar formato da marca** (ex: 'usa o gradient como fundo do hero')
> - **Adicionar pills riscadas no slide de problema** (ex: 'mostra Photoshop, Canva, Figma riscados pra reforçar que substituímos esses')
>
> Também dá pra exportar a caption gerada pra colocar na descrição do post: vou colar aqui se quiser."

## Componentes opcionais

### Pills riscadas (`legacy_items` no slide de problema)
Quando o briefing fala de **substituir uma ferramenta/método** ou **comparar com concorrente nomeado**, vale gerar `legacy_items` no slide de problema. São 2-5 pills curtas tachadas no fundo escuro, criando o efeito visual "esquece X, Y, Z". O Gemini decide quando usar via system prompt — você não precisa pedir explicitamente, mas pode sugerir se notar oportunidade no briefing (ex: aluno disse "quero mostrar que substituo Canva e Figma" → garante que entra).

### Watermark de marca (logo de fundo)
Aparece automaticamente nos slides hero, CTA e solution **se o aluno tiver `logo_path` no brand-kit**. Sem logo, sem watermark. Aceita SVG (escala melhor), PNG, JPG. Se o aluno não gostar, dá pra remover via flag (futuro: passar `--no-watermark` no `render_slides.py`).

## Princípios de copy (lembre ao gerar)

Esses princípios estão no `docs/prompts-gemini.md` mais detalhados, mas sempre considere:

1. **O hook tem 1 segundo** — slide 1 precisa parar o scroll. Promete benefício forte, desafia uma crença, ou faz pergunta provocativa. Não descreve o produto.

2. **Mostra dor concreta, não features genéricas** — "Pare de perder leads" funciona muito melhor que "CRM com 200 funcionalidades".

3. **CTA específico** — "Quero meu diagnóstico grátis" > "Saiba mais". CTA genérico mata conversão.

4. **Prova social vale ouro quando real** — número de clientes, depoimento curto, resultado mensurável. Não invente.

5. **Last slide ≠ outros slides** — sem swipe arrow (sinaliza que acabou), progress bar 100%, CTA clarinho, espaço respirando.

6. **Carrossel tem arco** — não é lista solta de slides. Cada slide deve abrir gancho pro próximo.

## Estrutura padrão de pastas após gerar

```
output/
└── carrossel-2026-04-24-2300/
    ├── slide-1.png        # 1080×1350
    ├── slide-2.png
    ├── ...
    ├── slide-7.png
    └── README.txt         # caption + metadata pra ajudar a publicar

output/carrossel-2026-04-24-2300.zip   # ZIP com tudo dentro
```

## Erros comuns

| Sintoma | Causa | Como resolver |
|---|---|---|
| Gemini retorna JSON com slide faltando campo (`headline` vazio, etc) | Modelo às vezes ignora campo opcional do schema | Roda `gemini_text.py` com `--retry 1`. Persistindo, edita o JSON manualmente e segue. |
| Gemini bloqueia geração de imagem com `400 INVALID_ARGUMENT` | Prompt acionou safety filter (pessoas, contexto sensível) | Reescreve o prompt mais neutro: tira nomes próprios, descreve gestos em vez de emoções intensas. Documentado em `docs/prompts-gemini.md`. |
| Playwright timeout no 4º slide | Imagem pesada (>2MB base64) atrasou render | Reduz qualidade da imagem antes (Pillow `image.resize(...)` no script) ou aumenta `--wait 8000`. |
| Fonte renderiza errada (Times New Roman em vez da Plus Jakarta) | Google Fonts não terminou de baixar antes do screenshot | Aumenta `--wait-fonts 5000` no `render_slides.py`. |
| Texto estoura o card no slide de features | Aluno deu features muito longas | Avisa o aluno e oferece duas saídas: cortar texto ou ativar autofit (reduz fontSize iterativamente — script já tem flag). |
| Cores erradas em alguns slides | brand-kit.json com hex inválido (ex: `#ZZZ`) | Roda `python3 scripts/derive_palette.py --validate brand/brand-kit.json` que checa formato. |

## Quando NÃO invocar

- Aluno quer 1 imagem só → `criar-estatico`
- Setup ainda não validado → `verificar-setup` primeiro
- Brand kit não existe → `configurar-marca` primeiro
- Aluno quer apenas a copy (sem renderizar) → use `gemini_text.py` direto e devolve o JSON
