---
name: configurar-marca
description: Conduz briefing de identidade visual da marca (cor primária, tipografia, logo, tom de voz, handle) e salva tudo em brand/brand-kit.json para ser usado pelos criativos. Lida com dois cenários - aluno que já tem identidade definida (coleta direta) e aluno que não tem nada definido ou só tem referências (analisa imagens visuais que o aluno arrasta no chat e sugere uma direção). Invoque sempre que brand/brand-kit.json não existir e o aluno quiser criar um criativo, ou quando ele disser frases tipo "configurar marca", "mudar a marca", "outra empresa", "trocar cor da marca", "vou usar pra outro projeto", "ainda não tenho identidade", "me ajuda a definir o estilo", "tenho referências mas não defini nada". Também invoque se o aluno mencionar que vai criar conteúdo pra uma marca diferente da que está salva.
---

# Skill: configurar-marca

Cria ou atualiza `brand/brand-kit.json` — fonte de verdade visual usada por todos os criativos. Suporta dois caminhos: aluno com identidade pronta ou aluno que precisa de ajuda pra construir uma.

## Quando invocar

- `brand/brand-kit.json` não existe e o aluno quer criar um criativo
- Aluno disse: "quero mudar a marca", "vou trocar a cor", "configurar a marca", "outra empresa"
- Aluno disse que tem identidade nova / outro projeto

## Pergunta inicial (sempre)

> "Vamos configurar a identidade visual. Você já tem uma marca com cor, fonte e logo definidos, ou ainda tá descobrindo o estilo?
>
> 1. **Tenho tudo definido** — me passa cor, fonte e logo
> 2. **Mais ou menos** — tenho algumas referências mas não definiu
> 3. **Não tenho nada** — me ajuda a descobrir"

