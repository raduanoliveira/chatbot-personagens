# Guia de Configuração CI/CD no GitHub

Este guia explica como configurar CI/CD para este projeto usando GitHub Actions.

## 📋 Pré-requisitos

- Repositório no GitHub
- Acesso de administrador ao repositório
- Docker Hub account (opcional, apenas se quiser publicar imagens)

## 🚀 Passos para Configurar

### 1. Criar o Repositório no GitHub

Se ainda não criou:

1. Acesse [GitHub](https://github.com)
2. Clique em **New repository**
3. Preencha:
   - **Repository name**: `chatbot-personagens` (ou o nome que preferir)
   - **Description**: Sistema de chatbot com gerenciamento de personagens
   - **Visibility**: Escolha Public ou Private
   - **NÃO** marque "Initialize with README" (já temos um)
4. Clique em **Create repository**

### 2. Fazer Push do Código

```bash
# Se ainda não inicializou o git
git init
git add .
git commit -m "Initial commit"

# Adicione o remote do GitHub
git remote add origin https://github.com/raduanoliveira/chatbot-personagens.git

# Faça push
git branch -M main
git push -u origin main
```

### 3. Configurar Secrets para Docker Hub

Para publicar imagens Docker automaticamente no Docker Hub:

#### Passo 1: Criar Access Token no Docker Hub

1. Acesse [Docker Hub](https://hub.docker.com/) e faça login
2. Clique no seu perfil (canto superior direito) > **Account Settings**
3. Vá em **Security** (no menu lateral)
4. Clique em **New Access Token**
5. Preencha:
   - **Description**: `github-actions` (ou qualquer nome)
   - **Access permissions**: Selecione **Read & Write**
6. Clique em **Generate**
7. **IMPORTANTE**: Copie o token agora (você só verá uma vez!)
   - Exemplo: `dckr_pat_xxxxxxxxxxxxxxxxxxxx`

#### Passo 2: Configurar Secrets no GitHub

1. No seu repositório GitHub, vá em **Settings**
2. No menu lateral: **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Adicione os seguintes secrets:

   **DOCKER_USERNAME**
   - Name: `DOCKER_USERNAME`
   - Secret: Seu usuário do Docker Hub (ex: `raduanoliveira`)

   **DOCKER_PASSWORD**
   - Name: `DOCKER_PASSWORD`
   - Secret: O token de acesso que você criou (não use a senha!)

   **VITE_API_URL** (opcional)
   - Name: `VITE_API_URL`
   - Secret: URL da sua API em produção (ex: `https://api.seudominio.com`)
   - Se não configurar, usará `http://localhost:8000` como padrão

### 4. Verificar os Workflows

Os workflows já estão configurados em `.github/workflows/`:

- ✅ **ci.yml**: Executa em cada push/PR
- ✅ **cd.yml**: Executa em push para `main` ou tags

### 5. Testar o CI

1. Faça uma pequena alteração no código
2. Faça commit e push:
   ```bash
   git add .
   git commit -m "Test CI workflow"
   git push
   ```
3. No GitHub, vá em **Actions** (no menu superior)
4. Você verá o workflow rodando em tempo real
5. Aguarde a conclusão (deve levar alguns minutos)

### 6. Verificar Status

- ✅ **Verde**: Tudo passou
- ❌ **Vermelho**: Algum erro (clique para ver detalhes)

### 7. Verificar Imagens no Docker Hub

Após o workflow de CD executar com sucesso:

1. **Acesse o Docker Hub**:
   - Backend: `https://hub.docker.com/r/SEU_USUARIO/chatpersonagens-backend`
   - Frontend: `https://hub.docker.com/r/SEU_USUARIO/chatpersonagens-frontend`
   - Substitua `SEU_USUARIO` pelo seu usuário do Docker Hub

2. **Tags disponíveis**:
   - `latest`: Sempre a última versão da branch `main`
   - `{commit-sha}`: Versão específica de um commit
   - `{tag}`: Se você criar uma tag (ex: `v1.0.0`)

3. **Usar as imagens**:
   ```bash
   # Pull das imagens
   docker pull SEU_USUARIO/chatpersonagens-backend:latest
   docker pull SEU_USUARIO/chatpersonagens-frontend:latest
   
   # Ou use no docker-compose.yml
   # Substitua as imagens locais pelas do Docker Hub
   ```

## 📊 O que os Workflows Fazem

### CI (Continuous Integration)

**Backend:**
- Instala dependências Python
- Verifica sintaxe do código
- Testa conexão com banco de dados

**Frontend:**
- Instala dependências Node.js
- Executa linter (ESLint)
- Faz build de produção

**Docker:**
- Constrói imagens Docker
- Valida que o build funciona

### CD (Continuous Deployment)

**Deploy:**
- Constrói imagens Docker otimizadas
- Publica no Docker Hub (se configurado)
- Pronto para deploy em servidor

## 🔧 Personalização

### Adicionar Testes

Se quiser adicionar testes automatizados:

1. **Backend**: Adicione testes em `backend/tests/`
2. **Frontend**: Adicione testes em `frontend/src/__tests__/`
3. Atualize `.github/workflows/ci.yml` para executar os testes

### Deploy Automático

Para fazer deploy automático em um servidor:

1. Adicione secrets para acesso ao servidor:
   - `SSH_PRIVATE_KEY`: Chave SSH privada
   - `SSH_HOST`: IP/hostname do servidor
   - `SSH_USER`: Usuário SSH

2. Adicione step de deploy no `.github/workflows/cd.yml`:
   ```yaml
   - name: Deploy to server
     uses: appleboy/ssh-action@master
     with:
       host: ${{ secrets.SSH_HOST }}
       username: ${{ secrets.SSH_USER }}
       key: ${{ secrets.SSH_PRIVATE_KEY }}
       script: |
         cd /path/to/app
         docker compose pull
         docker compose up -d
   ```

## 🐛 Troubleshooting

### Workflow falha no build do frontend

- Verifique se `VITE_API_URL` está configurado corretamente
- Veja os logs clicando no workflow que falhou

### Workflow falha no build do backend

- Verifique se todas as dependências estão em `requirements.txt`
- Veja os logs para identificar qual dependência está faltando

### Imagens Docker não são publicadas

- Verifique se `DOCKER_USERNAME` e `DOCKER_PASSWORD` estão configurados
- Verifique se você tem permissão para publicar no Docker Hub

## 📚 Recursos

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com/)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## ✅ Checklist

- [ ] Repositório criado no GitHub
- [ ] Código enviado para o GitHub
- [ ] Secrets configurados (se necessário)
- [ ] Primeiro workflow executado com sucesso
- [ ] Badge de status adicionado ao README (opcional)

---

**Pronto!** Seu CI/CD está configurado. Cada push/PR será testado automaticamente! 🎉

