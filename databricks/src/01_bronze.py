# Databricks notebook source
# Bronze: Auto Loader lê incrementalmente os Parquet que o consumer Kafka gravou no Volume.
catalogo = dbutils.widgets.get("catalogo")
origem = f"/Volumes/{catalogo}/bronze/landing/operacoes/"
checkpoint = f"/Volumes/{catalogo}/bronze/_checkpoints/operacoes"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalogo}.bronze")

(spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", checkpoint)
    .load(origem)
    .selectExpr("*", "_metadata.file_path AS _arquivo", "current_timestamp() AS _ingerido_em")
    .writeStream
    .option("checkpointLocation", checkpoint)
    .trigger(availableNow=True)
    .toTable(f"{catalogo}.bronze.operacoes"))
