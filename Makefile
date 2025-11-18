.PHONY: help docker-up docker-down docker-build docker-logs docker-ps clean dev-up dev-down

help:
	@echo "Comandos disponíveis:"
	@echo "  make docker-up      - Inicia todos os serviços Docker (produção)"
	@echo "  make docker-down     - Para todos os serviços Docker"
	@echo "  make docker-build    - Reconstrói as imagens Docker"
	@echo "  make docker-logs     - Mostra os logs dos containers"
	@echo "  make docker-ps       - Mostra o status dos containers"
	@echo "  make clean           - Remove containers, volumes e imagens"
	@echo "  make dev-up          - Inicia em modo desenvolvimento (com hot-reload)"
	@echo "  make dev-down        - Para o modo desenvolvimento"

docker-up:
	@echo "🚀 Iniciando serviços Docker (produção)..."
	docker compose up -d
	@echo "✅ Serviços iniciados!"
	@echo "Frontend: http://localhost:8080"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev-up:
	@echo "🚀 Iniciando serviços Docker (desenvolvimento com hot-reload)..."
	docker compose -f docker-compose.dev.yml up -d
	@echo "✅ Serviços iniciados em modo desenvolvimento!"
	@echo "Frontend (com hot-reload): http://localhost:5173"
	@echo "Backend (com hot-reload): http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "💡 Alterações no código serão refletidas automaticamente!"

dev-down:
	@echo "🛑 Parando serviços de desenvolvimento..."
	docker compose -f docker-compose.dev.yml down

docker-down:
	@echo "🛑 Parando serviços Docker..."
	docker compose down

docker-build:
	@echo "🔨 Construindo imagens Docker..."
	docker compose build --no-cache

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

clean:
	@echo "🧹 Limpando containers, volumes e imagens..."
	docker compose down -v
	docker compose -f docker-compose.dev.yml down -v
	docker system prune -f


