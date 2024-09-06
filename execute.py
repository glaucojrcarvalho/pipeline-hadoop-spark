from pyspark.sql import SparkSession

# Inicializando a nossa sessao spark para trabalhar com SQL no Hadoop/Hive

spark_session = SparkSession \
				.builder \
				.enableHiveSupport() \
				.appName("spark sql") \
				.master("local") \
				.getOrCreate()


# A operações no hadoop são limitadas, em geral imutável, sendo necessário substituir a nova coleção de dados.
# Para este projeto criaremos uma tabela temporária para receber os valores que não sofrerão alteração, em seguida 
# atribuímos o valor da tabela temporária para a dimensão que vai sofrer a alteração.

spark_session.sql(" CREATE TABLE adventureworks.temp_culture SELECT * FROM adventureworks.culture WHERE cultureid NOT LIKE '%ar%' ")

spark_session.sql(" INSERT INTO adventureworks.temp_culture VALUES ('AR', 'Arabic', now())")

spark_session.sql(" DROP TABLE adventureworks.culture ")

spark_session.sql(" CREATE TABLE adventureworks.culture SELECT * FROM adventureworks.temp_culture ")

spark_session.sql(" DROP TABLE adventureworks.temp_culture ")

spark_session.sql(" SELECT * FROM adventureworks.culture ").show()