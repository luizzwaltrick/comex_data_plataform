-- Databricks notebook source
-- Rodar uma vez no Free Edition: catálogo, schemas e Volumes.
CREATE CATALOG IF NOT EXISTS comex;
CREATE SCHEMA IF NOT EXISTS comex.bronze;
CREATE SCHEMA IF NOT EXISTS comex.silver;
CREATE SCHEMA IF NOT EXISTS comex.gold;
CREATE VOLUME IF NOT EXISTS comex.bronze.landing;
CREATE VOLUME IF NOT EXISTS comex.bronze.checkpoints;
