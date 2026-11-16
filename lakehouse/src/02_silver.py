# Databricks notebook source
# Silver: estado atual de cada operação. Aplica o último evento de cada id (insert, update
# ou delete). Como a entrega do Kafka é "pelo menos uma vez", eventos repetidos são
# descartados aqui: o MERGE só aplica evento mais novo que o já gravado.
from pyspark.sql import Window
from pyspark.sql import functions as F

catalogo = dbutils.widgets.get("catalogo")
destino = f"{catalogo}.silver.operacao"

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {destino} (
    id BIGINT, fluxo STRING, ano INT, mes INT, data_ref DATE, co_ncm STRING, co_pais INT,
    sg_uf STRING, co_via INT, co_urf INT, kg_liquido DOUBLE, vl_fob DOUBLE, vl_frete DOUBLE,
    vl_seguro DOUBLE, vl_cif DOUBLE, ts_ms BIGINT
) PARTITIONED BY (fluxo, ano)
""")

ultimo = Window.partitionBy("id").orderBy(F.col("ts_ms").desc())
frete_seguro = F.coalesce("vl_frete", F.lit(0)) + F.coalesce("vl_seguro", F.lit(0))

(spark.table(f"{catalogo}.bronze.operacao_eventos")
    .withColumn("_n", F.row_number().over(ultimo))
    .where("_n = 1")
    .withColumn("data_ref", F.make_date("ano", "mes", F.lit(1)))
    .withColumn("vl_cif", F.when(F.col("fluxo") == "IMP", F.col("vl_fob") + frete_seguro))
    .createOrReplaceTempView("ultimos_eventos"))

spark.sql(f"""
MERGE INTO {destino} t
USING ultimos_eventos s ON t.id = s.id
WHEN MATCHED AND s.deletado AND s.ts_ms >= t.ts_ms THEN DELETE
WHEN MATCHED AND s.ts_ms > t.ts_ms THEN UPDATE SET
    fluxo = s.fluxo, ano = s.ano, mes = s.mes, data_ref = s.data_ref, co_ncm = s.co_ncm,
    co_pais = s.co_pais, sg_uf = s.sg_uf, co_via = s.co_via, co_urf = s.co_urf,
    kg_liquido = s.kg_liquido, vl_fob = s.vl_fob, vl_frete = s.vl_frete,
    vl_seguro = s.vl_seguro, vl_cif = s.vl_cif, ts_ms = s.ts_ms
WHEN NOT MATCHED AND NOT s.deletado THEN INSERT (
    id, fluxo, ano, mes, data_ref, co_ncm, co_pais, sg_uf, co_via, co_urf,
    kg_liquido, vl_fob, vl_frete, vl_seguro, vl_cif, ts_ms
) VALUES (
    s.id, s.fluxo, s.ano, s.mes, s.data_ref, s.co_ncm, s.co_pais, s.sg_uf, s.co_via, s.co_urf,
    s.kg_liquido, s.vl_fob, s.vl_frete, s.vl_seguro, s.vl_cif, s.ts_ms
)
""")
