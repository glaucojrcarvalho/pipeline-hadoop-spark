# Data Warehouse with Hadoop, Hive, and Spark — Modernized (2025)

[![CI](https://github.com/glaucojrcarvalho/pipeline-hadoop-spark/actions/workflows/ci.yml/badge.svg)](https://github.com/glaucojrcarvalho/pipeline-hadoop-spark/actions/workflows/ci.yml)

> **Background**: This is a refreshed, reproducible version of a 2018/2020 educational project. It uses **Docker** and **Spark JDBC** (instead of Sqoop) to build a small **Hive-based DW** and demonstrate **SCD Type 1 & Type 2** with PySpark.

## Goals
- Run a single-node lab with Hadoop + Hive + Spark via `docker-compose`.
- Load **AdventureWorks (MySQL)** into **Hive** using **Spark JDBC** (no Sqoop).
- Demonstrate **SCD Type 1** (overwrite) and **SCD Type 2** (history) with Spark SQL.
- Keep the door open for ACID tables (MERGE) and/or Lakehouse formats (Iceberg/Delta) — optional.

## Stack
- **MySQL 8.0** (source)
- **Hadoop 3.3.x**
- **Hive 3.1.x** (PostgreSQL metastore for this lab)
- **Spark 3.5.x** (with Hive support)
- **Python 3.11** for PySpark jobs

> This is a **lab** setup. For production, use an external Hive metastore, configure compaction for ACID tables, tune memory/CPU, and consider Lakehouse formats.

---

## Quick start

### 1) Download the AdventureWorks dump
Place the dump under `./data/AWBackup.sql`. Example:

```bash
mkdir -p data
curl -L -o data/AWBackup.sql "https://raw.githubusercontent.com/glaucojrcarvalho/pipeline-hadoop-spark/refs/heads/main/AWBackup.sql"
```

### 2) Environment variables
```bash
cp .env.example .env
# edit user/password for MySQL if needed
```

### 3) Bring the stack up
```bash
make up
# wait ~1–3 minutes for services to stabilize
```

### 4) Load MySQL with the dump
```bash
make mysql-load
```

### 5) Ingest tables from MySQL -> Hive (Spark JDBC)
```bash
make ingest
```

### 6) Run SCD examples
```bash
make scd1   # SCD Type 1 (MERGE overwrite)
make scd2   # SCD Type 2 (history)
```

> **Tip:** This project writes to Hive managed tables in the `adventureworks` database. You can open Beeline or PySpark to explore:
>
> ```bash
> docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -n root -p root
> docker exec -it spark-master /opt/spark/bin/pyspark --master local[*]
> ```

---

## Project structure
```
.
├── .github/workflows/ci.yml     # Lint + dockerized smoke test on PRs, PR comment
├── .github/workflows/nightly.yml# Nightly SCD1/SCD2
├── conf/
├── data/
│   └── AWBackup.sql             # put the dump here
├── jobs/
│   ├── scd_type1_culture.py     # SCD1 example with Hive MERGE
│   └── scd_type2_culture.py     # SCD2 example (history range)
├── scripts/
│   ├── import_mysql_to_hive.py  # JDBC-based ingestion (no Sqoop)
│   └── smoke_check.py           # tiny Spark/Hive connectivity & table check
├── .env.example
├── docker-compose.yml
├── Makefile
├── pyproject.toml               # ruff (lint) config
└── README.md
```

---

## Implementation notes

### Ingestion (Spark JDBC)
- We query `information_schema.tables` to list tables in `adventureworks`.
- We cast known problematic columns (e.g., BLOB/VARBINARY) to `STRING` on the destination.
- We save into Hive using `saveAsTable("adventureworks.<table>")`.

Environment knobs for CI:
- `SMOKE_TABLE_LIMIT`: if set (e.g., `1`), the import script will only ingest the first *N* tables alphabetically.
- `ONLY_TABLES`: a comma-separated list to ingest **only** those tables (e.g., `ONLY_TABLES=culture`). When provided, it takes precedence over `SMOKE_TABLE_LIMIT`.

### SCD
- **Type 1**: overwrite-by-key semantics using `MERGE INTO` on Hive ACID table (`TBLPROPERTIES ('transactional'='true')`).
- **Type 2**: `valid_from`, `valid_to`, `is_current` columns to maintain history. Simplified example.

---

## CI & Nightly

- **CI** (`.github/workflows/ci.yml`): Lint + spin up stack + ingest a small subset + smoke test. Also posts a **PR comment** with the smoke log.
- **Nightly** (`.github/workflows/nightly.yml`): Runs daily at 02:00 UTC; ingests `culture` and executes **SCD Type 1 & 2** to ensure queries remain healthy.

---

## License
MIT
