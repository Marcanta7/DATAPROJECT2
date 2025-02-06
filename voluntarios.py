import random
import uuid
import json
import argparse
from faker import Faker
from google.cloud import pubsub_v1

fake = Faker("es_ES") 

# Argumentos desde la línea de comandos
def get_args():
    parser = argparse.ArgumentParser(description="Generador de datos aleatorios de voluntarios para Pub/Sub")
    parser.add_argument("--project_id", type=str, required=True, help="ID del proyecto de Google Cloud")
    parser.add_argument("--topic_name", type=str, required=True, help="Nombre del tópico de Pub/Sub")
    parser.add_argument("--num_voluntarios", type=int, default=10, help="Número de voluntarios a generar")
    return parser.parse_args() 


# Tipos de ayuda disponibles
TIPOS_AYUDA = [
    "Primeros auxilios", "Limpieza", "Maquinaria pesada", "Transporte",
    "Cuidado de personas", "Suministros", "Alimentación", "Asistencia psicológica"
]


MUNICIPIOS_COORDENADAS = {
    "Alaquàs": (39.4553, -0.4613),
    "Albal": (39.3925, -0.4186),
    "Albalat de la Ribera": (39.2333, -0.3667),
    "Alborache": (39.3833, -0.7833),
    "Alcàsser": (39.3667, -0.45),
    "l'Alcúdia": (39.1833, -0.5167),
    "Aldaia": (39.4667, -0.4667),
    "Alfafar": (39.4167, -0.4),
    "Alfarb": (39.3, -0.6),
    "Algemesí": (39.1833, -0.4333),
    "Alginet": (39.25, -0.4667),
    "Almussafes": (39.2833, -0.4167),
    "Alzira": (39.15, -0.4333),
    "Benetússer": (39.4167, -0.3833),
    "Benicull de Xúquer": (39.2, -0.4),
    "Benifaió": (39.2833, -0.4333),
    "Beniparrell": (39.3667, -0.4167),
    "Bétera": (39.5833, -0.45),
    "Bugarra": (39.6167, -0.8333),
    "Buñol": (39.4167, -0.75),
    "Calles": (39.7, -1.0833),
    "Camporrobles": (39.65, -1.45),
    "Carcaixent": (39.1167, -0.45),
    "Carlet": (39.2333, -0.5167),
    "Castelló": (39.1667, -0.5833),
    "Catadau": (39.3, -0.5667),
    "Catarroja": (39.4, -0.4),
    "Caudete de las Fuentes": (39.5667, -1.3),
    "Chera": (39.6167, -0.9833),
    "Cheste": (39.5, -0.6833),
    "Chiva": (39.4833, -0.7),
    "Chulilla": (39.65, -0.8833),
    "Corbera": (39.2, -0.3667),
    "Cullera": (39.1667, -0.25),
    "Dos Aguas": (39.3, -0.7667),
    "Favara": (39.1167, -0.2833),
    "Fortaleny": (39.1833, -0.3333),
    "Fuenterrobles": (39.5667, -1.3833),
    "Gestalgar": (39.6167, -0.8167),
    "Godelleta": (39.45, -0.7),
    "Guadassuar": (39.2, -0.45),
    "l'Ènova": (39.0667, -0.4667),
    "Llaurí": (39.2, -0.3333),
    "Llombai": (39.3, -0.6),
    "Llíria": (39.6333, -0.6),
    "Llocnou de la Corona": (39.4167, -0.3833),
    "Loriguilla": (39.5667, -0.6167),
    "Macastre": (39.4, -0.8),
    "Manuel": (39.05, -0.5),
    "Manises": (39.4833, -0.4667),
    "Massanassa": (39.4, -0.4),
    "Millares": (39.2, -0.8333),
    "Mislata": (39.4833, -0.4167),
    "Montroi/Montroy": (39.3667, -0.6333),
    "Montserrat": (39.3667, -0.6167),
    "Paiporta": (39.4333, -0.4167),
    "Paterna": (39.5, -0.4333),
    "Pedralba": (39.6, -0.7167),
    "Picanya": (39.45, -0.4167),
    "Picassent": (39.3667, -0.45),
    "Polinyà de Xúquer": (39.2, -0.4),
    "La Pobla Llarga": (39.0667, -0.5),
    "Quart de Poblet": (39.4833, -0.45),
    "Rafelguaraf": (39.05, -0.5),
    "Real": (39.3667, -0.6167),
    "Requena": (39.4833, -1.2),
    "Riba-roja de Túria": (39.55, -0.5667),
    "Riola": (39.2, -0.35),
    "Sedaví": (39.4167, -0.3833),
    "Senyera": (39.05, -0.5),
    "Siete Aguas": (39.5, -0.9333),
    "Silla": (39.3667, -0.4167),
    "Sinarcas": (39.75, -1.3),
    "Sollana": (39.3, -0.3833),
    "Sot de Chera": (39.65, -0.9333),
    "Sueca": (39.2, -0.3167),
    "Tavernes de la Valldigna": (39.0667, -0.2667),
    "Torrent": (39.4333, -0.4667),
    "Tous": (39.1167, -0.5667),
    "Turís": (39.4, -0.7),
    "Utiel": (39.5667, -1.2),
    "València": (39.4667, -0.375),
    "Vilamarxant": (39.5667, -0.6167),
    "Xirivella": (39.4667, -0.4333),
    "Yátova": (39.4, -0.8333)
    }

# Generar coordenadas aleatorias cercanas al centro de un municipio
def generar_coordenadas():
    municipio = random.choice(list(MUNICIPIOS_COORDENADAS.keys()))
    lat_centro, lon_centro = MUNICIPIOS_COORDENADAS[municipio]
    latitud = round(lat_centro + random.uniform(-0.01, 0.01), 6)
    longitud = round(lon_centro + random.uniform(-0.01, 0.01), 6)
    return municipio, latitud, longitud

# Generar un voluntario aleatorio
def generar_voluntario():
    municipio, latitud, longitud = generar_coordenadas()
    return {
        "id": str(uuid.uuid4()),
        "nombre": fake.name(),
        "edad": random.randint(18, 65),
        "telefono": f"6{random.randint(10000000, 99999999)}",
        "municipio": municipio,
        "ubicacion": {"latitud": latitud, "longitud": longitud},
        "habilidades": random.sample(TIPOS_AYUDA, random.randint(1, 3)),
        "disponibilidad": {
            "mañana": random.choice([True, False]),
            "tarde": random.choice([True, False]),
            "noche": random.choice([True, False])
        }
    }

# Publicar voluntario en Pub/Sub
def publicar_voluntario(publisher, topic_path, voluntario):
    data = json.dumps(voluntario).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"Voluntario publicado en Pub/Sub: {voluntario['id']}")
    return future.result()

# Generar y enviar varios voluntarios a Pub/Sub
def enviar_voluntarios_pubsub(project_id, topic_name, num_voluntarios):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    for _ in range(num_voluntarios):
        voluntario = generar_voluntario()
        publicar_voluntario(publisher, topic_path, voluntario)

# Ejecutar el script con los argumentos
if __name__ == "__main__":
    args = get_args()
    enviar_voluntarios_pubsub(args.project_id, args.topic_name, args.num_voluntarios)
