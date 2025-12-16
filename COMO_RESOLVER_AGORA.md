# Como Resolver o Erro 502 no Railway - PASSO A PASSO

## Situação Atual

O backend está retornando **502 Bad Gateway** porque não consegue iniciar. O problema é que a tabela `alembic_version` ainda contém referência à migration antiga que não existe mais.

## Solução: Limpar a Tabela alembic_version

### Passo 1: Acessar o Terminal do MySQL no Railway

1. Acesse https://railway.app/
2. Entre no seu projeto
3. Clique no serviço **MySQL** (não no backend!)
4. No menu superior, clique em **"Data"** ou **"Query"**
5. Você verá uma interface para executar queries SQL

### Passo 2: Executar o SQL

Cole e execute este comando:

```sql
USE railway;
DELETE FROM alembic_version;
```

### Passo 3: Verificar o Resultado

Execute para confirmar:

```sql
SELECT * FROM alembic_version;
```

Deve retornar vazio (0 linhas).

### Passo 4: Force Redeploy do Backend

1. Vá para o serviço **backend** no Railway
2. Clique nos 3 pontinhos (⋯) no canto superior direito
3. Clique em **"Redeploy"**
4. Aguarde o deploy completar

### Passo 5: Verificar os Logs

1. No serviço backend, clique em **"Deploy Logs"**
2. Procure por:
   - ✅ `Migrations executadas com sucesso!`
   - ✅ `Iniciando servidor uvicorn na porta 7000`
   
Se aparecer:
   - ❌ `Can't locate revision identified by` → volte ao Passo 2
   - ❌ `Connection refused` → verifique se MySQL está rodando

### Passo 6: Testar o Health Check

Acesse no navegador:
```
https://backend-chatbot-personagens-production.up.railway.app/health
```

Deve retornar:
```json
{"status":"ok"}
```

### Passo 7: Testar o Frontend

Acesse:
```
https://frontend-chatbot-personagens-production.up.railway.app
```

Deve carregar os personagens normalmente.

---

## Alternativa: Via Terminal do Backend (se preferir)

Se você preferir executar via terminal do backend:

1. No Railway, vá para o serviço **backend**
2. Clique em **"Terminal"** ou **"Shell"**
3. Execute:

```bash
python3 << 'EOF'
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    rows = result.fetchall()
    print(f"Revisão atual: {rows}")
    
    conn.execute(text("DELETE FROM alembic_version"))
    conn.commit()
    print("✅ Tabela alembic_version limpa!")
EOF
```

4. Depois, reinicie o backend:
```bash
exit
```

5. O Railway vai reiniciar automaticamente e executar as migrations.

---

## Se ainda não funcionar

Compartilhe os logs do backend aqui para eu analisar. Para copiar:

1. No Railway, serviço **backend**
2. Clique em **"Deploy Logs"**
3. Copie toda a saída
4. Cole aqui na conversa

---

## Verificar Variáveis de Ambiente

Enquanto isso, verifique se estas variáveis estão configuradas no serviço **backend**:

```
ALLOWED_ORIGINS=https://frontend-chatbot-personagens-production.up.railway.app
DB_HOST=mysql.railway.internal
DB_PORT=3306
DB_NAME=railway
DB_USER=root
DB_PASSWORD=<sua-senha-do-mysql>
OPENAI_API_KEY=<sua-key>
MODERATION_ENABLED=true
MODERATION_LEVEL=moderate
```

**Importante**: Não deve ter espaços extras, aspas, ou vírgulas no `ALLOWED_ORIGINS`.

