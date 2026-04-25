# Design System

Documento de referência interno usado pelo agente quando precisar tomar decisões de visual sem perguntar ao aluno (ou pra justificar uma sugestão de cor/fonte).

---

## 1. Tokens de cor

A partir de **uma cor primária** (escolhida pelo aluno ou inferida das referências), o `derive_palette.py` gera 6 tokens consistentes:

| Token | Como é derivado | Uso |
|---|---|---|
| `BRAND_PRIMARY` | Cor escolhida pelo aluno | Acento principal — botão CTA, ícones, progress bar, tags em fundos claros |
| `BRAND_LIGHT` | Primary com `lightness +0.20` (HSL) | Acento secundário — tags em fundos escuros, texto destacado |
| `BRAND_DARK` | Primary com `lightness -0.30` | Texto do CTA, âncora do gradient |
| `LIGHT_BG` | Off-white tintado conforme temperatura | Fundo claro de slides — nunca `#fff` puro |
| `LIGHT_BORDER` | LIGHT_BG com `lightness -0.05` | Divisores em slides claros |
| `DARK_BG` | Near-black tintado conforme temperatura | Fundo escuro de slides — nunca `#000` puro |

### Detecção de temperatura

- **Warm** (red, orange, yellow, magenta — hue 0°–60° ou 300°–360°): LIGHT_BG = `#FAF9F7` (cream), DARK_BG = `#1A1918`
- **Cool** (green, cyan, blue, purple — hue 60°–300°): LIGHT_BG = `#F8F9FB` (cool white), DARK_BG = `#0F172A`

Esta regra existe pra evitar dissonância (cor warm com fundo cool gera estranhamento subliminar).

### Gradient

```
BRAND_GRADIENT = linear-gradient(165deg, BRAND_DARK 0%, BRAND_PRIMARY 50%, BRAND_LIGHT 100%)
```

Usado em slides de hero, CTA e solution. O ângulo 165° foi escolhido pra dar um diagonal sutil — nem horizontal (estático) nem vertical (datado).

### Quando usar cada fundo

- **Light slides** (LIGHT_BG): hero, features, how-to — slides que ensinam ou listam, precisam de respiro
- **Dark slides** (DARK_BG): problem, details — slides que confrontam, criam tensão
- **Gradient slides**: solution, cta — slides que inspiram ação

A alternância light → dark → gradient cria ritmo visual no carrossel. Não tem regra rígida — é ferramenta de pacing.

---

## 2. Tipografia

### Pareamentos pré-definidos

| ID | Heading | Body | Quando usar |
|---|---|---|---|
| `editorial_premium` | Playfair Display | DM Sans | Marcas premium, lifestyle, bem-estar, design |
| `modern_clean` | Plus Jakarta Sans (700) | Plus Jakarta Sans (400) | SaaS, tech, produtividade, B2B moderno |
| `warm_approachable` | Lora | Nunito Sans | Coaching, terapia, alimentação saudável, parentalidade |
| `technical_sharp` | Space Grotesk | Space Grotesk | Crypto, dev tools, fintech, segurança |
| `bold_expressive` | Fraunces | Outfit | Moda, agências criativas, lançamentos disruptivos |
| `classic_trust` | Libre Baskerville | Work Sans | Direito, contabilidade, finanças tradicionais, educação |
| `rounded_friendly` | Bricolage Grotesque | Bricolage Grotesque | DTC casual, pets, infantil, food brands |

### Escala de tamanhos (fixa)

Pensada para legibilidade no layout 420px (que escala pra 1080px no export final):

- **Headline**: 28-38px, weight 600-700, letter-spacing -0.4 a -0.5px, line-height 1.05-1.15
- **Subheadline**: 14-16px, weight 400-500, line-height 1.45-1.5
- **Body**: 13-14px, weight 400, line-height 1.5-1.55
- **Tag/label**: 10-11px, weight 600, letter-spacing 2px, uppercase
- **Step number**: heading font, 24-26px, weight 300
- **Small/handle**: 11-12px, opacity 0.6-0.7

### Princípio: heading curto, body resumido

