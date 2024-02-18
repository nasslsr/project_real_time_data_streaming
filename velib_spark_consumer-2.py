import os
os.environ["SPARK_HOME"] = "/workspaces/project_real_time_data_streaming/spark-3.2.3-bin-hadoop2.7"
os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars /workspaces/project_real_time_data_streaming/spark-streaming-kafka-0-10-assembly_2.12-3.2.3.jar pyspark-shell'
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
import findspark
findspark.init()
from pyspark.sql import SparkSession
import pyspark.sql.functions as pysqlf
import pyspark.sql.types as pysqlt

# Todo: il faut créer un nouveau dataframe qui contient:
    # - le code postal, le nombre total de vélo disponible par code postal, le nombre total de vélo mécanique par code postal, le nombre total de vélo electrique par code postal
    # - Pousser ce nouveau dataframe vers une file kafka appéler velib-projet-clean


if __name__ == "__main__":
    # Initier spark
    spark = (SparkSession
             .builder
             .appName("news")
             .master("local[1]")
             .config("spark.sql.shuffle.partitions", 1)
             .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.3")
             .getOrCreate()
             )

    # Lire les données temps réel
    kafka_df = (spark
                .readStream
                .format("kafka")
                .option("kafka.bootstrap.servers", "localhost:9092")
                .option("subscribe", "velib-projet")
                .option("startingOffsets", "earliest")
                .load()
                )

    # Appliquer des traitements sur les données
    schema = pysqlt.StructType([
        pysqlt.StructField("stationCode", pysqlt.StringType()),
        pysqlt.StructField("station_id", pysqlt.StringType()),
        pysqlt.StructField("num_bikes_available", pysqlt.IntegerType()),
        pysqlt.StructField("numBikesAvailable", pysqlt.IntegerType()),
        pysqlt.StructField("num_bikes_available_types",
                           pysqlt.ArrayType(pysqlt.MapType(pysqlt.StringType(), pysqlt.IntegerType()))),
        pysqlt.StructField("num_docks_available", pysqlt.IntegerType()),
        pysqlt.StructField("numDocksAvailable", pysqlt.IntegerType()),
        pysqlt.StructField("is_installed", pysqlt.IntegerType()),
        pysqlt.StructField("is_returning", pysqlt.IntegerType()),
        pysqlt.StructField("is_renting", pysqlt.IntegerType()),
        pysqlt.StructField("last_reported", pysqlt.TimestampType())
    ])

    # Transformation des données JSON en colonnes DataFrame Spark
    kafka_df = (kafka_df
                .select(pysqlf.from_json(pysqlf.col("value").cast("string"), schema).alias("value"))
                .withColumn("stationCode", pysqlf.col("value.stationCode"))
                .withColumn("station_id", pysqlf.col("value.station_id"))
                .withColumn("stationCode", pysqlf.col("value.stationCode"))
                .withColumn("num_bikes_available", pysqlf.col("value.num_bikes_available"))
                .withColumn("numBikesAvailable", pysqlf.col("value.numBikesAvailable"))
                .withColumn("num_bikes_available_types", pysqlf.col("value.num_bikes_available_types"))
                .withColumn("num_docks_available", pysqlf.col("value.num_docks_available"))
                .withColumn("numDocksAvailable", pysqlf.col("value.numDocksAvailable"))
                .withColumn("is_installed", pysqlf.col("value.is_installed"))
                .withColumn("is_returning", pysqlf.col("value.is_returning"))
                .withColumn("is_renting", pysqlf.col("value.is_renting"))
                .withColumn("last_reported", pysqlf.col("value.last_reported"))
                .withColumn("mechanical ", pysqlf.col("num_bikes_available_types").getItem(0).getItem("mechanical"))
                .withColumn("ebike ", pysqlf.col("num_bikes_available_types").getItem(1).getItem("ebike"))
                )

    # Lecture des informations de station depuis un fichier CSV
    df_station_informations = spark.read.csv("stations_information.csv", header=True)


    # Aggrégation des données par station_id puis jointure avec les informations de station pour ajouter le code postal
    aggregated_kafka_df = (kafka_df
                     .groupBy("station_id")
                     .agg(pysqlf.sum("num_bikes_available").alias("total_bikes_available"),
                          pysqlf.sum("mechanical").alias("total_mechanical"),
                          pysqlf.sum("ebike").alias("total_electric"))
                     )
    
    
    aggregated_kafka_df_postcode = (aggregated_kafka_df
                                   .join(df_station_informations.select("station_id", "postcode"), ["station_id"], "left")
                                   .drop("station_id")
                                   )
    
    # Ajout d'un timestamp 
    aggregated_kafka_df_postcode = aggregated_kafka_df_postcode.withColumn("timestamp", pysqlf.current_timestamp())

   # Dataframe final
    col_selections = ["timestamp", "postcode", "total_bikes_available", "total_mechanical_bikes", "total_electric_bikes"]
    aggregated_kafka_df_postcode = aggregated_kafka_df_postcode.select(*col_selections)
    
   # Envoi du DataFrame final vers un topic Kafka `velib-clean` en mode streaming
    out = (aggregated_kafka_df_postcode
           .writeStream
           .format("kafka")
           .queryName("projet-esme")
           .option("kafka.bootstrap.servers", "localhost:9092")
           .option("topic", "velib-clean")
           .outputMode("complete")
           .option("checkpointLocation", "chk-point-dir")
           .trigger(processingTime="1 second")
           .start()
           )

    out.awaitTermination()