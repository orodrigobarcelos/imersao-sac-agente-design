# 🎨 Agente Criativo de Design — Imersão SAC

Crie criativos de anúncio profissionais (estáticos ou carrossel) **conversando com o Claude**, dentro do Claude Code Desktop. A IA escreve a copy, monta o visual e exporta os arquivos prontos pra subir no Meta Ads.

> **É feito pra você não precisar abrir Photoshop, Canva ou nenhum editor.** Só conversar.

---

## 🚀 Primeira vez aqui? **[Lê o COMECE-AQUI.md →](COMECE-AQUI.md)**

3 passos simples, sem terminal, sem código. O Claude conduz o resto.

---

## 🎯 O que dá pra fazer

- **Criativo único (estático)** — 1 imagem nos formatos 1:1, 4:5 ou 9:16
- **Carrossel de anúncio** — 5 a 10 slides com arco persuasivo (gancho, problema, solução, CTA)
- IA gera **copy** (texto), **imagens ilustrativas** (opcional) e o **layout final**
- Você pode **enviar suas próprias fotos** (do produto, suas) ou deixar a IA gerar
- **Não tem identidade visual definida?** Manda imagens de design que você gosta — a IA analisa e sugere uma paleta pra você

---

## ⚙️ O que você precisa instalar (uma vez só)

Antes de começar, instale:

### 1. Claude Code Desktop
Se você já tá lendo isso aqui dentro do Claude, ✅ já tem.

Se não: baixe em https://claude.com/download

### 2. Python 3.10 ou superior

**Mac:**
```bash
# Verifica se já tem
python3 --version

# Se der erro ou versão for menor que 3.10, instala via Homebrew:
brew install python@3.12
```

**Windows:**
1. Baixe em https://www.python.org/downloads/
2. **MARQUE a opção "Add Python to PATH"** durante a instalação
3. Abra o PowerShell e teste: `python --version`

### 3. Chave Gemini (grátis até 1500 usos por dia)

1. Acesse https://aistudio.google.com/app/apikey
2. Faça login com conta Google
3. Clique em **"Create API key"**
4. Copie a chave (começa com `AIza...`)
5. **Não compartilhe essa chave com ninguém**

### 4. As bibliotecas Python e o navegador headless

Não se preocupe — **o Claude vai instalar isso pra você** na primeira vez que você abrir o projeto. Mas se quiser fazer manualmente:

```bash
cd <pasta-do-projeto>
pip install -r scripts/requirements.txt
playwright install chromium
```

---

## 🚀 Como começar

### Passo 1 — Configure sua chave Gemini

1. Abra o arquivo `.env.example` (na raiz do projeto)
2. Salve uma cópia com o nome `.env` (sem o `.example`)
3. Abra `.env` e cole sua chave depois do `=`:

```
GEMINI_API_KEY=AIzaSy...sua-chave-aqui
```

> ⚠️ Nunca compartilhe ou faça commit desse arquivo. O `.gitignore` já protege ele.

### Passo 2 — Abra o projeto no Claude Code

1. Abra o **Claude Code Desktop**
2. **File → Open Folder** (ou arrasta a pasta pra janela)
3. Selecione a pasta `imersao-sac-agente-design`

### Passo 3 — Mande sua primeira mensagem

Na caixa de chat, digite algo simples tipo:

```
oi, vamos criar um anúncio
```

ou

```
quero criar um carrossel pra divulgar meu curso de inglês
```

O Claude vai:
1. Verificar se tudo tá instalado
2. Te perguntar sobre sua marca (cor, fonte, logo) — se ainda não configurou
3. Te perguntar sobre o anúncio (público, oferta, formato)
4. Gerar a copy com IA
5. Perguntar se quer usar foto sua ou imagem gerada
6. Montar o criativo
7. Salvar em `output/` e abrir pra você ver

---

## 💡 Dicas pra usar bem

### Tem uma identidade visual? Diga logo de cara
Se você já tem cor da marca, fonte, logo — manda tudo de uma vez:

> "Minha marca é Acme Co, cor #6366f1, fonte Plus Jakarta Sans, handle @acme. Quero criar um carrossel sobre meu curso de copywriting."

### Não tem identidade? Manda referências
Arrasta 2-5 imagens de anúncios/posts/sites que você gosta direto na conversa. O Claude analisa e sugere uma paleta.

### Quer usar uma foto sua?
Coloca a foto na pasta `assets/` e fala onde tá:

> "Usa a foto que tá em assets/minha-foto.jpg como imagem do hero"

### Não gostou de algo? Fala
> "Refaz a headline mais ousada"
> "Troca a cor de fundo desse slide pra mais escura"
> "A imagem do slide 3 não combina, gera outra"

### Precisa de variantes pra A/B test?
> "Me dá 3 versões diferentes desse mesmo carrossel"

---

## 📂 Onde fica o quê

| Pasta | O que tem |
|---|---|
| `brand/` | Sua identidade visual (gerada na primeira conversa) |
| `assets/` | Suas fotos / imagens que você quer usar |
| `output/` | **Os criativos prontos vão pra cá** |
| `templates/`, `scripts/`, `docs/` | Tripas do projeto — você não precisa mexer |

---

## ❓ Problemas comuns

### "ModuleNotFoundError: google.genai"
As bibliotecas Python não foram instaladas. Manda no chat:
> "instala as dependências"

### "GEMINI_API_KEY not set"
Você esqueceu de criar o `.env`. Volta no **Passo 1** acima.

### "RESOURCE_EXHAUSTED" / "429"
Você usou as 1500 chamadas grátis do dia. Espera 24h ou aumenta o limite no AI Studio.

### Playwright travou no install
A primeira instalação do Chromium baixa ~200MB. Aguarda. Se travar mais de 5 min, manda no chat:
> "tenta de novo o setup"

### Outra coisa
Manda no chat o erro que apareceu. O Claude tá treinado pra resolver.

---

## 🤓 Pra quem quer entender o que tá rolando

- `CLAUDE.md` — instruções que o Claude segue (você pode ler e até editar pra customizar o comportamento)
- `PLANO.md` — plano técnico completo do projeto
- `.claude/skills/` — fluxos detalhados que o Claude carrega quando precisa
- `docs/` — documentação interna (design system, prompts de IA)

---

## 📝 Licença

Template educacional da Imersão SAC. Use livremente nos seus projetos pessoais e profissionais.
