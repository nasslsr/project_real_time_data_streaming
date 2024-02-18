import json  # Importe le module json pour la sérialisation et la désérialisation des données JSON
import time  # Importe le module time pour gérer les pauses entre les appels API
import requests  # Importe le module requests pour effectuer des requêtes HTTP
from kafka import KafkaProducer  # Importe KafkaProducer de la bibliothèque kafka pour envoyer des données à Kafka

# To do: Créer via l'invite de command un topic velib-projet
# To do: Envoyer les données vers un topic velib-projet
# To do: Il faut filtrer les données collectées pour ne prendre que les données des deux stations suivantes: 16107, 32017

def get_velib_data():
    """
    Fonction pour obtenir les données des stations Velib à partir de l'API Velib Metropole.
    :return: liste des informations filtrées des stations
    """
    # Effectue une requête GET pour récupérer les données des stations depuis l'API Velib Metropole
    response = requests.get('https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json')
    data = json.loads(response.text)  # Convertit la réponse en texte en un dictionnaire Python

    # Filtre les données pour obtenir uniquement celles des stations 16107 et 32017
    stations = data["data"]["stations"]
    stations_filtered = [station for station in stations if station['stationCode'] in ['16107', '32017']]

    return stations_filtered  # Retourne la liste filtrée des stations

def velib_producer():
    """
    Fonction pour créer un producteur Kafka et envoyer les données filtrées des stations Velib à un topic Kafka.
    """
    # Crée un objet producteur Kafka configuré pour se connecter à un serveur Kafka local et sérialiser les messages en JSON
    producer = KafkaProducer(bootstrap_servers="localhost:9092",
                             value_serializer=lambda x: json.dumps(x).encode('utf-8')
                             )

    while True:  # Boucle infinie pour envoyer des données périodiquement
        data = get_velib_data()  # Récupère les données filtrées des stations Velib
        for message in data:  # Pour chaque station dans les données filtrées
            producer.send("velib-projet", message)  # Envoie la donnée de la station au topic Kafka
            print("added:", message)  # Affiche un message de confirmation dans la console
        time.sleep(1)  # Attend 1 seconde avant de répéter le processus

if __name__ == '__main__':
    velib_producer()  # Exécute la fonction principale si le script est exécuté directement
