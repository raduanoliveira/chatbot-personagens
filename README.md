# Chatbot Personagens 💬

[![CI](https://github.com/SEU_USUARIO/chatbot-personagens/actions/workflows/ci.yml/badge.svg)](https://github.com/SEU_USUARIO/chatbot-personagens/actions/workflows/ci.yml)

Sistema completo de chatbot com gerenciamento de personagens, interface web moderna e moderação de conteúdo integrada.

## 🚀 Funcionalidades

- **Gerenciamento de Personagens**: Interface web completa para criar, editar e gerenciar personagens de chatbot
- **Chat Interativo**: Interface de chat em tempo real com os personagens
- **Moderação de Conteúdo**: Sistema de guardrails integrado para prevenir conteúdo inadequado
- **Pré-visualização de Imagens**: Preview automático ao adicionar URLs de imagens
- **Layout Responsivo**: Interface otimizada para desktop e mobile
- **Validação de Formulários**: Validação completa com feedback visual

---

## 📋 Pré-requisitos

- Python 3.12+
- Node.js 20+
- MySQL 8.0+ (ou compatível)
- Chave da API OpenAI
- Docker e Docker Compose (para deploy com containers)

---

## 🏗️ Arquitetura

O projeto possui três camadas principais:

1. **Backend (FastAPI + MySQL)**: API REST para gerenciamento de personagens e chat
2. **Frontend (React + Vite)**: Interface web moderna e responsiva
3. **Moderação (Guardrails)**: Sistema de moderação de conteúdo usando ML

---

## 🛠️ Instalação e Configuração

### 1. Dependências Python

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 2. Backend (FastAPI)

#### Estrutura
```
backend/
├── app/
│   ├── api/routes/      # Rotas da API (characters, chat)
│   ├── core/            # Configurações e guardrails
│   ├── models/          # Modelos SQLAlchemy
│   └── schemas/         # Schemas Pydantic
├── alembic/             # Migrations do banco
└── env.example          # Modelo de variáveis de ambiente
```

#### Configuração

1. Copie `backend/env.example` para `backend/.env` e configure:

```env
# Banco de Dados
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mario_chat
DB_USER=usuario
DB_PASSWORD=senha

# OpenAI
OPENAI_API_KEY=sua-chave-aqui

# Moderação de Conteúdo
MODERATION_ENABLED=true
MODERATION_LEVEL=moderate  # strict, moderate, permissive
```

2. Execute as migrations:

```bash
cd backend
alembic upgrade head
```

3. Inicie o servidor:

```bash
uvicorn app.main:app --reload --app-dir backend
```

A API estará disponível em `http://localhost:8000`
- Documentação: `http://localhost:8000/docs`
- Endpoints: `/api/characters`, `/api/chat`

### 3. Frontend (React + Vite)

#### Estrutura
```
frontend/
├── src/
│   ├── api/             # Cliente API
│   ├── components/      # Componentes React
│   ├── pages/           # Páginas principais
│   └── types/           # Tipos TypeScript
├── public/              # Arquivos estáticos
└── Dockerfile           # Build de produção
```

#### Configuração

1. Instale as dependências:

```bash
cd frontend
npm install
```

2. Configure a URL da API (opcional):

```bash
cp frontend/env.example frontend/.env
# Edite VITE_API_URL se necessário
```

3. Execute em modo desenvolvimento:

```bash
npm run dev
```

Acesse `http://localhost:5173` para a interface web.

4. Build de produção:

```bash
npm run build
```

Os arquivos estarão em `frontend/dist/`.

---

## 🐳 Deploy com Docker

A forma mais simples de fazer deploy é usando Docker Compose.

### Pré-requisitos
- Docker instalado e rodando
- Docker Compose instalado

### Passos para Deploy

1. **Configure as variáveis de ambiente:**

```bash
cp docker-compose.env.example .env
```

Edite o arquivo `.env` e configure:
- `OPENAI_API_KEY`: sua chave da OpenAI
- `DB_PASSWORD`: senha do banco de dados
- `MYSQL_ROOT_PASSWORD`: senha root do MySQL
- `MODERATION_ENABLED`: habilitar moderação (true/false)
- `MODERATION_LEVEL`: nível de moderação (strict/moderate/permissive)

2. **Modo Desenvolvimento (com hot-reload):**

```bash
docker compose -f docker-compose.dev.yml up -d
```

- Frontend: `http://localhost:5173` (Vite dev server)
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

3. **Modo Produção:**

```bash
docker compose up -d
```

- Frontend: `http://localhost:8080` (Nginx)
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Comandos Úteis

**Usando Make:**
```bash
make docker-up      # Inicia serviços (produção)
make docker-down    # Para serviços
make docker-logs    # Ver logs
make docker-ps      # Status dos containers
make docker-build   # Reconstruir imagens
make clean          # Limpar tudo (containers, volumes, imagens)
```

**Usando Docker Compose:**
```bash
# Produção
docker compose up -d
docker compose down
docker compose logs -f

# Desenvolvimento
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml logs -f

# Reconstruir
docker compose build
docker compose -f docker-compose.dev.yml build frontend
```

---

## 🔒 Moderação de Conteúdo (Guardrails)

O sistema inclui moderação automática de conteúdo usando:

- **better-profanity**: Detecção de palavrões
- **detoxify**: Detecção de toxicidade usando Machine Learning

### Configuração

Configure no arquivo `.env`:

```env
MODERATION_ENABLED=true
MODERATION_LEVEL=moderate
```

### Níveis de Moderação

- **strict**: Threshold 0.3 - Bloqueia conteúdo com baixa toxicidade
- **moderate**: Threshold 0.5 - Recomendado para uso geral
- **permissive**: Threshold 0.7 - Bloqueia apenas conteúdo extremamente tóxico

### Funcionalidades

- Moderação de entrada (mensagens do usuário)
- Moderação de saída (respostas do assistente)
- Whitelist de frases comuns para evitar falsos positivos
- Ajuste automático de threshold para textos curtos

---

## 📱 Interface Web

### Funcionalidades

- **Gerenciamento de Personagens**:
  - Criar, editar e excluir personagens
  - Validação de formulários em tempo real
  - Pré-visualização de imagens ao colar URL
  - Campo "Contexto do prompt" obrigatório
  - Botão para limpar formulário

- **Chat Interativo**:
  - Interface de chat em tempo real
  - Seleção de personagem
  - Histórico de conversa
  - Indicador de digitação

- **Layout Responsivo**:
  - Otimizado para desktop e mobile
  - Formulário deslizante no mobile
  - Navegação fluida entre telas

---

## 🗄️ Estrutura do Banco de Dados

O sistema usa MySQL com as seguintes tabelas:

- **characters**: Armazena os personagens
  - `id`: ID único
  - `name`: Nome do personagem
  - `description`: Descrição
  - `catchphrase`: Frase característica
  - `personality_traits`: Traços de personalidade (JSON)
  - `image_url`: URL da imagem
  - `system_prompt`: Prompt do sistema (obrigatório)
  - `created_at`, `updated_at`: Timestamps

---

## 🔧 Variáveis de Ambiente

### Backend (`backend/.env`)

```env
# Banco de Dados
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mario_chat
DB_USER=usuario
DB_PASSWORD=senha

# OpenAI
OPENAI_API_KEY=sua-chave-aqui

# Moderação
MODERATION_ENABLED=true
MODERATION_LEVEL=moderate
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
```

### Docker Compose (`.env`)

```env
# Banco de Dados
DB_HOST=db
DB_PORT=3306
DB_NAME=mario_chat
DB_USER=mario
DB_PASSWORD=secret
MYSQL_ROOT_PASSWORD=rootpassword

# OpenAI
OPENAI_API_KEY=sua-chave-aqui

# Frontend
VITE_API_URL=http://localhost:8000

# Moderação
MODERATION_ENABLED=true
MODERATION_LEVEL=moderate
```

---

## 📚 API Endpoints

### Personagens

- `GET /api/characters` - Lista todos os personagens
- `GET /api/characters/{id}` - Obtém um personagem
- `POST /api/characters` - Cria um personagem
- `PUT /api/characters/{id}` - Atualiza um personagem
- `DELETE /api/characters/{id}` - Remove um personagem

### Chat

- `POST /api/chat` - Envia mensagem e recebe resposta do personagem

Consulte `http://localhost:8000/docs` para documentação interativa completa.

---

## 🧪 Desenvolvimento

### Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

### Com Docker (Desenvolvimento)

```bash
docker compose -f docker-compose.dev.yml up -d
```

O frontend terá hot-reload automático na porta 5173.

---

## 📦 Dependências Principais

### Backend
- FastAPI: Framework web
- SQLAlchemy: ORM
- Alembic: Migrations
- OpenAI: API de chat
- better-profanity: Detecção de palavrões
- detoxify: Detecção de toxicidade
- PyMySQL: Driver MySQL

### Frontend
- React: Framework UI
- TypeScript: Tipagem estática
- Vite: Build tool
- React Hook Form: Gerenciamento de formulários
- Zod: Validação de schemas
- TanStack Query: Gerenciamento de estado servidor

---

## 🚀 Deploy Manual (sem Docker)

### Backend

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run build
# Sirva os arquivos de frontend/dist/ com Nginx ou outro servidor web
```

---

## 📝 Notas Importantes

- O sistema cria automaticamente o banco de dados se não existir
- O seed inicial cria o personagem "Mario Bros" automaticamente
- O sistema impede que todos os personagens sejam removidos (sempre deve existir pelo menos um)
- O campo "Contexto do prompt" é obrigatório para todos os personagens
- A moderação de conteúdo pode ser desabilitada configurando `MODERATION_ENABLED=false`

---

## 🔄 CI/CD

O projeto possui CI/CD configurado com GitHub Actions:

- **CI**: Executa automaticamente em cada push/PR
  - Lint e build do frontend
  - Verificação do backend
  - Build de imagens Docker

- **CD**: Executa em push para `main` ou tags
  - Publica imagens Docker (se configurado)

📖 **Veja o guia completo**: [CI_CD_SETUP.md](./CI_CD_SETUP.md)

## 🔮 Próximos Passos Sugeridos

- [ ] Autenticação e autorização
- [ ] Histórico de conversas persistente
- [ ] Exportação/importação de personagens
- [ ] Temas personalizáveis
- [ ] Suporte a múltiplos idiomas
- [ ] Integração com outros modelos de IA
- [ ] Testes automatizados

---

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
