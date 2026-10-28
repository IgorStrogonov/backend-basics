from clients.http import get_request, ExternalServiceError
from typing import Dict, Any, Tuple


class CityNotFoundError(Exception):
    pass


WEATHER_CODES: Dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    95: "thunderstorm",
}


def get_coordinates(city: str) -> Tuple[float, float]:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru"}

    try:
        response = get_request(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "results" not in data or not data["results"]:
            raise CityNotFoundError(f"Город '{city}' не найден")
        location = data["results"][0]
        return location["latitude"], location["longitude"]

    except (CityNotFoundError, ExternalServiceError):
        raise

    except Exception as e:
        raise ExternalServiceError(f"Ошибка обработки данных геокодинга: {e}")


def get_weather(city: str) -> Dict[str, Any]:
    lat, lon = get_coordinates(city)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": "true"}

    try:
        response = get_request(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "current_weather" not in data:
            raise ExternalServiceError("В ответе API нет 'current_weather'")
        current = data["current_weather"]
        temp = current.get("temperature")
        if temp is None:
            raise ExternalServiceError("Отсутствует temperature")
        code = current.get("weathercode")
        if code is None:
            raise ExternalServiceError("Отсутствует weathercode")
        return {
            "temp_c": float(temp),
            "description": WEATHER_CODES.get(code, "unknown conditions"),
        }

    except ExternalServiceError:
        raise

    except Exception as e:
        raise ExternalServiceError(f"Ошибка обработки данных погоды: {e}")
