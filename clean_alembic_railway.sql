-- Script para limpar a tabela alembic_version no Railway
-- Execute este script no terminal do MySQL no Railway

USE railway;

-- Mostra a revisão atual (se existir)
SELECT * FROM alembic_version;

-- Limpa todas as revisões antigas
DELETE FROM alembic_version;

-- Confirma que está vazio
SELECT * FROM alembic_version;

-- Se preferir dropar e recriar a tabela completamente:
-- DROP TABLE IF EXISTS alembic_version;

