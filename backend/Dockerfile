# Build stage - instala dependências que precisam de compilação
FROM python:3.12-slim AS builder

WORKDIR /app

# Instala dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .

# Instala torch CPU-only primeiro (muito menor: ~200-300MB vs ~1.6GB)
# A versão CPU-only reduz drasticamente o tamanho da imagem
RUN pip install --no-cache-dir --user --index-url https://download.pytorch.org/whl/cpu torch>=2.0.0

# Instala as demais dependências (detoxify precisa do torch já instalado)
# Remove torch e linhas vazias/comentários do requirements.txt
RUN sed '/^torch/d; /^#/d; /^$/d' requirements.txt > /tmp/requirements_no_torch.txt && \
    pip install --no-cache-dir --user -r /tmp/requirements_no_torch.txt && \
    rm /tmp/requirements_no_torch.txt

# Production stage - imagem final menor
FROM python:3.12-slim

WORKDIR /app

# Instala apenas dependências de runtime (sem compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências Python instaladas do builder
COPY --from=builder /root/.local /root/.local

# Garante que o Python encontre os pacotes instalados
ENV PATH=/root/.local/bin:$PATH

# Configura PYTHONPATH para incluir o diretório de trabalho
ENV PYTHONPATH=/app

# Copia apenas o código da aplicação (não requirements.txt)
COPY . .

# Debug: lista arquivos após cópia para diagnosticar problemas no Railway
RUN echo "=== Estrutura de diretórios após COPY ===" && \
    ls -la /app && \
    echo "=== Conteúdo de app/ ===" && \
    ls -la /app/app/ 2>/dev/null || echo "ERRO: app/ não encontrado" && \
    echo "=== Conteúdo de app/core/ ===" && \
    ls -la /app/app/core/ 2>/dev/null || echo "ERRO: app/core/ não encontrado" && \
    echo "=== Verificando app/core/config.py ===" && \
    test -f /app/app/core/config.py && echo "✅ app/core/config.py encontrado" || echo "❌ app/core/config.py NÃO encontrado"

# Expõe a porta
EXPOSE 7000

# Comando para iniciar a aplicação
# Executa migrations antes de iniciar o servidor
# Garante que estamos no diretório correto e que o PYTHONPATH está configurado
CMD sh -c "cd /app && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 7000"


