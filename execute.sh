#! Importante:
	# Substitua {SEU USUÁRIO} e {SUA SENHA} para o usuário e senha do seu banco de dados, respectivamente.


# Coletando tabelas que possuem varbinary, este tipo de dado o hive não aceita, é necessário realizar um tratamento para String na hora da importação.
mysql -u{SEU USUÁRIO} -p{SUA SENHA} -e "SELECT DISTINCT table_name \
				   FROM information_schema.columns \
				   WHERE column_type LIKE '%varbinary%' \
				   AND table_schema = 'adventureworks'" > /home/hadoop/Project/tables_varbinary

# Coletando tabelas que não possuem restrições de tipos de dados
mysql -u{SEU USUÁRIO} -p{SUA SENHA} -e "SELECT DISTINCT table_name \
FROM information_schema.columns \
WHERE table_schema = 'adventureworks' \
AND table_name NOT IN (SELECT table_name \
					   FROM information_schema.columns \
					   WHERE column_type LIKE '%varbinary%' \
					   OR column_type LIKE '%blob%' \
					   AND table_schema = 'adventureworks')" > /home/hadoop/Project/tables_ok

# Tabelas que possuem dados do tipo BLOB o hive não aceita, sendo necessário realizar um tratamento.
sqoop import --connect jdbc:mysql://localhost:3306/adventureworks?serverTimezone=UTC --username {SEU USUÁRIO} \
			 --password {SUA SENHA} -m 1 --table document --map-column-hive Document=String \
			 --hive-database adventureworks --hive-import

sqoop import --connect jdbc:mysql://localhost:3306/adventureworks?serverTimezone=UTC --username {SEU USUÁRIO} \
			 --password {SUA SENHA} --table productphoto --map-column-hive LargePhoto=String \
			 --hive-database adventureworks --hive-import

sqoop import --connect jdbc:mysql://localhost:3306/adventureworks?serverTimezone=UTC --username {SEU USUÁRIO} \
			 --password {SUA SENHA} --table productphoto --map-column-hive ThumbNailPhoto=String \
			 --hive-database adventureworks --hive-import


# Removendo a primeira linha de cada arquivo
# A primeira linha consiste no cabeçalho da coluna
sed -i '1d' /home/hadoop/Project/tables_varbinary
sed -i '1d' /home/hadoop/Project/tables_ok

# Criando um script para ler o nome de cada tabela e realizar o import com a ferramenta ETL sqoop, no documento que extaímos de tabelas sem restrições de conversão.
while read table; do
	sqoop import --connect jdbc:mysql://localhost:3306/adventureworks?serverTimezone=UTC --username {SEU USUÁRIO} \
				 --password {SUA SENHA} -m 1 --table $table \
				 --hive-database adventureworks --hive-import
done </home/hadoop/Project/tables_ok

# Script para ler arquivo de tabelas com varbinary.
# Note que utilizamos o --map-column-hive para alterar o tipo de dado para String.
while read table; do
	sqoop import --connect jdbc:mysql://localhost:3306/adventureworks?serverTimezone=UTC --username {SEU USUÁRIO} \
				 --password {SUA SENHA} --table $table --map-column-hive rowguid=String \
				 --hive-database adventureworks --hive-import
done </home/hadoop/Project/tables_blob