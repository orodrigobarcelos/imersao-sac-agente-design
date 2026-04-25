# Prompts Gemini — Copywriting + Geração de Imagem

Documento de referência interno usado pelo agente quando precisar refinar prompts pro Gemini ou justificar decisões de copy.

---

## 1. Princípios de copywriting de anúncio

Anúncio não é conteúdo orgânico. As regras são diferentes:

| Conteúdo orgânico | Anúncio (foco aqui) |
|---|---|
| Educa, entretém, constrói relação | Converte. Tem um objetivo único. |
| Pode ser longo, narrativa | Curto. Cada palavra paga aluguel. |
| Tom natural da marca | Tom da marca + gancho de venda |
| CTA opcional | CTA obrigatório, específico |
| Headline pode ser sutil | Headline para o scroll em 1s |

### As 6 leis de uma headline de anúncio

1. **Promete benefício, não feature.**
   - Ruim: "CRM com 200 funcionalidades"
   - Bom: "Pare de perder leads enquanto você dorme"

2. **Especifica resultado, não descreve produto.**
   - Ruim: "Curso completo de inglês com 60 horas de aula"
   - Bom: "Falando inglês fluente em 60 dias — sem morar fora"

3. **Combate uma crença errada do público.**
   - "Você não precisa de 5 anos pra mudar de carreira"
   - "Não é falta de disciplina — é falta de método"

4. **Usa pergunta provocativa quando faz sentido.**
   - "Por que seus anúncios não vendem mais?"
   - "Você sabia que 80% das dietas falham por isso?"

5. **Encurta até doer.** 7-9 palavras é o sweet spot.

6. **Usa números quando tem.** "+2.000 alunos", "em 30 dias", "3x mais leads" — números pegam atenção.

### Anti-headlines (não fazer)

- "Conheça a melhor solução do mercado" → vazio, todo mundo fala isso
- "Promoção imperdível!" → spam
- "Compre agora!" → não deu nem motivo
- "Você sabia que..." → curiosity gap fraco

---

## 2. Variantes obrigatórias (estático)

Pra cada criativo estático, o Gemini retorna **3 variantes** prontas pra A/B test:

### Agressiva
- Provoca, desafia, usa negação
- Hooks: "Pare de...", "Você sabia que...", "Chega de..."
- Tom: direto, quase confrontador
- Quando funciona: produtos de transformação (cursos, coaching, fitness, finanças)

### Racional
- Foca em prova e dado concreto
- Hooks: "X clientes...", "Em Y dias...", "Reduza Z%..."
- Tom: confiante, objetivo
- Quando funciona: B2B, SaaS, serviços profissionais

### Emocional
- Apela a aspiração, identidade, desejo profundo
- Hooks: "Você merece...", "Imagina ser...", "A vida que você quer..."
- Tom: caloroso, aspiracional
- Quando funciona: lifestyle, beleza, bem-estar, viagem

**Por que não 1 variante perfeita?**
Anúncio se valida no teste. Você não sabe qual mensagem ressoa mais com o público antes de rodar. As 3 variantes permitem subir 3 ad sets paralelos e deixar o algoritmo do Meta decidir o vencedor com R$ 50-100 de teste.

---

## 3. Arco do carrossel (7 slides)

A estrutura padrão segue jornada psicológica clássica de vendas:

```
1. HOOK  →  2. DOR  →  3. SOLUÇÃO  →  4. FEATURES  →  5. DETALHES  →  6. PASSO-A-PASSO  →  7. CTA
```

### Slide 1 — Hero (gancho)
Função: parar o scroll.
- Headline impactante (ver leis acima)
- Subheadline curta de reforço
- Logo lockup
- Imagem opcional (não é obrigatória — texto pode ocupar tudo)

### Slide 2 — Problema
Função: o usuário se ver na situação descrita.
- Headline que nomeia a dor com palavras dele
- Lista de 3-4 sintomas/situações concretas (ele lê e pensa "sou eu")
- **Opcional: pills riscadas** (`legacy_items`) — quando a narrativa é "deixe X, Y, Z pra trás". Use APENAS se o briefing menciona algum tipo de pivot ou substituição (ex: "antes era Photoshop, agora é Canva", "pare de usar planilha"). Não force quando não cabe.
- Imagem que reforça (frustração, cansaço, etc) — opcional

**Quando usar `legacy_items`** (regra prática pro Gemini):

| Briefing menciona... | Usar pills? |
|---|---|
| Substituir uma ferramenta/método específico | ✅ sim |
| Comparativo com concorrentes nomeados | ✅ sim |
| "Cansou de X?", "Esquece Y" | ✅ sim |
| Dor genérica sem pivot ("não consigo emagrecer") | ❌ não — só items |
| Apresentação de produto novo | ❌ não — só items |

Quando usar, escolha 2-5 pills, 1-3 palavras cada. Mais que isso polui visualmente.

### Slide 3 — Solução
Função: aliviar tensão. Mostrar saída.
- Headline da promessa
- Body explicando o método (1-2 frases)
- Quote/depoimento curto opcional pra prova social
- Fundo gradient pra mudar a energia visualmente

### Slide 4 — Features (o que tem)
Função: justificar valor.
- 3-4 features no formato `ícone + label + desc curta`
- Não confunde com benefício — features apoiam a promessa, não a substituem
- Ícones: chars unicode simples (▶ ✦ ◆ ★ ●)

### Slide 5 — Detalhes (diferencial)
Função: aprofundar 1-2 diferenciais.
- Pode ser texto corrido (body) ou lista
- Foco em o que outros NÃO oferecem
- Imagem opcional pra ilustrar o diferencial

