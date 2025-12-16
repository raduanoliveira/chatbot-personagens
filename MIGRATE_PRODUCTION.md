# 🔄 Executar Migrations no Railway - Guia Rápido

Se você está recebendo erro 500 ao carregar personagens, provavelmente as migrations não foram executadas no Railway.

## 🚀 Solução Mais Simples: Forçar Novo Deploy

O `start.sh` já executa as migrations automaticamente. Se não executou, force um novo deploy:

1. Acesse o dashboard do Railway: https://railway.app
2. Clique no seu projeto
3. Clique no serviço **backend**
4. Vá na aba **"Settings"**
5. Role até **"Deploy"** ou **"Redeploy"**
6. Clique em **"Redeploy"** ou **"Deploy Latest"**
7. Aguarde o deploy terminar
8. Verifique os logs para ver se as migrations foram executadas

## 🔧 Solução Alternativa: Via Settings (Start Command)

1. No Railway, clique no serviço **backend**
2. Vá na aba **"Settings"**
3. Role até **"Deploy"** ou procure por **"Start Command"** ou **"Command"**
4. Se encontrar, altere para garantir que as migrations rodem:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Salve e faça um novo deploy

## 📋 Verificar se as Migrations Foram Executadas

1. No Railway, clique no serviço **backend**
2. Vá na aba **"Deployments"**
3. Clique no deployment mais recente
4. Clique em **"View Logs"**
5. Procure por mensagens como:
   - `✅ Migrations executadas com sucesso!`
   - `INFO  [alembic.runtime.migration] Running upgrade ...`
   - `Running upgrade 001_refactor_characters_with_phrases -> 931b714a7d45`

## ✅ Verificar se Funcionou

1. Acesse a URL do backend: `https://sua-url-backend.railway.app/api/characters/`
2. Deve retornar uma lista de personagens (mesmo que vazia)
3. Se ainda der erro, verifique os logs do Railway

## 🔍 Como Ver os Logs no Railway

1. No Railway, clique no serviço **backend**
2. Vá na aba **"Deployments"** (ou **"Logs"**)
3. Clique no deployment mais recente
4. Você verá os logs do container
5. Procure por:
   - `📊 Tentativa X/10: Executando migrations...`
   - `✅ Migrations executadas com sucesso!`
   - Ou mensagens de erro do Alembic

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

