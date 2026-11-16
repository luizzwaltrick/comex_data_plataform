-- Tabela transacional observada pelo CDC (Debezium).
CREATE TABLE IF NOT EXISTS operacao (
    id          bigserial PRIMARY KEY,
    fluxo       char(3)  NOT NULL CHECK (fluxo IN ('EXP', 'IMP')),
    ano         smallint NOT NULL,
    mes         smallint NOT NULL CHECK (mes BETWEEN 1 AND 12),
    co_ncm      char(8)  NOT NULL,
    co_pais     integer  NOT NULL,
    sg_uf       char(2)  NOT NULL,
    co_via      smallint NOT NULL,
    co_urf      integer  NOT NULL,
    kg_liquido  numeric(18, 2) NOT NULL,
    vl_fob      numeric(18, 2) NOT NULL,
    vl_frete    numeric(18, 2),
    vl_seguro   numeric(18, 2),
    atualizado  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (fluxo, ano, mes, co_ncm, co_pais, sg_uf, co_via, co_urf)
);
