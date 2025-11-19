# Troubleshooting - Imagens Docker Hub

## ❌ Problema: "Page not found" no Docker Hub

Se você está vendo "Page not found" ao acessar `https://hub.docker.com/r/raduanoliveira/chatpersonagens-backend`, siga estes passos:

### 1. Verificar se o Workflow Executou

1. No GitHub, vá em **Actions**
2. Procure pelo workflow **"CD"**
3. Clique no último workflow executado
4. Verifique:
   - ✅ Todos os steps estão verdes?
   - ❌ Algum step falhou?

### 2. Verificar os Logs do Workflow

No workflow de CD, verifique os logs dos steps:

**"Login to Docker Hub"**
- Se falhou: Verifique se `DOCKER_USERNAME` e `DOCKER_PASSWORD` estão configurados
- Se pulou (skipped): Os secrets não estão configurados

**"Build and push backend image"**
- Procure por mensagens como:
  - `Pushed` ou `published` = ✅ Sucesso
  - `denied` ou `unauthorized` = ❌ Problema de autenticação
  - `not found` = ❌ Problema com o nome da imagem

### 3. Verificar Secrets Configurados

1. No GitHub: **Settings** > **Secrets and variables** > **Actions**
2. Verifique se existem:
   - ✅ `DOCKER_USERNAME` (deve ser `raduanoliveira`)
   - ✅ `DOCKER_PASSWORD` (deve ser o token, não a senha)

### 4. Verificar Token do Docker Hub

1. Acesse [Docker Hub](https://hub.docker.com/) > **Account Settings** > **Security**
2. Verifique se o token existe e tem permissão **Read & Write**
3. Se necessário, crie um novo token e atualize o secret `DOCKER_PASSWORD`

### 5. Testar Push Manual

Para testar se suas credenciais funcionam:

```bash
# Login no Docker Hub
docker login -u raduanoliveira

# Build local
docker build -t raduanoliveira/chatpersonagens-backend:test ./backend

# Push manual
docker push raduanoliveira/chatpersonagens-backend:test
```

Se funcionar, o problema está no workflow. Se não funcionar, o problema está nas credenciais.

### 6. Verificar Nome do Repositório

O nome do repositório no Docker Hub deve ser exatamente:
- `raduanoliveira/chatpersonagens-backend`
- `raduanoliveira/chatpersonagens-frontend`

**Importante**: 
- O nome é case-sensitive
- Não pode ter maiúsculas (Docker Hub só aceita minúsculas)
- Não pode ter espaços ou caracteres especiais

### 7. Verificar Visibilidade do Repositório

Por padrão, repositórios no Docker Hub são **públicos**. Se você criou como privado:
- Acesse: https://hub.docker.com/r/raduanoliveira/chatpersonagens-backend/settings
- Mude para **Public** (se quiser que seja público)

### 8. Aguardar Propagação

Após o push, pode levar alguns minutos para aparecer no Docker Hub. Aguarde 2-5 minutos e tente novamente.

### 9. Verificar no Docker Hub

1. Acesse: https://hub.docker.com/u/raduanoliveira
2. Você deve ver os repositórios listados lá
3. Se não aparecer, o push não aconteceu

## ✅ Checklist de Verificação

- [ ] Workflow "CD" executou?
- [ ] Todos os steps do workflow passaram?
- [ ] Secrets `DOCKER_USERNAME` e `DOCKER_PASSWORD` estão configurados?
- [ ] O token do Docker Hub tem permissão "Read & Write"?
- [ ] O nome do usuário está correto (case-sensitive)?
- [ ] Aguardou alguns minutos após o push?
- [ ] Tentou acessar: https://hub.docker.com/u/raduanoliveira (página do usuário)?

## 🔍 Comandos Úteis

```bash
# Verificar se consegue fazer login
docker login -u raduanoliveira

# Verificar imagens locais
docker images | grep chatpersonagens

# Tentar pull (se a imagem existir)
docker pull raduanoliveira/chatpersonagens-backend:latest
```

## 📞 Se Nada Funcionar

1. Verifique os logs completos do workflow no GitHub Actions
2. Copie as mensagens de erro
3. Verifique se o token do Docker Hub não expirou
4. Tente criar um novo token e atualizar o secret

