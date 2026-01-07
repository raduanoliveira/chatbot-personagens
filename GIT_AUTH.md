# 🔐 Como Resolver Autenticação do Git

## ❌ Erro Atual
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed
```

## ✅ Soluções

### Opção 1: Usar SSH (Recomendado - Mais Seguro)

#### Passo 1: Gerar chave SSH
```bash
ssh-keygen -t ed25519 -C "seu-email@example.com"
# Pressione Enter para aceitar o local padrão
# Pressione Enter para não usar senha (ou defina uma se preferir)
```

#### Passo 2: Copiar a chave pública
```bash
cat ~/.ssh/id_ed25519.pub
```

#### Passo 3: Adicionar no GitHub
1. Acesse: https://github.com/settings/keys
2. Clique em **"New SSH key"**
3. Dê um título (ex: "Meu Notebook")
4. Cole o conteúdo da chave pública
5. Clique em **"Add SSH key"**

#### Passo 4: Alterar o remote para SSH
```bash
cd /home/raduan/projetos/ia/chatbot-personagens
git remote set-url origin git@github.com:raduanoliveira/chatbot-personagens.git
```

#### Passo 5: Testar conexão
```bash
ssh -T git@github.com
# Deve retornar: "Hi raduanoliveira! You've successfully authenticated..."
```

#### Passo 6: Fazer push
```bash
git push origin main
```

---

### Opção 2: Usar Token de Acesso Pessoal (Mais Rápido)

#### Passo 1: Criar token no GitHub
1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Dê um nome (ex: "chatbot-personagens")
4. Selecione escopos: **`repo`** (marca tudo)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (você só verá ele uma vez!)

#### Passo 2: Configurar o Git para usar o token
```bash
cd /home/raduan/projetos/ia/chatbot-personagens
git remote set-url origin https://SEU_TOKEN@github.com/raduanoliveira/chatbot-personagens.git
```

**OU** usar o Git Credential Manager:
```bash
git config --global credential.helper store
# Na primeira vez que fizer push, digite:
# Username: raduanoliveira
# Password: SEU_TOKEN
```

#### Passo 3: Fazer push
```bash
git push origin main
```

---

### Opção 3: Usar GitHub CLI (gh)

#### Passo 1: Instalar GitHub CLI
```bash
# Ubuntu/Debian
sudo apt install gh

# Ou via snap
sudo snap install gh
```

#### Passo 2: Autenticar
```bash
gh auth login
# Escolha: GitHub.com → HTTPS → Login with web browser
```

#### Passo 3: Fazer push
```bash
git push origin main
```

---

## 🎯 Qual Opção Escolher?

- **SSH**: Melhor para uso contínuo, mais seguro, não expira
- **Token**: Mais rápido de configurar, mas precisa renovar periodicamente
- **GitHub CLI**: Bom se você já usa outras ferramentas do GitHub

---

## ✅ Verificar Configuração Atual

```bash
# Ver remote atual
git remote -v

# Ver configuração do Git
git config --list | grep -E "(user|credential|remote)"
```

---

## 🆘 Ainda com Problemas?

1. Verifique se o repositório existe: https://github.com/raduanoliveira/chatbot-personagens
2. Verifique se você tem permissão de escrita no repositório
3. Tente fazer um `git pull` primeiro para testar a conexão

