from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("scd-type1-culture")
         .enableHiveSupport()
         .getOrCreate())

spark.sql("USE adventureworks")

# ACID/MERGE settings
spark.sql("SET hive.txn.manager=org.apache.hadoop.hive.ql.lockmgr.DbTxnManager")
spark.sql("SET hive.support.concurrency=true")
spark.sql("SET hive.exec.dynamic.partition=true")
spark.sql("SET hive.exec.dynamic.partition.mode=nonstrict")

spark.sql("""
CREATE TABLE IF NOT EXISTS adventureworks.culture (
  cultureid STRING,
  name      STRING,
  modifieddate TIMESTAMP
)
STORED AS ORC
TBLPROPERTIES ('transactional'='true')
""")

spark.sql("DROP TABLE IF EXISTS adventureworks.temp_culture")
spark.sql("""
CREATE TABLE adventureworks.temp_culture AS
SELECT * FROM adventureworks.culture WHERE cultureid NOT LIKE '%ar%'
""")
spark.sql("INSERT INTO adventureworks.temp_culture VALUES ('AR', 'Arabic', current_timestamp())")

spark.sql("""
MERGE INTO adventureworks.culture AS tgt
USING adventureworks.temp_culture AS src
ON (tgt.cultureid = src.cultureid)
WHEN MATCHED THEN UPDATE SET
  tgt.name = src.name,
  tgt.modifieddate = src.modifieddate
WHEN NOT MATCHED THEN INSERT *
""")

spark.sql("DROP TABLE adventureworks.temp_culture")

spark.sql("SELECT * FROM adventureworks.culture ORDER BY cultureid").show(truncate=False)
