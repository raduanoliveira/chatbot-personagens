# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copia package files
COPY package*.json ./

# Instala dependências (incluindo devDependencies para build)
RUN npm ci --no-audit --no-fund

# Copia código fonte
COPY . .

# ARG para variáveis de build
ARG VITE_API_URL=http://localhost:7000
ENV VITE_API_URL=$VITE_API_URL

# Build da aplicação
RUN npm run build

# Debug: mostra a URL da API que foi usada no build
RUN echo "🔍 VITE_API_URL usado no build: $VITE_API_URL" && \
    echo "📁 Verificando arquivos buildados..." && \
    ls -la /app/dist && \
    echo "📄 Verificando se a URL está no código..." && \
    grep -r "VITE_API_URL\|localhost:7000\|localhost:8000" /app/dist || echo "⚠️  URL não encontrada nos arquivos buildados"

# Limpa cache e node_modules para reduzir tamanho
RUN rm -rf node_modules package*.json .npm

# Production stage
FROM nginx:alpine

# Copia arquivos buildados
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Cria diretório de logs e garante permissões
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /usr/share/nginx/html

# Testa configuração do nginx antes de iniciar
RUN nginx -t

EXPOSE 80

# Inicia nginx em foreground
CMD ["nginx", "-g", "daemon off;"]

