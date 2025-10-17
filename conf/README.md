# Configuration Directory

This directory is reserved for future Hadoop/Hive/Spark configuration files.

## Potential configurations:
- `hive-site.xml` - Custom Hive configuration
- `spark-defaults.conf` - Spark defaults
- `core-site.xml`, `hdfs-site.xml` - Hadoop configurations
- Custom log4j properties

Currently, the project uses default configurations from the Docker images.
To customize, add configuration files here and mount them in `docker-compose.yml`.