Anúncio não é texto longo de blog. Quando o texto da copy passar dos limites:
1. Pede pra encurtar antes de usar autofit
2. Se for inevitável (depoimento longo, lista de items), o autofit reduz fontSize iterativamente até caber (mínimo 11px no body, 22px no heading)

---

## 3. Layout — slide 420×525px (carrossel)

A escolha de 420px de largura no design (e não 1080px direto) é deliberada:
- O Playwright renderiza no viewport 420×525 e usa `device_scale_factor=2.5714` pra escalar pra 1080×1350
- Layout permanece nativo em 420px — fonts e espaçamentos não se distorcem
- Mais leve no headless browser (menos pixels pra processar)

### Padding padrão
- Conteúdo: `36px` lateral
- Bottom (com progress bar): `52px` pra não sobrepor a barra
- Hero/CTA slides: `justify-content: center` (texto vertical-centrado)
- Slides com features/lista: `justify-content: flex-end` (lista no fundo, ar em cima)

### Elementos sempre presentes (carrossel)

1. **Progress bar** (bottom: 16px 28px 20px) — track 3px, fill na cor da marca, counter "1/7"
2. **Swipe arrow** (right: 40px wide) — chevron sutil em todos os slides exceto o último
3. **Logo lockup** — apenas no hero (slide 1) e CTA (último slide)

### Por que swipe arrow some no último slide?
Sinaliza fim. Sem o arrow, o cérebro do usuário entende que não tem mais nada — reforçado por progress bar 100%. Detalhe pequeno, impacto grande na UX.

---

## 4. Layouts dos estáticos

### 1:1 (1080×1080)
- Quadrado clássico de feed
- Layout: imagem à esquerda 50%, texto 50% (se tiver imagem); ou texto centrado em fundo gradient (sem imagem)
- Uso: feed Instagram/Facebook

### 4:5 (1080×1350) — recomendado
- Vertical mobile-first
- Layout: imagem topo (260px), texto no fundo escuro com gradient blend; ou só texto centrado
- Uso: feed Instagram/Facebook (formato que ocupa mais tela no mobile, melhor CTR)

### 9:16 (1080×1920)
- Vertical full-screen
- Layout: imagem fullbleed com overlay gradient escuro; texto distribuído verticalmente (top/middle/bottom)
- Uso: Stories, Reels, status WhatsApp

---

## 5. Componentes reutilizáveis

### Tag pill
Pequeno selo uppercase acima da headline. 10-11px, weight 600, letter-spacing 2px.
- Light slides: cor = BRAND_PRIMARY
- Dark slides: cor = BRAND_LIGHT
- Gradient slides: cor = `rgba(255,255,255,0.7)`

### CTA button
- Padding: 12-14px vertical, 24-28px horizontal
- Background: LIGHT_BG (mesmo em fundo escuro/gradient — gera contraste alto)
- Text color: BRAND_DARK
- Border-radius: 28-32px (pill)
- Font: 13.5-14.5px, weight 600

### Logo lockup
- Círculo 36px em BRAND_PRIMARY com inicial branca em heading font
- Nome da marca ao lado, body font, 13px weight 600

### Quote box
Para depoimentos curtos:
- Background: `rgba(0,0,0,0.18)`
- Border: 1px `rgba(255,255,255,0.1)`
- Border-radius: 10px
- Texto em itálico, heading font, 14px

### Feature row
Ícone + label + desc:
- Ícone: char unicode (▶ ✦ ◆ ★ etc) em BRAND_PRIMARY/LIGHT, 16px
- Label: body font, 13.5px, weight 600
- Desc: body font, 12px, opacity 0.65
- Separador: 1px solid LIGHT_BORDER

### Step row (numbered)
Para how-to:
- Número: heading font, 24-26px, weight 300, em BRAND_PRIMARY (formato "01", "02")
- Title + desc seguindo padrão de feature row

### Strikethrough pills (legacy_items)
Pills ovaladas com texto cortado, usadas no slide de **problema** quando a narrativa é "deixe X, Y, Z pra trás — agora é assim". Útil pra anúncios de pivot ("esquece o Photoshop") ou comparativos com concorrentes.

