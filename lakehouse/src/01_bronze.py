# Databricks notebook source
# Bronze: histórico bruto dos eventos de CDC. O Auto Loader lê só os arquivos novos do Volume.
catalogo = dbutils.widgets.get("catalogo")
origem = f"/Volumes/{catalogo}/bronze/landing/operacao/"
checkpoint = f"/Volumes/{catalogo}/bronze/checkpoints/operacao"

(spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", checkpoint)
    .load(origem)
    .selectExpr("*", "_metadata.file_path AS _arquivo", "current_timestamp() AS _ingerido_em")
    .writeStream
    .option("checkpointLocation", checkpoint)
    .trigger(availableNow=True)
    .toTable(f"{catalogo}.bronze.operacao_eventos"))