### Slide 6 — How-to (passo-a-passo)
Função: simplificar a ação.
- 3 passos numerados (01, 02, 03) com title + desc
- Mostra que é simples — derrubando objeção "vai ser complicado pra mim"

### Slide 7 — CTA
Função: ação.
- Headline que reforça a promessa final
- Subheadline com remoção de risco ("Sem cartão", "Sem compromisso", "Garantia 30 dias")
- CTA pill bem visível
- Logo lockup
- **Sem swipe arrow** (último slide)

### Variações da estrutura

A estrutura clássica funciona pra 90% dos casos. Mas:

- **Lançamento de produto novo**: Hero → Antes/Depois → Features → CTA (5 slides)
- **Captura de lead pra evento**: Hero → Pra quem é → O que vai aprender → Quem é o expert → CTA com data (5 slides)
- **Promoção de desconto**: Hero (oferta no rosto) → Por tempo limitado → O que tá incluso → CTA com urgência (4 slides — limite mínimo)

O agente pode adaptar o arco com o aluno. Não é regra de pedra.

---

## 4. Prompts de imagem (Gemini Image)

### Estrutura de um bom prompt

```
[descrição central da cena] + [estilo] + [iluminação] + [composição] + [aspect ratio hint] + [no text, no watermark]
```

Exemplo:
```
professional in modern office, confident posture, looking forward.
Editorial photography style. Soft natural light from side window.
Centered composition, depth of field background.
Vertical 4:5 aspect ratio.
High quality, no text, no watermark, no logo.
```

### Estilos que funcionam bem

- `editorial photography` — fotografia premium estilo revista (default seguro)
- `flat illustration, geometric shapes, vibrant` — ilustração moderna pra tech/SaaS
- `minimalist 3D render, soft shadows, pastel palette` — 3D limpo pra produtos digitais
- `documentary photography, candid` — autenticidade, lifestyle
- `studio product photography, clean white background` — produto físico

### Iluminação que funciona

- `soft natural light from side window` — clássico flattering
- `warm golden hour light` — emocional, lifestyle
- `studio softbox lighting` — produto, neutro
- `dramatic chiaroscuro` — alto contraste, premium

### O que SEMPRE incluir no prompt

- `no text, no watermark, no logo` — Gemini às vezes inventa texto rabiscado
- aspect ratio explícito ("vertical 4:5", "horizontal 16:9", "square 1:1")
- "high quality" ou "professional photography"

### O que NUNCA incluir

- Nomes próprios de pessoas (acionará safety filter)
- Marcas registradas ("foto estilo Nike")
- Conteúdo violento, sexual, médico (filtros)
- Referências a IPs (Disney, Mickey, etc)

### Quando o prompt for rejeitado (400 INVALID_ARGUMENT)

Reescreve com:
1. Tira nomes próprios
2. Substitui emoções intensas por descrições neutras (ex: "frustrated" → "pensive")
3. Remove menções a corpo/saúde se for o caso
4. Generaliza ("a person" em vez de "young woman", se gênero não for crucial)

### Quando preferir upload em vez de IA

Use upload do aluno quando:
- Produto físico (a IA inventa detalhes errados)
- Pessoa real do anúncio (depoimento, fundador, expert)
- Resultado real (antes/depois de transformação)
- Print de tela do app/dashboard

Use IA quando:
- Ilustração conceitual (sem produto real)
- Fundo abstrato pra texto
- Hero genérico de "pessoa profissional"
- Refazer mood board

---

## 5. Caption (legenda do post)

A caption é gerada junto com a copy. Princípios:

- **Primeira linha = repete o gancho do hero** (Instagram corta após ~125 chars no feed)
- **Quebra em parágrafos curtos** (1-2 linhas cada)
- **Termina com CTA + 3-5 hashtags relevantes**
- **Não exagera no emoji** (1-2 estratégicos > 10 espalhados)

Tamanho ideal: 150-300 caracteres. Mais que isso, ninguém lê.

---

## 6. Tom de voz

O `brand-kit.json` salva o tom. Aplicação:

| Tom | Headline | Body | CTA |
|---|---|---|---|
| Profissional e direto | "Reduza CAC em 40% no próximo trimestre" | "Método validado por 50+ empresas SaaS." | "Agendar diagnóstico" |
| Casual e amigável | "Cansou de pagar caro pra atrair cliente?" | "A gente entende — passou por isso. Por isso fizemos diferente." | "Quero saber mais" |
| Provocativo e ousado | "Seu funil tá vazando dinheiro" | "E você nem percebeu. 3 vazamentos comuns que destroem ROI." | "Tampar os buracos" |
| Educativo e didático | "Como reduzir CAC em 3 passos" | "Sem terceirizar tráfego. Sem aumentar budget. Só processo." | "Aprender o método" |

---

## 7. Cuidados éticos / compliance

O agente NÃO gera copy que:
- Promete resultado garantido sem evidência ("ganhe 10k em 7 dias")
- Usa termos médicos (cura, trata, previne) sem certificação
- Usa antes/depois em saúde/estética sem disclaimer
- Plagia copy de concorrente conhecido
- Apela a medo de doença / morte

Se o aluno pedir, alerta sobre risco de bloqueio do Meta Ads (que tem políticas próprias) e oferece reescrever de forma compatível.

---

## 8. Resumo prático

Quando o agente for gerar copy:
1. **Headline curta** (7-9 palavras, sem clichê)
2. **3 variantes** (agressiva, racional, emocional) pra estático
3. **Arco completo** (7 slides) pra carrossel — adaptável conforme briefing
4. **CTA específico** (nunca "saiba mais")
5. **Caption** com primeira linha = gancho
6. **Tom da marca** (lê do brand-kit.json)
7. **Sem promessas mirabolantes** (compliance)
