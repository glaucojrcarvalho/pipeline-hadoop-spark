SHELL := /bin/bash

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

mysql-load:
	docker exec -i mysql mysql -u$$MYSQL_USER -p$$MYSQL_PASSWORD < /docker-entrypoint-initdb.d/AWBackup.sql

ingest:
	docker exec spark-master /opt/spark/bin/spark-submit --master local[*] \
	  --conf spark.sql.warehouse.dir=/warehouse \
	  --conf spark.sql.catalogImplementation=hive \
	  /workspace/scripts/import_mysql_to_hive.py

scd1:
	docker exec spark-master /opt/spark/bin/spark-submit --master local[*] \
	  --conf spark.sql.warehouse.dir=/warehouse \
	  --conf spark.sql.hive.convertMetastoreParquet=false \
	  /workspace/jobs/scd_type1_culture.py

scd2:
	docker exec spark-master /opt/spark/bin/spark-submit --master local[*] /workspace/jobs/scd_type2_culture.py
