import random
import logging
import time
import faker as fk
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import unidecode
from google.cloud import pubsub_v1
import json
import os

fake = fk.Faker('es_ES')

class PubSubMessages:
    """ Publish Messages in our PubSub Topic """

    def __init__(self, project_id: str):
        """
        Initialize the PubSubMessages class.

        Params:
            project_id(str): Google Cloud Project ID.
        """
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = project_id
        logging.info("PubSub Client initialized.")

    def publishMessages(self, payload: dict, topic_name: str):
        """
        Publishes the desired message to the specified topic.

        Params:
            payload(dict): Data Payload.
            topic_name(str): Google PubSub Topic Name.
        """
        json_str = json.dumps(payload).encode("utf-8")
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        self.publisher.publish(topic_path, json_str)

    def __exit__(self):
        self.publisher.transport.close()
        logging.info("PubSub Client closed.")


def get_cities():
    '''Lista de cuidades donde se van a generar los datos'''
    return ["valencia", "albal", "paiporta", "alfafar", "catarroja"]


def get_messages_affected():
    '''mensajes de la gente afectada por la dana '''

    messages = [
        ("suministros", "Un refugio temporal requiere productos de higiene personal y desinfectantes.", "productos_limpieza"),
        ("suministros", "Se solicita leche en polvo y panales para bebes en un centro de acogida.", "comida_bebida"),
        ("botas", "He perdido mis botas, dadme unas", "botas"),
        ("limpieza", "Las calles de un barrio estan cubiertas de lodo y se requieren palas para la limpieza.", "palas"),
        ("limpieza", "Un centro comunitario necesita escobas para retirar el barro acumulado en el suelo.", "escobas"),
        ("medicinas", "Un centro de salud necesita medicamentos esenciales para pacientes afectados.", "medicinas"),
        ("transporte", "Se necesita transporte para evacuar personas de areas afectadas.", "transporte"),
        ("refugio", "Familias desplazadas necesitan albergue temporal.", "refugio"),
        ("medicinas", "Necesitamos medicinas genericas para dolor de cabeza", "medicinas")

    ]
    return messages


def get_messages_volunteers():
    '''Mensajes de la gente voluntaria'''

    messages = [
        ("suministros", "Somos un grupo de voluntarios y llevamos comida y agua potable para los afectados.", "comida_bebida"),
        ("capricho", "Quiero pasearme con mi bolso y hacerme una foto con alguien que lo haya perdido todo", "bolso"),
        ("suministros", "Recolectamos ropa seca para distribuirla entre quienes la necesiten.", "ropa"),
        ("suministros", "Llevamos kits de higiene y productos de limpieza a los refugios.", "productos_limpieza"),
        ("suministros", "Tenemos alimentos no perecederos para repartir en zonas afectadas.", "comida_bebida"),
        ("suministros", "Estamos recolectando productos de higiene personal para entregar en los albergues.", "productos_limpieza"),
        ("medicinas", "Disponemos de medicamentos esenciales para entregar en centros de salud.", "medicinas"),
        ("transporte", "Tenemos vehiculos disponibles para ayudar en la evacuacion de personas.", "transporte"),
        ("refugio", "Ofrecemos alojamiento temporal para familias desplazadas.", "refugio")
    ]
    return messages


def generate_phone_number():
    ''' Generamos numeros de teléfono aleatorios'''

    return f'+34-{random.randint(600000000, 699999999)}'


def disponibility_options():
    '''Dod tipos de disponibilidades para ir a ayudar o para solicitar ayuda solo una franja horaria'''

    options = ('morning', 'afternoon')
    return random.choice(options)


def normalize_names(name):
    '''Normalizar los nombres para que salgan sin errores'''
    return unidecode.unidecode(name)


