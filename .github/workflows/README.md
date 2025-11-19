# GitHub Actions Workflows

Este diretório contém os workflows de CI/CD para o projeto.

## Workflows Disponíveis

### CI (Continuous Integration)
**Arquivo:** `.github/workflows/ci.yml`

Executa automaticamente em:
- Push para branches `main` ou `develop`
- Pull requests para `main` ou `develop`

**Jobs:**
1. **Backend**: Verifica sintaxe, instala dependências, testa conexão com banco
2. **Frontend**: Instala dependências, executa linter, faz build
3. **Docker Build**: Constrói as imagens Docker para validação

### CD (Continuous Deployment)
**Arquivo:** `.github/workflows/cd.yml`

Executa automaticamente em:
- Push para branch `main`
- Tags que começam com `v*` (ex: `v1.0.0`)

**Jobs:**
1. **Deploy**: Constrói e publica imagens Docker (se configurado)

## Configuração

### Secrets Necessários (opcional, para CD)

Se quiser publicar imagens Docker no Docker Hub:

1. Vá em **Settings** > **Secrets and variables** > **Actions**
2. Adicione os seguintes secrets:
   - `DOCKER_USERNAME`: Seu usuário do Docker Hub
   - `DOCKER_PASSWORD`: Sua senha/token do Docker Hub
   - `VITE_API_URL`: URL da API em produção (opcional)

### Variáveis de Ambiente

Os workflows usam variáveis padrão, mas você pode configurar:
- `VITE_API_URL`: URL da API para build do frontend

