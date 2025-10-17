from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("smoke-check")
         .enableHiveSupport()
         .getOrCreate())

spark.sql("CREATE DATABASE IF NOT EXISTS adventureworks")
spark.sql("USE adventureworks")

dbs = spark.sql("SHOW DATABASES").collect()
print("[SMOKE] Databases:", [r.databaseName for r in dbs])

tables = spark.sql("SHOW TABLES IN adventureworks").collect()
print("[SMOKE] Tables:", [(r.tableName, r.isTemporary) for r in tables])

assert len(tables) >= 1, "Expected at least one table in adventureworks after ingestion"
print("[SMOKE] OK - at least one table present.")
