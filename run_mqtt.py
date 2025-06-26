import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
import time
from datetime import datetime

# Broker MQTT
broker = "test.mosquitto.org"
port = 1883
topics = ["IUT/Colmar2025/SAE2.04/Maison1", "IUT/Colmar2025/SAE2.04/Maison2"]

# Connexion MySQL (VM Debian)
mysql_host = '10.252.9.132'
mysql_database = 'pj_integratif'
mysql_user = 'root'
mysql_password = 'darklucas'

# Connexion à la base de données
try:
    connection = mysql.connector.connect(
        host=mysql_host,
        database=mysql_database,
        user=mysql_user,
        password=mysql_password
    )
    if connection.is_connected():
        cursor = connection.cursor()
        print("Connecté à la base de données MySQL")

except Error as e:
    print(f"Erreur de connexion : {e}")
    exit()

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connecté avec le code {rc}")
    for topic in topics:
        client.subscribe(topic)
        print(f"Abonné à {topic}")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message reçu : {message} sur le topic {msg.topic}")

    try:
        # Extraction de la température
        temp_part = message.split("temp=")[1]
        temp_value = temp_part.split(',')[0] if ',' in temp_part else temp_part
        temp_value = float(temp_value.replace(',', '.'))

        message_without_temp = message.replace(f",temp={temp_part}", "")
        data = dict(item.split("=") for item in message_without_temp.split(","))

        data['temp'] = temp_value

        required_keys = {'Id', 'piece', 'date', 'heure'}
        if not required_keys.issubset(data.keys()):
            required_keys = {'Id', 'piece', 'date', 'time'}
            if not required_keys.issubset(data.keys()):
                raise ValueError(f"Clés manquantes dans le message : {data}")

        sensor_id = data['Id']
        piece = data['piece']
        date = data['date']
        heure = data.get('time', data.get('heure'))
        temp = data['temp']

        date_heure = datetime.strptime(f"{date} {heure}", "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

        # Vérification de l'existence du capteur (id_capteur)
        cursor.execute("SELECT id_capteur FROM capteurs WHERE id_capteur = %s", (sensor_id,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute(
                "INSERT INTO capteurs (id_capteur, nom_capteur, piece) VALUES (%s, %s, %s)",
                (sensor_id, sensor_id, piece)
            )
            connection.commit()
            print(f"Capteur {sensor_id} inséré dans la table capteur.")

        # Insertion dans la table mesures
        cursor.execute(
            "INSERT INTO mesures (id_capteur, date_heure, temperature) VALUES (%s, %s, %s)",
            (sensor_id, date_heure, temp)
        )
        connection.commit()
        print("Mesure insérée avec succès.")

    except Exception as e:
        print(f"Erreur lors du traitement du message : {e}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port, 60)

    client.loop_start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        client.loop_stop()
        print("Arrêt du programme...")

if __name__ == "__main__":
    main()

    # Fermeture de la connexion MySQL
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connexion MySQL fermée")
