-- Cadastros (OLTP) replicados para o Kafka via CDC (Debezium).
CREATE TABLE IF NOT EXISTS pais (
    co_pais     integer PRIMARY KEY,
    no_pais     text NOT NULL,
    bloco       text,
    atualizado  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ncm (
    co_ncm      char(8) PRIMARY KEY,
    no_ncm      text NOT NULL,
    co_sh2      char(2) NOT NULL,
    atualizado  timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE pais REPLICA IDENTITY FULL;
ALTER TABLE ncm  REPLICA IDENTITY FULL;
