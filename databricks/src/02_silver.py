# Databricks notebook source
# Silver: tipagem, regras de qualidade e MERGE idempotente (Delta).
from pyspark.sql import functions as F

catalogo = dbutils.widgets.get("catalogo")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalogo}.silver")

CHAVE = ["fluxo", "ano", "mes", "co_ncm", "co_pais", "sg_uf", "co_via"]

df = (spark.table(f"{catalogo}.bronze.operacoes")
      .where("vl_fob >= 0 AND kg_liquido >= 0 AND length(co_ncm) = 8")
      .withColumn("data_ref", F.make_date("ano", "mes", F.lit(1)))
      .withColumn("vl_cif", F.when(F.col("fluxo") == "IMP",
                  F.col("vl_fob") + F.coalesce("vl_frete", F.lit(0)) + F.coalesce("vl_seguro", F.lit(0))))
      .dropDuplicates(CHAVE))

destino = f"{catalogo}.silver.operacoes"
if not spark.catalog.tableExists(destino):
    df.write.partitionBy("fluxo", "ano").saveAsTable(destino)
else:
    df.createOrReplaceTempView("novos")
    cond = " AND ".join(f"t.{c} = s.{c}" for c in CHAVE)
    spark.sql(f"""
        MERGE INTO {destino} t USING novos s ON {cond}
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
