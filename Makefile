SHELL := /bin/bash

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

mysql-load:
	cat data/AWBackup.sql | docker exec -i mysql mysql -uawuser -pawpass adventureworks

ingest:
	docker exec spark-master /opt/spark/bin/spark-submit --master local[*] \
	  --packages mysql:mysql-connector-java:8.0.33 \
	  --conf spark.sql.warehouse.dir=/warehouse \
	  --conf spark.sql.catalogImplementation=hive \
	  --conf spark.driver.extraClassPath=/root/.ivy2.5.2/jars/com.mysql_mysql-connector-j-8.0.33.jar \
	  /workspace/scripts/import_mysql_to_hive.py

scd1:
	docker exec spark-master /opt/spark/bin/spark-submit --master local[*] \
	  --packages mysql:mysql-connector-java:8.0.33 \
	  --conf spark.sql.warehouse.dir=/warehouse \
	  --conf spark.sql.hive.convertMetastoreParquet=false \
	  /workspace/jobs/scd_type1_culture.py

scd2:
	docker exec spark-master /opt/spark/bin/spark-submit --master local[*] \
	  --packages mysql:mysql-connector-java:8.0.33 \
	  /workspace/jobs/scd_type2_culture.py
