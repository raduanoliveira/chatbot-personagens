# Chatbot Mario Bros 🍄

Agora o projeto possui três camadas:

1. **FastAPI + MySQL** para um backend com CRUD de personagens/memórias.
2. **Frontend React (Vite)** para gerenciar os personagens via navegador.
3. **Clientes existentes** (CLI `main.py` e Streamlit `app.py`) para conversar com o personagem escolhido.

---

## 1. Dependências principais

- Python 3.10+
- Node 18+
- MySQL 8 (ou compatível)
- Chave da OpenAI

Crie e ative o ambiente virtual e instale as dependências Python:

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Backend (FastAPI + MySQL)

Estrutura básica dentro de `backend/`:
- `app/` → código FastAPI (rotas, modelos, schemas)
- `alembic/` → migrations versionadas
- `env.example` → modelo de variáveis de ambiente

### Configuração
1. Copie `backend/env.example` para `backend/.env` e ajuste:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=mario_chat
   DB_USER=usuario
   DB_PASSWORD=senha
   OPENAI_API_KEY=sua-chave
   # (Opcional) Para sobrepor a URL completa:
   # DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/mario_chat
   ```
2. Rode as migrations (necessário MySQL acessível):
   ```bash
   cd backend
   alembic upgrade head
   ```
3. Suba o servidor:
   ```bash
   uvicorn app.main:app --reload --app-dir backend
   ```
   A API estará em `http://localhost:8000` (rota `/api/characters`).

---

## 3. Frontend (React + Vite)

Localizado em `frontend/`.

1. Instale as dependências:
   ```bash
   cd frontend
   npm install
   ```
2. Copie `frontend/env.example` para `frontend/.env` e ajuste o `VITE_API_URL`.
3. Execute em modo dev:
   ```bash
   npm run dev
   ```
   Abra `http://localhost:5173` para acessar o painel CRUD dos personagens.

Para gerar a build de produção:
```bash
npm run build
```

---

## 4. Clientes para conversar com o personagem

Você continua podendo conversar com os personagens diretamente:

### Streamlit (interface rápida)
```bash
streamlit run app.py
```

### Linha de comando
```bash
python main.py
```

> **Importante:** configure a chave da OpenAI via `config.py`, `.env` ou variável de ambiente antes de executar esses clientes.

---

## 5. Deploy com Docker 🐳

A forma mais simples de fazer deploy é usando Docker Compose. Tudo está configurado e pronto!

### Pré-requisitos
- Docker instalado e rodando
- Docker Compose instalado

### Passos para deploy

1. **Configure as variáveis de ambiente:**
   ```bash
   cp docker-compose.env.example .env
   ```
   Edite o arquivo `.env` e configure:
   - `OPENAI_API_KEY`: sua chave da OpenAI
   - `DB_PASSWORD`: senha do banco de dados (opcional, padrão: `secret`)
   - `MYSQL_ROOT_PASSWORD`: senha root do MySQL (opcional, padrão: `rootpassword`)

2. **Inicie todos os serviços:**
   
   **Opção 1 - Usando Make (recomendado):**
   ```bash
   make docker-up
   ```
   
   **Opção 2 - Usando Docker Compose diretamente:**
   ```bash
   docker compose up -d
   ```
   
   Isso irá:
   - Criar e iniciar o MySQL
   - Construir e iniciar o backend (FastAPI)
   - Construir e iniciar o frontend (React + Nginx)
   - Executar as migrations automaticamente (criando o banco e inserindo o Mario)

3. **Acesse a aplicação:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Comandos úteis:**
   
   **Usando Make:**
   ```bash
   make docker-up      # Inicia serviços
   make docker-down    # Para serviços
   make docker-logs    # Ver logs
   make docker-ps      # Status dos containers
   make docker-build   # Reconstruir imagens
   make clean          # Limpar tudo (containers, volumes, imagens)
   ```
   
   **Ou usando Docker Compose diretamente:**
   ```bash
   docker compose logs -f      # Ver logs
   docker compose down         # Parar serviços
   docker compose down -v      # Parar e remover volumes (apaga o banco)
   docker compose build        # Reconstruir imagens
   docker compose ps           # Status dos containers
   ```

> **Nota:** O backend aguarda o MySQL ficar saudável antes de iniciar e executa as migrations automaticamente na primeira inicialização.

---

## 6. Deploy Manual / Produção (sem Docker)

1. Configure as variáveis de ambiente (ou arquivos `.env`) tanto no backend quanto no frontend (usando os campos `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `OPENAI_API_KEY` e opcionalmente `DATABASE_URL`).
2. **Backend**
   ```bash
   cd backend
   alembic upgrade head      # cria o banco (se não existir), tabelas e já insere o Mario padrão via seed
   uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
   ```
   > **Importante:** O sistema verifica automaticamente se o banco de dados existe ao iniciar. Se não existir, ele será criado automaticamente com charset `utf8mb4`. Você só precisa garantir que o usuário MySQL tenha permissões para criar bancos de dados.
3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run build   # gera dist/
   ```
   Sirva os arquivos de `frontend/dist` com o web server de sua preferência (Nginx, Vercel, etc.).
4. Opcional: configure um serviço (systemd/Docker) para manter o `uvicorn` rodando em produção.

> Observações:
> - **Criação automática do banco:** Tanto ao rodar `alembic upgrade head` quanto ao iniciar o servidor FastAPI, o sistema verifica se o banco de dados existe e o cria automaticamente se necessário.
> - O seed garante que o personagem "Mario Bros" esteja disponível após o deploy.
> - O backend impede que todos os personagens sejam removidos (sempre deve existir pelo menos um registro).

---

## 7. Estrutura de diretórios

```
backend/     # FastAPI + Alembic + models
frontend/    # React + Vite
app.py       # Chatbot via Streamlit
main.py      # Chatbot via CLI
```

---

## Próximos passos sugeridos
- Integrar o frontend com a escolha de personagem para o chatbot.
- Adicionar autenticação no backend.
- Salvar histórico de conversas amarrado a cada persona.

