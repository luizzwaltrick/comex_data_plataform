# Databricks notebook source
# Gold: balança comercial mensal, pronta para o Power BI (SQL Warehouse).
catalogo = dbutils.widgets.get("catalogo")

spark.sql(f"""
CREATE OR REPLACE TABLE {catalogo}.gold.fct_balanca_mensal AS
SELECT data_ref, sg_uf, co_pais, substr(co_ncm, 1, 2) AS co_sh2,
       SUM(CASE WHEN fluxo = 'EXP' THEN vl_fob ELSE 0 END) AS vl_exportacao,
       SUM(CASE WHEN fluxo = 'IMP' THEN vl_fob ELSE 0 END) AS vl_importacao,
       SUM(CASE WHEN fluxo = 'EXP' THEN vl_fob ELSE -vl_fob END) AS saldo,
       SUM(kg_liquido) AS kg_liquido
FROM {catalogo}.silver.operacao
GROUP BY ALL
""")
spark.sql(f"OPTIMIZE {catalogo}.gold.fct_balanca_mensal ZORDER BY (data_ref, sg_uf)")
