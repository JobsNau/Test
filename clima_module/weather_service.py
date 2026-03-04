import requests
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.open-meteo.com/v1/forecast"


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
            "wind_speed": data["current_weather"]["windspeed"],
            "wind_direction": data["current_weather"]["winddirection"],
            "latitud": data["latitude"],
            "longitud": data["longitude"],
            "time": datetime.datetime.fromisoformat(data["current_weather"]["time"]) - datetime.timedelta(hours=5),
        }

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        raise