import requests
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_MAP = {
    0: "Cielo despejado",
    1: "Principalmente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    66: "Lluvia helada ligera",
    67: "Lluvia helada intensa",
    71: "Nieve ligera",
    73: "Nieve moderada",
    75: "Nieve fuerte",
    77: "Granizo",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos violentos",
    85: "Nevadas ligeras",
    86: "Nevadas intensas",
    95: "Tormenta",
    96: "Tormenta con granizo leve",
    99: "Tormenta con granizo fuerte"
}


def create_session():
    retry_strategy = Retry(
        total=5,                       # Máximo 5 intentos
        backoff_factor=1,              # Espera exponencial: 1s, 2s, 4s, 8s...
        status_forcelist=[429, 500, 502, 503, 504],  # Errores reintentables
        allowed_methods=["GET"],       # Solo GET
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "User-Agent": "clima-module/1.0"
    })

    return session

def get_weather_description(weather_code: int) -> str:
    """
    Retorna la descripción en texto del weather_code WMO.
    """
    return WEATHER_CODE_MAP.get(weather_code, "Estado del clima desconocido")


def get_weather(lat, lon):
    session = create_session()

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
    }

    try:
        response = session.get(BASE_URL, params=params, timeout=15)

        # Si después de retries sigue mal
        if response.status_code != 200:
            raise Exception(f"Error API: {response.status_code} - {response.text}")

        data = response.json()

        print(f"Datos recibidos: {data}")

        return {
            "temperatura": data["current_weather"]["temperature"],
            "weather_code": data["current_weather"]["weathercode"],
            "weather_description": get_weather_description(data["current_weather"]["weathercode"]),
            "wind_speed": data["current_weather"]["windspeed"],
            "wind_direction": data["current_weather"]["winddirection"],
            "latitud": data["latitude"],
            "longitud": data["longitude"],
            "time": datetime.datetime.fromisoformat(data["current_weather"]["time"]) - datetime.timedelta(hours=5),
        }

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        raise