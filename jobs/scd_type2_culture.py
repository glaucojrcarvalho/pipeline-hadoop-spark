from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("scd-type2-culture")
         .enableHiveSupport()
         .getOrCreate())

spark.sql("USE adventureworks")

spark.sql("""
CREATE TABLE IF NOT EXISTS adventureworks.dim_culture_scd2 (
  surrogate_key BIGINT,
  cultureid     STRING,
  name          STRING,
  valid_from    TIMESTAMP,
  valid_to      TIMESTAMP,
  is_current    BOOLEAN
)
STORED AS ORC
TBLPROPERTIES ('transactional'='true')
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS adventureworks.src_culture_current AS
SELECT cultureid, name, current_timestamp() AS snapshot_ts
FROM adventureworks.culture
""")

spark.sql("SET hive.txn.manager=org.apache.hadoop.hive.ql.lockmgr.DbTxnManager")
spark.sql("SET hive.support.concurrency=true")

spark.sql("""
UPDATE adventureworks.dim_culture_scd2 d
SET d.valid_to = current_timestamp(), d.is_current = false
WHERE d.is_current = true
  AND EXISTS (
    SELECT 1 FROM adventureworks.src_culture_current s
    WHERE s.cultureid = d.cultureid
      AND s.name <> d.name
  )
""")

spark.sql("""
INSERT INTO adventureworks.dim_culture_scd2
SELECT
  CAST(UNIX_TIMESTAMP(current_timestamp())*1000 + ROW_NUMBER() OVER() AS BIGINT) AS surrogate_key,
  s.cultureid,
  s.name,
  current_timestamp() AS valid_from,
  CAST(NULL AS TIMESTAMP) AS valid_to,
  true AS is_current
FROM adventureworks.src_culture_current s
LEFT JOIN adventureworks.dim_culture_scd2 d
  ON d.cultureid = s.cultureid AND d.is_current = true
WHERE d.cultureid IS NULL OR d.name <> s.name
""")

spark.sql(
    "SELECT * FROM adventureworks.dim_culture_scd2 ORDER BY cultureid, valid_from"
).show(truncate=False)
