import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_DB   = os.environ.get("MYSQL_DB", "adventureworks")
MYSQL_USER = os.environ.get("MYSQL_USER", "awuser")
MYSQL_PASS = os.environ.get("MYSQL_PASSWORD", "awpass")
MYSQL_URL  = f"jdbc:mysql://{MYSQL_HOST}:3306/{MYSQL_DB}?serverTimezone=UTC"

spark = (SparkSession.builder
         .appName("mysql-to-hive")
         .enableHiveSupport()
         .getOrCreate())

spark.sql("CREATE DATABASE IF NOT EXISTS adventureworks")

# Discover tables
tables = (spark.read
    .format("jdbc")
    .option("url", MYSQL_URL)
    .option("driver", "com.mysql.cj.jdbc.Driver")
    .option("dbtable", "information_schema.tables")
    .option("user", MYSQL_USER)
    .option("password", MYSQL_PASS)
    .load()
    .filter((col("TABLE_SCHEMA") == MYSQL_DB) & (col("TABLE_TYPE") == "BASE TABLE"))
    .select("TABLE_NAME")
    .distinct()
    .collect())

table_names = [r["TABLE_NAME"] for r in tables]

# Optional: only specific tables (comma-separated)
only = os.environ.get("ONLY_TABLES")
if only:
    only_set = {t.strip().lower() for t in only.split(",") if t.strip()}
    table_names = [t for t in table_names if t.lower() in only_set]

# Limit for CI smoke runs
limit = os.environ.get("SMOKE_TABLE_LIMIT")
if limit and not only:
    try:
        n = int(limit)
        table_names = sorted(table_names)[:max(1, n)]
    except Exception:
        table_names = sorted(table_names)[:1]

# Column casts for problematic types (examples)
BLOBY_COLUMNS = {"document": ["Document"], "productphoto": ["LargePhoto", "ThumbNailPhoto"]}
VARBINARY_HINT = {"rowguid"}  # simple hint

for t in sorted(table_names):
    try:
        df = (spark.read.format("jdbc")
              .option("url", MYSQL_URL)
              .option("driver", "com.mysql.cj.jdbc.Driver")
              .option("dbtable", t)
              .option("user", MYSQL_USER)
              .option("password", MYSQL_PASS)
              .load())

        if t in BLOBY_COLUMNS:
            for c in BLOBY_COLUMNS[t]:
                if c in df.columns:
                    df = df.withColumn(c, col(c).cast("string"))
        for c in VARBINARY_HINT:
            if c in df.columns:
                df = df.withColumn(c, col(c).cast("string"))

        spark.sql("USE adventureworks")
        df.write.mode("overwrite").saveAsTable(f"adventureworks.{t}")
        print(f"[OK] {t}")
    except Exception as e:
        print(f"[WARN] Failed to import {t}: {e}")
