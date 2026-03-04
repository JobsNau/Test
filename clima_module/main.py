import json
from weather_service import get_weather
from database import init_db, upsert_or_update_clima
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "municipios.json"

with open(file_path, "r", encoding="utf-8") as f:
    data_municipos = json.load(f)
    MUNICIPIOS = data_municipos["municipios"]

def main():
    
    init_db()

    for municipio in MUNICIPIOS:
        clima = get_weather(municipio["lat"], municipio["lon"])

        upsert_or_update_clima(
            municipio["nombre"],
            clima["temperatura"],
            clima["weather_code"],
            clima["weather_description"],
            latitud=clima["latitud"],
            longitud=clima["longitud"],
            fecha=clima["time"]
        )

if __name__ == "__main__":
    main()