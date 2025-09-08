# Makefile для управления проектом TDP

.PHONY: help check migrate static deploy build up down logs clean

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

check: ## Проверить миграции и настройки Django
	docker compose run --rm web python manage.py makemigrations --check --dry-run
	docker compose run --rm web python manage.py check

migrate: ## Применить миграции
	docker compose run --rm web python manage.py migrate --noinput

static: ## Собрать статические файлы
	docker compose run --rm web python manage.py collectstatic --noinput

build: ## Собрать Docker образ
	docker compose build

up: ## Запустить сервисы
	docker compose up -d

down: ## Остановить сервисы
	docker compose down

logs: ## Показать логи
	docker compose logs -f

clean: ## Очистить неиспользуемые Docker ресурсы
	docker system prune -f
	docker volume prune -f

deploy: migrate static up ## Полный деплой: миграции + статика + запуск

reload-caddy: ## Перезагрузить Caddy
	docker compose restart caddy

# Команды для разработки
dev-up: ## Запустить в режиме разработки
	docker compose -f compose.yml -f compose.dev.yml up -d

dev-logs: ## Логи в режиме разработки
	docker compose -f compose.yml -f compose.dev.yml logs -f
