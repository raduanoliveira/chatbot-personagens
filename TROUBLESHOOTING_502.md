# Troubleshooting: 502 Bad Gateway e Erro de CORS

## Problema

O frontend está recebendo:
- **502 Bad Gateway** ao tentar acessar o backend
- **CORS Error**: `No 'Access-Control-Allow-Origin' header is present`

## Causa

O erro 502 indica que o **backend não está respondendo**. Isso geralmente acontece quando:
1. O backend não está rodando
2. O backend está crashando durante a inicialização
3. As migrations estão falhando e impedindo o backend de iniciar

O erro de CORS é **consequência** do 502 - se o backend não responde, não pode retornar headers CORS.

## Diagnóstico

### 1. Verificar Logs do Backend no Railway

1. Acesse o Railway Dashboard
2. Vá para o serviço do backend
3. Clique em **"Deploy Logs"** ou **"Logs"**
4. Procure por:
   - `❌ ERRO CRÍTICO: Migrations falharam`
   - `Can't locate revision identified by`
   - `ModuleNotFoundError`
   - `OperationalError` ou `Connection refused`
   - `RuntimeError`

### 2. Verificar Variáveis de Ambiente

No Railway, verifique se as seguintes variáveis estão configuradas no serviço do backend:

```bash
ALLOWED_ORIGINS="https://frontend-chatbot-personagens-production.up.railway.app"
DB_HOST="mysql.railway.internal"
DB_PORT="3306"
DB_NAME="railway"
DB_USER="root"
DB_PASSWORD="<sua-senha>"
OPENAI_API_KEY="<sua-key>"
MODERATION_ENABLED="true"
MODERATION_LEVEL="moderate"
```

**Importante**: `ALLOWED_ORIGINS` deve incluir a URL exata do frontend com `https://`.

### 3. Testar Health Check do Backend

Tente acessar diretamente no navegador:
```
https://backend-chatbot-personagens-production.up.railway.app/health
```

Se retornar `{"status":"ok"}`, o backend está funcionando.
Se retornar 502 ou erro, o backend não está rodando.

### 4. Verificar Status do MySQL

No Railway, verifique se o serviço MySQL está:
- ✅ **Running** (verde)
- ✅ Conectado ao backend

## Soluções

### Solução 1: Limpar Tabela alembic_version Manualmente

Se o erro for `Can't locate revision identified by 'fa3c80dae25c'`:

1. No Railway, abra o **Terminal** do serviço MySQL
2. Execute:
```sql
USE railway;
DELETE FROM alembic_version;
```

3. No Railway, abra o **Terminal** do serviço backend
4. Execute:
```bash
alembic upgrade head
```

5. Reinicie o serviço backend (force redeploy)

### Solução 2: Verificar e Corrigir ALLOWED_ORIGINS

1. No Railway, vá para o serviço backend
2. Vá em **Variables**
3. Verifique se `ALLOWED_ORIGINS` está configurado como:
   ```
   https://frontend-chatbot-personagens-production.up.railway.app
   ```
   (sem espaços, sem trailing slash)

4. Se não estiver, adicione ou atualize
5. Force um redeploy do backend

### Solução 3: Verificar Conexão com MySQL

1. No Railway, verifique se o serviço MySQL está rodando
2. Verifique se `DB_HOST` está como `mysql.railway.internal`
3. Verifique se `DB_PASSWORD` está correto
4. Force um redeploy do backend

### Solução 4: Rebuild Completo

Se nada funcionar:

1. No Railway, vá para o serviço backend
2. Clique em **Settings**
3. Clique em **Delete Service** (cuidado!)
4. Crie um novo serviço
5. Configure todas as variáveis de ambiente novamente
6. Conecte ao repositório GitHub
7. Configure o Root Directory como `backend`
8. Configure a porta como `7000`

## Prevenção

Para evitar problemas futuros:

1. ✅ Sempre verifique os logs após um deploy
2. ✅ Mantenha `ALLOWED_ORIGINS` atualizado com a URL do frontend
3. ✅ Use `mysql.railway.internal` para `DB_HOST` (não use IPs ou URLs públicas)
4. ✅ Verifique se as migrations estão rodando corretamente

## Comandos Úteis

### Ver logs em tempo real (Railway Terminal)
```bash
# No terminal do backend
tail -f /proc/1/fd/1
```

### Testar conexão MySQL (Railway Terminal)
```bash
# No terminal do backend
python3 -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); print(conn.execute(text('SELECT 1')).fetchone())"
```

### Verificar variáveis de ambiente (Railway Terminal)
```bash
# No terminal do backend
env | grep -E "(DB_|ALLOWED_|OPENAI_)"
```

