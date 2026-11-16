COMPOSE = docker compose --env-file .env -f infra/docker/docker-compose.yml
ANO ?= 2024
LIMITE ?= 10000

.PHONY: up down conector simular consumir test lint

up:            ## sobe Kafka, Postgres, Debezium e Kafka UI
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

conector:      ## registra o conector de CDC no Debezium
	curl -fsS -X POST -H "Content-Type: application/json" \
		--data @infra/docker/debezium/connectors/operacao-cdc.json localhost:8083/connectors

simular:       ## grava operações no Postgres (gera os eventos de CDC)
	$(COMPOSE) run --rm app simular exp --ano $(ANO) --limite $(LIMITE)

consumir:      ## leva os eventos do Kafka para o Volume do Databricks
	$(COMPOSE) run --rm app consumir

test:
	pytest -q

lint:
	ruff check .