Se aluno escolher **1**: vai pro [Caminho A](#caminho-a--aluno-tem-identidade-definida).
Se escolher **2** ou **3**: vai pro [Caminho B](#caminho-b--aluno-precisa-de-ajuda-com-referências).

---

## Caminho A — Aluno tem identidade definida

### A.1 — Coletar info, uma pergunta por vez

Em ordem (NUNCA pergunte tudo junto):

1. **Nome da marca**
   > "Qual o nome da marca / empresa / projeto?"

2. **Handle (opcional)**
   > "Tem um @ no Instagram pra mostrar? (Pode pular se não tiver)"

3. **Cor primária**
   > "Qual a cor principal da marca? Pode ser:
   > - Código hex (ex: `#6366f1`)
   > - Nome (ex: 'azul cobalto', 'vermelho coral')
   > - Foto/print da marca/site"

   Se aluno der nome ou foto, **escolha um hex razoável** e mostre antes de salvar:
   > "Beleza, então vou usar `#6366f1` como cor primária. Tá bom ou quer ajustar?"

4. **Fontes**
   > "Sobre tipografia, qual desses estilos combina com a marca?
   > 1. **Editorial / premium** (Playfair + DM Sans)
   > 2. **Moderno / clean** (Plus Jakarta Sans)
   > 3. **Caloroso / acessível** (Lora + Nunito Sans)
   > 4. **Técnico / sharp** (Space Grotesk)
   > 5. **Bold / expressivo** (Fraunces + Outfit)
   > 6. **Clássico / confiável** (Libre Baskerville + Work Sans)
   > 7. **Arredondado / amigável** (Bricolage Grotesque)
   > 8. Tenho fontes específicas em mente"

   Se 8: pede o nome (precisa estar no Google Fonts).

5. **Logo (opcional)**
   > "Tem logo? Posso usar de duas formas:
   > - Você arrasta o arquivo aqui na conversa, eu salvo em `brand/logo.png`
   > - Pula logo e uso só a inicial do nome em círculo da cor primária"

6. **Tom de voz**
   > "Como a marca fala com o público?
   > 1. Profissional e direto
   > 2. Casual e amigável
   > 3. Provocativo e ousado
   > 4. Educativo e didático
   > 5. Outro (descreva)"

### A.2 — Gerar paleta derivada

Roda o script:

```bash
python3 scripts/derive_palette.py --primary "#6366f1" --output brand/brand-kit.json --append
```

O script gera os 6 tokens (BRAND_PRIMARY, LIGHT, DARK, LIGHT_BG, LIGHT_BORDER, DARK_BG) e mescla com o resto do brand kit já coletado.

### A.3 — Mostra o resultado

Mostra um resumo:

> ✅ Marca configurada:
> - **Acme Co** (@acme)
> - Cor primária: #6366f1
> - Paleta derivada: 6 tons (clarinho, escuro, fundos)
> - Tipografia: Plus Jakarta Sans (heading + body)
> - Tom: profissional e direto
>
> Salvei em `brand/brand-kit.json`. Bora criar um anúncio?

---

## Caminho B — Aluno precisa de ajuda com referências

### B.1 — Pede referências visuais

> "Pode me mandar 2 a 5 imagens de design que você gosta? Pode ser:
> - Anúncios que te chamaram atenção
> - Posts de marcas que você admira
> - Sites/landing pages
> - Paletas que você curte
>
> Arrasta as imagens aqui na conversa que eu analiso o estilo e sugiro uma direção."

### B.2 — Analisa as imagens (multimodal)

Quando o aluno anexar as imagens:

1. **Você (Claude) analisa diretamente** — descreve o que vê: cores dominantes, mood (corporativo/playful/editorial), tipografia (serif/sans/display), uso de fotos vs ilustrações, contraste, espaço negativo

2. **Opcional — extrai paleta numérica via script:**
   Se o aluno anexou imagens e elas foram salvas em `brand/references/`, roda:
   ```bash
   python3 scripts/analyze_references.py --dir brand/references/ --output /tmp/palette.json
   ```
   O script usa Pillow pra extrair as 5 cores dominantes via k-means.

3. **Sintetiza um padrão**:
   > "Analisando suas referências, vejo que você gosta de:
   > - Paleta: tons terrosos com um acento vibrante (laranja queimado #C84B1F)
   > - Mood: editorial / premium, espaço negativo generoso
   > - Tipografia: serif para títulos, sans pra corpo
   > - Estética: minimalista, foto > ilustração
   >
   > Faz sentido com a marca que você quer construir?"

### B.3 — Itera com o aluno

Aluno pode:
- Aprovar tudo → salva e segue
- Ajustar partes → "gostei das cores mas quero fonte mais moderna" → atualiza
- Refazer → pede mais referências

### B.4 — Coleta o resto

Mesmo do Caminho A.1, mas com sugestões já preenchidas:
- Nome da marca, handle, logo
- Tom de voz

### B.5 — Gera paleta + salva

Igual A.2 e A.3.

---

## Schema do `brand/brand-kit.json`

```json
{
  "name": "Acme Co",
  "handle": "@acme",
  "tone": "profissional e direto",
  "primary_color": "#6366f1",
  "heading_font": "Plus Jakarta Sans",
  "body_font": "Plus Jakarta Sans",
  "font_pairing_id": "modern_clean",
  "logo_path": "brand/logo.png",
  "logo_initial": "A",
  "tokens": {
    "BRAND_PRIMARY": "#6366f1",
    "BRAND_LIGHT": "#a5b4fc",
    "BRAND_DARK": "#3730a3",
    "LIGHT_BG": "#faf9f7",
    "LIGHT_BORDER": "#e8e5e0",
    "DARK_BG": "#1a1918",
    "BRAND_GRADIENT": "linear-gradient(165deg, #3730a3 0%, #6366f1 50%, #a5b4fc 100%)"
  },
  "references": [
    "brand/references/ref-1.jpg",
    "brand/references/ref-2.jpg"
  ],
  "created_at": "2026-04-24T22:00:00Z"
}
```

## Boas práticas

1. **Nunca pergunte tudo de uma vez.** Uma decisão por vez.

2. **Sempre confirme cores em hex.** Se aluno disser "azul", mostra o hex que você escolheu antes de salvar.

3. **Se aluno mandar foto/print da marca**, use sua capacidade multimodal pra extrair a cor primária (com `analyze_references.py` como apoio se a foto for complexa).

4. **Logo opcional.** Se aluno não tiver, gera placeholder com inicial do nome em círculo da cor primária — código já tá nos templates.

5. **Salve sempre.** Mesmo que o aluno pare no meio, salva o que foi coletado até ali em `brand/brand-kit.json` parcial. Pode retomar depois.

6. **Imagens de referência** vão em `brand/references/`. Salva os arquivos originais que o aluno anexou.

## Quando NÃO invocar

- Quando `brand/brand-kit.json` já existe e tá completo (a menos que o aluno peça pra mudar)
- No meio de criar um criativo (espera o aluno terminar e pergunta depois)
