# project_real_time_data_streaming

Introduction

Ce projet a pour but de collecter, traiter et analyser en temps réel les données de disponibilité des vélos en libre-service (Velib) à Paris, en utilisant Apache Kafka pour la gestion des flux de données et Apache Spark pour l'analyse en temps réel. Le projet se décompose en deux grandes parties : la collecte et l'envoi des données vers un topic Kafka, puis le traitement de ces données avec Spark pour en extraire des statistiques significatives.

Prérequis

Pour exécuter ce projet, vous devez avoir installé sur votre machine :

- Apache Kafka (avec Zookeeper)
- Apache Spark
- Python 3.x avec les bibliothèques requests, kafka-python, pyspark, et findspark.
- Assurez-vous également que Java est installé, car Kafka et Spark en dépendent.

Configuration Initiale de Kafka

Avant de lancer les scripts Python, vous devez démarrer Zookeeper et Kafka et créer les topics nécessaires. Voici les commandes pour démarrer Zookeeper et Kafka :

Démarrer Zookeeper :
./kafka_2.12-2.6.0/bin/zookeeper-server-start.sh ./kafka_2.12-2.6.0/config/zookeeper.properties

Démarrer le serveur Kafka :
./kafka_2.12-2.6.0/bin/kafka-server-start.sh ./kafka_2.12-2.6.0/config/server.properties

Créer les topics Kafka :
Pour le projet, vous aurez besoin de créer deux topics : un pour les données brutes (velib-projet) et un autre pour les données nettoyées et agrégées (velib-projet-clean). Voici comment créer le premier topic :
./kafka_2.12-2.6.0/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic velib-projet

Répétez la commande pour le deuxième topic en changeant le nom du topic en velib-projet-clean.

Partie 1 : Collecte et envoi des données Vers Kafka

Le premier script Python (producer.py) collecte les données de disponibilité des vélos depuis l'API Velib et les envoie vers le topic Kafka velib-projet. Ce script filtre les données pour ne prendre en compte que les stations spécifiées et les publie en format JSON.

Exécution du script de collecte

il faut s'assurer que Kafka et Zookeeper sont en fonctionnement, puis exécutez le script :
python producer.py

Ce script tourne en continu, envoyant des données mises à jour à intervalles réguliers.

Partie 2 : Traitement des données avec Spark

Le second script Python (consumer.py) utilise Apache Spark pour lire les données du topic velib-projet, les traite pour calculer le nombre total de vélos disponibles par code postal, et envoie le résultat vers le topic velib-projet-clean.

Configuration de Spark
Il faut s'assurer que Spark est correctement configuré avec les variables d'environnement nécessaires (SPARK_HOME et JAVA_HOME). Il faut également ajouter le package Kafka pour Spark à votre configuration SparkSession dans le script.

Exécution du Script de Traitement
Avec Kafka, Zookeeper, et le producteur de données en fonctionnement, lancez le script de traitement :
python consumer.py

Ce script lit en continu les données du topic velib-projet, effectue les agrégations nécessaires et publie les résultats agrégés dans le topic velib-projet-clean.
