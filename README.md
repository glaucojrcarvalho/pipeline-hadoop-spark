## Introdução
<p> Data Warehouse (DS) tem com objetivo centralizar dados extraídos de diversas fontes para consultas e projetos de B.I, para este projeto vamos utilizar o Apache Hadoop, Apache Hive e Apache Spark, softwares livres voltados para computação distribuída com grandes volumes de dados. </p>

<p> SCD (Slowly Changing Dimension) que significa dimensão de alteração lenta, é uma técnica para atualizar a tabela dimensão, existem vários tipos de SCD's, neste projeto utilizaremos SCD do tipo 1 realizando a alteração sem deixar histórico na dimensão.</p>

<p>	Nosso objetivo neste projeto é construir um Data Warehouse utilizando Hadoop e Hive, em seguida realizar uma SCD utilizando Spark. </p>

### ! IMPORTANTE: Neste experimento foram utilizadas as seguintes versões de sistema:
##### Projeto criado em 2018 e atualizado em 2020, pode ser que algumas versões não sejam mais compatível, necessário validar.
- CentOS Linux 7;
- MySQL  Ver 8.0.20;
- Hadoop 3.2.0;
- Hive 3.1.1;
- Spark 2.4.4;
- Sqoop 1.4.7;

#### 1) O dump do banco de dados está anexo neste projeto, nosso trabalho começa importando os dados no MySQL.
<p> Utilize o script abaixo para fazer a importação: 

    mysql -u {usuário} -p < ./AWBackup.sql

Obs. Substitua o {usuário} pelo seu usuário do banco de dados, certifique-se de digitar o comando no terminal no endereço dos arquivos.
</p>

#### 2) Criação do DW no Hadoop e Hive.
<p> Utilize o script abaixo para criação do DW:

    ./execute.sh

Obs. +- 1 hora de processamento.
Certifique-se que deu tudo certo na transação, visualize as mensagens de LOG no terminal.
</p>

#### 3) Execução da SCD no spark.
<p> Utilize o script abaixo para execução da SCD:
  
    spark-submit execute.py
</p>
