-- Databricks notebook source
-- Rodar uma vez no Free Edition: catálogo, schemas e Volume de landing.
CREATE CATALOG IF NOT EXISTS comex;
CREATE SCHEMA IF NOT EXISTS comex.bronze;
CREATE VOLUME IF NOT EXISTS comex.bronze.landing;
CREATE VOLUME IF NOT EXISTS comex.bronze._checkpoints;
