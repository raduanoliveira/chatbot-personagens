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

# Limpa cache e node_modules para reduzir tamanho
RUN rm -rf node_modules package*.json .npm

# Production stage
FROM nginx:alpine

# Copia arquivos buildados
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

