# Comex Data Platform

Plataforma de dados de comércio exterior brasileiro com a base pública **Comex Stat (MDIC)**: streaming com Kafka, CDC do PostgreSQL, infraestrutura na Oracle Cloud com Terraform e lakehouse no Databricks, até chegar ao Power BI.

## Arquitetura

```
Comex Stat (CSV) ──► Producer ──► Kafka (comex.operacoes) ──► Consumer ──► Volume Databricks (Parquet)
PostgreSQL (pais, ncm) ──► Debezium CDC ──► Kafka (cdc.public.*)                     │
                                                                                     ▼
                      Databricks: Auto Loader ─► bronze ─► silver (MERGE Delta) ─► gold ─► Power BI
```

## Onde roda (custo zero)

| Peça | Onde | Plano gratuito |
|---|---|---|
| Kafka, PostgreSQL, Debezium, Kafka UI, producer e consumer | VM na **Oracle Cloud**, via Docker Compose | Always Free: ARM Ampere 4 OCPU / 24 GB e 200 GB de disco, sem prazo |
| Infraestrutura da VM | **Terraform** (provider OCI) | grátis |
| Lakehouse (bronze/silver/gold, job agendado) | **Databricks Free Edition** | serverless, sem cartão |
| CI | **GitHub Actions** | grátis em repositório público |
| Desenvolvimento | sua máquina com Docker | o mesmo `docker-compose.yml` |

A VM só abre SSH para o seu IP. Kafka UI (8080) e Postgres (5432) ficam no localhost da VM e são acessados por túnel SSH (`terraform output tunel_ssh`).

| Camada | Tecnologia | O que demonstra |
|---|---|---|
| Ingestão | Python, `confluent-kafka` | producer idempotente (`acks=all`), chave de partição, consumer com commit manual após gravar |
| CDC | PostgreSQL 16 + Debezium | replicação lógica (`wal_level=logical`) dos cadastros para o Kafka |
| Cloud | Oracle Cloud + Terraform | VCN, sub-rede, firewall restrito, VM provisionada com cloud-init |
| Lakehouse | Databricks (PySpark, Delta, Auto Loader, Unity Catalog) | medalhão, `MERGE` idempotente, `OPTIMIZE ZORDER`, job via Asset Bundle |
| Qualidade | pytest, ruff, GitHub Actions | CI com testes, lint e `terraform validate` |

## Como rodar

1. **Databricks:** crie a conta Free Edition, rode `databricks/src/00_setup.sql` e gere um token.
2. **VM:** `cd infra/terraform && terraform init && terraform apply -var compartment_id=... -var meu_ip_cidr=SEU_IP/32`.
3. **Na VM** (ou local):

```bash
git clone https://github.com/luizzwaltrick/comex_data_plataform && cd comex_data_plataform
cp .env.example .env    # preencher senha e token
docker compose up -d
curl -X POST -H "Content-Type: application/json" --data @connect/postgres-cdc.json localhost:8083/connectors
docker compose run --rm produtor produzir exp --ano 2024
docker compose run --rm consumidor
```

4. **Lakehouse:** `cd databricks && databricks bundle deploy -t dev && databricks bundle run comex_medalhao`.

## Próximos passos

- [ ] Schema Registry + Avro no lugar de JSON
- [ ] Consumer Spark Structured Streaming lendo direto do Kafka
- [ ] Dimensões a partir do CDC (SCD tipo 2 em `dim_pais`/`dim_ncm`)
- [ ] Expectations de qualidade (Great Expectations) na silver
- [ ] Dashboard Power BI conectado ao SQL Warehouse
