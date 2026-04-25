---
name: verificar-setup
description: Valida e instala dependências do projeto de criativos (Python ≥3.10, bibliotecas google-genai/playwright/dotenv/Pillow, Chromium headless, e arquivo .env com GEMINI_API_KEY). Use sempre que o aluno abrir o projeto pela primeira vez, mencionar erro tipo "ModuleNotFoundError", "Executable doesn't exist", "GEMINI_API_KEY not set", "command not found", ou disser frases como "tá dando erro", "não tô conseguindo rodar", "instala as coisas", "configura o setup". Também invoque antes de tentar qualquer skill criadora (configurar-marca, criar-estatico, criar-carrossel) se você ainda não validou o setup nesta sessão — vale mais 30s de checagem do que um erro confuso no meio do fluxo.
---

# Skill: verificar-setup

Garante que o ambiente do aluno tem tudo pra rodar os scripts. Se algo faltar, instala (com permissão) ou orienta.

## Quando invocar

- Primeira vez que o aluno abre o projeto
- Aluno mandou primeira mensagem mas você ainda não validou setup
- Algum script Python falhou com `ModuleNotFoundError`, `Executable doesn't exist`, ou `GEMINI_API_KEY not set`
- Aluno digitou algo como "instala", "setup", "tá dando erro"

## Fluxo passo-a-passo

### Passo 1 — Detecta o sistema operacional

```bash
uname -s
```

- `Darwin` → Mac
- `Linux` → Linux
- `MINGW*` ou `MSYS*` ou `CYGWIN*` → Windows (Git Bash). No Windows nativo, o Claude Code Desktop pode estar usando PowerShell.

### Passo 2 — Verifica Python ≥ 3.10

```bash
python3 --version 2>/dev/null || python --version 2>/dev/null
```

**Se não tiver Python ou versão < 3.10:**
- Mac: oriente `brew install python@3.12` (ou link pra https://www.python.org/downloads/)
- Windows: link pra https://www.python.org/downloads/ — **enfatize "Add Python to PATH"**
- Linux: `sudo apt install python3.12 python3-pip` (Debian/Ubuntu)

Não tente instalar Python automaticamente. Pede pro aluno fazer manualmente e voltar.

### Passo 3 — Verifica pip e bibliotecas Python

```bash
python3 -c "import google.genai, playwright, dotenv, PIL" 2>&1
```

Se falhar:

```bash
# Mostra ao aluno o que vai rodar:
# "Vou instalar as bibliotecas Python necessárias. Pode levar 30s."
pip install -r scripts/requirements.txt
```

Se `pip` não for encontrado:

```bash
python3 -m pip install -r scripts/requirements.txt
```

### Passo 4 — Verifica Playwright Chromium

```bash
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); b.close(); p.stop()" 2>&1
```

Se der `Executable doesn't exist`:

```bash
# Avisa o aluno: "Vou baixar o Chromium headless (~200MB). Demora 1-2 minutos."
playwright install chromium
```

### Passo 5 — Verifica `.env` e GEMINI_API_KEY

```bash
test -f .env && echo "ENV_EXISTS" || echo "ENV_MISSING"
```

Se `ENV_MISSING` ou (existe mas chave vazia — `grep -E "^GEMINI_API_KEY=.+" .env` falha):

**Não peça pro aluno editar arquivo manualmente.** Crie o `.env` por ele:

1. Pergunta no chat:
   > "Pra eu poder gerar textos e imagens com IA, preciso de uma chave gratuita do Google Gemini.
   >
   > 1. Abre este link em outra aba: https://aistudio.google.com/app/apikey
   > 2. Faz login com sua conta Google
   > 3. Clica em **'Create API key'** (botão azul no canto superior direito)
   > 4. Copia a chave que aparece (começa com `AIza...`)
   > 5. Cola aqui na conversa
   >
   > Pode mandar a chave aqui que eu salvo do jeito certo no arquivo `.env`."

2. Quando o aluno colar a chave, valida o formato:
   - Deve começar com `AIza`
   - Deve ter ~39 caracteres
   - Sem espaços nas pontas (faz `.strip()`)
   - Se não bater: "Hmm, isso não parece uma chave Gemini válida. Confere se você copiou tudo? Deve começar com `AIza`."

3. Use a tool **Write** pra criar `.env` na raiz do projeto com este conteúdo (substitua `{CHAVE}` pelo valor colado pelo aluno):
   ```
   GEMINI_API_KEY={CHAVE}
   GEMINI_TEXT_MODEL=gemini-2.5-flash
   GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
   ```

4. Confirma com mensagem curta: "✅ Chave salva. Vou testar agora se está funcionando..."

5. Pula direto pro Passo 6 (teste real).

**Importante**: depois de salvar, **nunca mais leia o conteúdo do `.env` nem mencione a chave em mensagens**. Se precisar validar de novo, use o script de teste do Passo 6.

### Passo 6 — Testa a chave Gemini com chamada real

```bash
python3 scripts/gemini_text.py --test
```

O script `--test` faz um ping mínimo na API e retorna `OK` ou erro descritivo.

Se erro `401`/`403`: chave inválida — pede pra gerar outra.
Se erro `429`: cota esgotada — explica e sugere esperar 24h.

### Passo 7 — Confirma sucesso

Quando tudo passa, mostra resumo curto:

> ✅ Python 3.12 — ok
> ✅ google-genai, playwright, dotenv, pillow — instalados
> ✅ Chromium headless — pronto
> ✅ Chave Gemini — funcionando
>
> Bora criar um anúncio. Estático ou carrossel?

## Manuseio da chave Gemini

A chave do Gemini é credencial pessoal do aluno — vazá-la dá acesso à conta dele e queima a cota grátis. Por isso:

- Não faça `cat .env` nem leia o conteúdo dele em nenhum momento. Use `grep -E "^GEMINI_API_KEY=.+" .env > /dev/null` que só checa se existe linha com chave preenchida, sem mostrar o valor.
- Para validar a chave de fato, rode `python3 scripts/gemini_text.py --test`. O script lê via `os.getenv`, faz uma chamada mínima e devolve só `OK` ou erro descritivo (401/403/429) — sem expor a chave em nenhum log.
- Se o aluno te pedir pra "ver a chave que tá salva", explique que você não imprime o valor por segurança e oriente ele a abrir o `.env` no editor dele.

## Erros conhecidos

| Sintoma | Causa | Fix |
|---|---|---|
| `pip: command not found` | pip não no PATH | Use `python3 -m pip` |
| `error: externally-managed-environment` (Mac/Linux) | PEP 668 bloqueia install global | Sugere criar venv: `python3 -m venv .venv && source .venv/bin/activate && pip install -r scripts/requirements.txt` |
| Playwright install lento ou trava | Download de 200MB | Aguarde até 5 min antes de cancelar |
| `playwright: command not found` após install | Instalado em local não-PATH | Use `python3 -m playwright install chromium` |
| Permission denied no `pip install` | Tentou instalar sem venv ou sudo | Use venv (recomendado) ou `pip install --user` |

## Quando NÃO invocar

- Se o setup já foi validado nesta sessão (não fica refazendo)
- Se o aluno está no meio de um fluxo (`criar-estatico`/`criar-carrossel`) e o erro é de outro tipo