- Container: flex wrap, gap 8px
- Pill: 6px 14px padding, border-radius 24px, fonte body 11.5px weight 500
- Borda em `rgba(255,255,255,0.16)` (dark) ou `light-border` (light)
- Background super sutil (`rgba(255,255,255,0.04)` / `rgba(0,0,0,0.02)`)
- `text-decoration: line-through`, espessura 1.5px
- Limite recomendado: **2 a 5 termos**, **1-3 palavras cada**. Mais que isso fica ruidoso.

Exemplos de uso:
- "Photoshop", "Canva", "Figma" → produto que substitui ferramentas de design
- "Planilha manual", "Email solto", "Reuniões longas" → SaaS de produtividade
- "Apps de tradução", "Filmes legendados", "Cursos genéricos" → curso especializado

### Watermark (logo de fundo)
Logo da marca em opacidade baixa (0.05–0.10) no canto inferior direito dos slides de alta atenção (**hero**, **cta**, **solution**). Tamanho ~220px. Adiciona refinamento visual sem competir com o conteúdo.

Regras:
- Só renderiza se `brand-kit.json` tem `logo_path` apontando pra arquivo existente. Se aluno só tem inicial, não tem watermark (inicial em watermark fica estranho).
- Aceita SVG, PNG, JPG, WebP. SVG escala melhor.
- Light slide: opacity 0.05 (quase imperceptível, refinado)
- Dark slide: opacity 0.06
- Gradient slide: opacity 0.10 (gradient já tem ruído visual, watermark precisa de mais peso pra aparecer)
- Posição padrão: bottom-right (-30px, -30px) — sai parcialmente do viewport pra parecer "estampado"

---

## 6. Anti-padrões (não fazer)

| Não fazer | Motivo |
|---|---|
| Usar `#FFFFFF` puro como fundo | Marca pulada/genérica. Sempre LIGHT_BG (off-white tintado) |
| Usar `#000000` puro como fundo | Mesmo motivo. Sempre DARK_BG (near-black com tint) |
| Headline com mais de 12 palavras | Anúncio. Não é blog. Encurta. |
| Mais de 3 fontes | Ruído visual. Usa heading font + body font, máximo |
| CTA "Saiba mais", "Clique aqui" | CTA fraco mata conversão. Usa específico: "Quero meu diagnóstico", "Pegar minha vaga" |
| Imagem genérica de banco com 5 mil pessoas igual | Anúncio parece spam. Use foto real do produto/aluno ou IA com prompt específico |
| 8+ features no slide de features | Ninguém lê. 3-4 max, com label curto |
| Cor saturada como fundo (ex: `#FF0000` puro) | Cansa o olho em 1s. Use BRAND_GRADIENT que já tem profundidade |
| Texto em cima de imagem sem overlay | Legibilidade quebra dependendo da foto. Sempre overlay gradient nos estáticos com imagem fullbleed |

---

## 7. Acessibilidade básica

Mesmo sendo anúncio (e não conteúdo nativo), vale:
- Contraste mínimo 4.5:1 entre texto e fundo (calc com BRAND_DARK no botão sobre LIGHT_BG geralmente passa)
- Tamanho mínimo de texto: 11px no layout 420px (que vira 28px em 1080px — ok)
- Não usar cor sozinha pra transmitir info (ex: vermelho = ruim, verde = bom — adicionar ícone ou label)

---

## 8. Resumo prático

Quando o agente for sugerir algo de visual, lembrar:

1. **Cor primária define tudo.** Os outros 5 tokens vêm dela.
2. **Light/dark/gradient** alternam pra criar ritmo.
3. **Layout 420×525** com `device_scale_factor=2.5714` pra exportar 1080×1350.
4. **2 fontes max** — heading e body. Não improvisar.
5. **Headlines curtas, CTAs específicos.** Anúncio.
6. **Imagem real > IA** sempre que possível.
7. **Último slide do carrossel é diferente** — sem arrow, progress 100%, CTA pop.
