# Troubleshooting - Network Error ao carregar personagens

## Problema: "Network Error" ao tentar listar personagens

### Possíveis causas:

1. **Migrations não foram executadas**
   - O banco de dados ainda tem a estrutura antiga (com `system_prompt` e sem `who_is_character` e `phrases`)
   - Execute as migrations: `alembic upgrade head`

2. **Backend não está rodando**
   - Verifique se o backend está ativo
   - Verifique os logs do backend para erros

3. **Estrutura do banco incompatível**
   - Se o banco tem a estrutura antiga, a query falhará ao tentar fazer `joinedload(Character.phrases)`
   - Solução: Execute as migrations ou recrie o banco

### Como resolver:

1. **Verificar se as migrations foram executadas:**
   ```bash
   # Executar migrations dentro do container do backend
   docker compose -f docker-compose.dev.yml exec backend alembic current
   docker compose -f docker-compose.dev.yml exec backend alembic upgrade head
   
   # Ou, se estiver rodando em modo produção:
   docker compose exec backend alembic upgrade head
   ```

2. **Verificar logs do backend:**
   - Procure por erros relacionados a `phrases`, `who_is_character`, ou `system_prompt`

3. **Recriar o banco (se necessário):**
   ```bash
   # CUIDADO: Isso apagará todos os dados!
   # Executar dentro do container do backend
   docker compose -f docker-compose.dev.yml exec backend alembic downgrade base
   docker compose -f docker-compose.dev.yml exec backend alembic upgrade head
   ```

4. **Verificar estrutura do banco:**
   ```sql
   -- Verificar se a tabela phrases existe
   SHOW TABLES LIKE 'phrases';
   
   -- Verificar estrutura da tabela characters
   DESCRIBE characters;
   ```

### Erro comum:

Se você ver o erro:
```
OperationalError: (1054, "Unknown column 'who_is_character' in 'field list'")
```

Isso significa que as migrations não foram executadas. Execute:
```bash
alembic upgrade head
```

