# Comex Data Platform

Plataforma de dados de comércio exterior brasileiro com a base pública **Comex Stat (MDIC)**: captura de mudanças (CDC) do PostgreSQL com Debezium, transporte por Kafka, lakehouse no Databricks e infraestrutura na Oracle Cloud com Terraform.

## Arquitetura

```
Comex Stat (CSV)
      │  simulador (Python): grava como se fosse o sistema transacional
      ▼
PostgreSQL ──► Debezium (CDC) ──► Kafka ──► consumer (Python) ──► Volume Databricks (Parquet)
 operacao        lê o WAL        cdc.public.operacao   │ valida                  │
                                                        └► DLQ (inválidos)        ▼
                                              Auto Loader ─► bronze ─► silver ─► gold ─► Power BI
                                                             eventos   estado    balança
                                                                       atual     mensal
```

1. **Simulador** baixa o Comex Stat e faz upsert na tabela `operacao`. Reprocessar o mesmo arquivo não duplica nada.
2. **Debezium** lê o log de transações do Postgres e publica cada insert, update e delete no Kafka.
3. **Consumer** valida cada evento. Os válidos vão em lotes para o Volume; os inválidos vão para um tópico de DLQ com o motivo. O offset só é confirmado depois que o lote foi gravado (entrega pelo menos uma vez).
4. **Lakehouse**: a bronze guarda o histórico de eventos; a silver aplica o último evento de cada registro com `MERGE` (e descarta repetidos); a gold agrega a balança mensal.

## Estrutura

```
src/comex/            aplicação (pacote Python instalável)
├── __main__.py       entrada: python -m comex <comando>
├── cli.py            argumentos e montagem das dependências
├── config.py         configuração lida do ambiente
├── models.py         Operacao, EventoOperacao e validação
├── pipelines.py      encadeia as etapas
├── extractors/       download e leitura do Comex Stat
├── repositories/     gravação no Postgres (SQL em queries.py)
├── streaming/        consumer Kafka e producer da DLQ
└── writers/          gravação no Volume do Databricks
tests/                testes unitários (pytest)
infra/
├── docker/           compose da plataforma, DDL do Postgres, conector Debezium
└── terraform/        modules/{network,compute} e environments/prod
lakehouse/            Databricks Asset Bundle (bronze, silver, gold)
```

## Onde roda (custo zero)

| Peça | Onde | Plano gratuito |
|---|---|---|
| Kafka, PostgreSQL, Debezium, Kafka UI e a aplicação | VM na **Oracle Cloud**, via Docker Compose | Always Free: ARM 4 OCPU / 24 GB, sem prazo |
| Infraestrutura da VM | **Terraform** (provider OCI) | grátis |
| Lakehouse e job agendado | **Databricks Free Edition** | serverless, sem cartão |
| CI | **GitHub Actions** | grátis em repositório público |

A VM só abre SSH para o seu IP. Kafka UI (8080) e Postgres (5432) ficam no localhost da VM e são acessados por túnel SSH (`terraform output tunel_ssh`). O mesmo compose roda na sua máquina para desenvolver.

## Como rodar

1. **Databricks:** crie a conta Free Edition, rode `lakehouse/src/00_setup.sql` e gere um token.
2. **VM (opcional, dá para rodar local):**

```bash
cd infra/terraform/environments/prod
cp terraform.tfvars.example terraform.tfvars   # preencher
terraform init && terraform apply
```

3. **Plataforma e aplicação** (na VM ou local):

```bash
cp .env.example .env    # preencher senha e token
make up
make conector
make simular ANO=2024 LIMITE=10000
make consumir
```

4. **Lakehouse:**

```bash
cd lakehouse && databricks bundle deploy -t dev && databricks bundle run comex_medalhao
```

## Desenvolvimento

```bash
pip install -e ".[dev]"
make lint test
```

## Próximos passos

- [ ] Schema Registry + Avro no lugar de JSON
- [ ] Reprocessamento da DLQ
- [ ] Consumer contínuo com Spark Structured Streaming
- [ ] Simular updates e deletes (retificações) para exercitar o MERGE
- [ ] Dashboard Power BI no SQL Warehouse