def get_city_coordinates():
    """
    Obtiene las coordenadas (latitud y longitud) de una lista predefinida de ciudades.
    """
    cities_list = get_cities()
    geolocator = Nominatim(user_agent="geoapi", timeout=10)
    city_coordinates = {}

    for city in cities_list:
        attempts = 3
        for attempt in range(attempts):
            try:
                location = geolocator.geocode(city, timeout=10)
                if location:
                    city_coordinates[city] = {"latitude": location.latitude, "longitude": location.longitude}
                else:
                    logging.warning(f"No se encontraron coordenadas para {city}. Se usará (0.0, 0.0).")
                    city_coordinates[city] = {"latitude": 0.0, "longitude": 0.0}
                break
            except GeocoderTimedOut:
                logging.warning(f"Tiempo de espera agotado para {city}. Reintentando... ({attempt+1}/{attempts})")
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error obteniendo coordenadas de {city}: {e}")
                city_coordinates[city] = {"latitude": 0.0, "longitude": 0.0}
                break

    return city_coordinates, cities_list


def generate_affected_messages(affected_id, timestamp_af, city, city_data, radius=0.005):
    messages = get_messages_affected()
    fake = fk.Faker('es_ES')
    name = normalize_names(fake.name())
    phone = generate_phone_number()

    category, message, necessity = random.choice(messages)
    lat = city_data['latitude'] + random.uniform(-radius, radius)
    lon = city_data['longitude'] + random.uniform(-radius, radius)
    disponibility = disponibility_options()

    return {
        "affected_id": affected_id,
        "timestamp": timestamp_af.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "name": name,
        "phone": phone,
        "category": category,
        "message": message,
        "necessity": necessity,
        "city": city,
        'disponibility': disponibility,
        "latitude": lat,
        "longitude": lon,
        'processed': 0
    }


def generate_volunteer_messages(volunteer_id, timestamp_vol, city_vol):
    messages = get_messages_volunteers()
    fake = fk.Faker('es_ES')
    name = normalize_names(fake.name())
    phone = generate_phone_number()
    category, message, necessity = random.choice(messages)

    disponibility = disponibility_options()

    return {
        "volunteer_id": volunteer_id,
        "timestamp": timestamp_vol.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "name": name,
        "phone": phone,
        "category": category,
        "message": message,
        "necessity": necessity,
        "city": city_vol,
        'disponibility': disponibility,
        'processed': 0
    }


def run_streaming(project_id: str, affected_topic: str, volunteer_topic: str):
    pubsub_class = PubSubMessages(project_id=project_id)

    # Generamos listas grandes de IDs
    affected_ids = [f"affected_{str(i).zfill(5)}" for i in range(10000, 9999999)]
    volunteer_ids = [f"volunteer_{str(i).zfill(5)}" for i in range(10000, 9999999)]

    # Timers iniciales para cada ID
    timestamps_af = {affected_id: datetime.now() for affected_id in affected_ids}
    timestamps_vol = {volunteer_id: datetime.now() for volunteer_id in volunteer_ids}

    city_coordinates, cities_list = get_city_coordinates()

    try:
        while True:
            affected_id = random.choice(affected_ids)
            volunteer_id = random.choice(volunteer_ids)

            selected_city = random.choice(cities_list)
            selected_city_vol = random.choice(cities_list)

            city_data = city_coordinates.get(selected_city, {"latitude": 0.0, "longitude": 0.0})

            event = generate_affected_messages(affected_id, timestamps_af[affected_id], selected_city, city_data)
            event_vol = generate_volunteer_messages(volunteer_id, timestamps_vol[volunteer_id], selected_city_vol)

            pubsub_class.publishMessages(payload=event, topic_name=affected_topic)
            pubsub_class.publishMessages(payload=event_vol, topic_name=volunteer_topic)

            logging.info(f"Published message for {affected_id} to {affected_topic}")
            logging.info(f"Published message for {volunteer_id} to {volunteer_topic}")

            # Actualizamos timestamp
            timestamps_af[affected_id] += timedelta(seconds=random.randint(1, 60))
            timestamps_vol[volunteer_id] += timedelta(seconds=random.randint(1, 60))

            # Pausa de 1 segundo entre publicaciones
            time.sleep(5)

    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Probando obtención de coordenadas...")
    city_coordinates, cities_list = get_city_coordinates()
    for city, coords in city_coordinates.items():
        print(f"{city}: {coords}")

    project_id = os.environ.get("PROJECT_ID")
    affected_topic = os.environ.get("AFFECTED_TOPIC")
    volunteer_topic = os.environ.get("VOLUNTEER_TOPIC")

    logging.info("Starting streaming data generator")
    run_streaming(project_id, affected_topic, volunteer_topic)
    logging.info("Streaming data generator finished")