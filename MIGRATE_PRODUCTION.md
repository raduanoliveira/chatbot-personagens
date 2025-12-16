# 🔄 Executar Migrations no Railway - Guia Rápido

Se você está recebendo erro 500 ao carregar personagens, provavelmente as migrations não foram executadas no Railway.

## 🚀 Solução Rápida

### Opção 1: Via Terminal do Railway (Recomendado)

1. Acesse o dashboard do Railway: https://railway.app
2. Clique no seu projeto
3. Clique no serviço **backend**
4. Vá na aba **"Deployments"**
5. Clique no deployment mais recente
6. Clique em **"View Logs"** ou **"Open Terminal"**
7. Execute:
   ```bash
   alembic upgrade head
   ```

### Opção 2: Via Variável de Ambiente (Automático)

1. No Railway, clique no serviço **backend**
2. Vá na aba **"Variables"**
3. Adicione uma nova variável:
   - **Nome**: `RUN_MIGRATIONS`
   - **Valor**: `true`
4. Faça um novo deploy (Railway vai executar as migrations automaticamente)

### Opção 3: Via Command no Railway

1. No Railway, clique no serviço **backend**
2. Vá na aba **"Settings"**
3. Role até **"Deploy Command"** ou **"Start Command"**
4. Altere para:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

## ✅ Verificar se Funcionou

1. Acesse a URL do backend: `https://sua-url-backend.railway.app/api/characters/`
2. Deve retornar uma lista de personagens (mesmo que vazia)
3. Se ainda der erro, verifique os logs do Railway

## 🔍 Verificar Estrutura do Banco

Se quiser verificar se as migrations foram executadas:

1. No Railway, acesse o serviço **MySQL**
2. Vá na aba **"Data"** ou use um cliente MySQL
3. Verifique se existe:
   - Tabela `phrases`
   - Coluna `who_is_character` na tabela `characters`
   - Coluna `image_url` deve ser `TEXT` (não `VARCHAR(500)`)

## ⚠️ Importante

- As migrations são **destrutivas** - elas vão **apagar** os dados antigos
- Se você tem personagens importantes, faça backup antes
- A migration `001_refactor_characters_with_phrases.py` vai:
  - Dropar a tabela `characters` antiga
  - Criar a nova estrutura
  - Recriar o personagem Mario com as novas frases

