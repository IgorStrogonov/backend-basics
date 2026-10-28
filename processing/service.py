from clients.weather import get_weather
from clients.rates import get_rate
from processing.preprocessing import *


def build_city_summary(city: str, currency: str = "USD") -> dict:
    weather_data = get_weather(city)
    rate = get_rate(currency)
    warm_clothes = is_warm_clothes_needed(weather_data["temp_c"])
    umbrella = is_umbrella_needed(weather_data["description"])
    expensive = is_rate_expensive(rate)
    cheap = is_rate_cheap(rate)

    return {
        "city": city,
        "weather": {
            "temp_c": weather_data["temp_c"],
            "description": weather_data["description"],
            "warm_clothes": warm_clothes,
            "umbrella": umbrella,
        },
        "rates": {
            "currency": currency.upper(),
            "rate_to_rub": rate,
            "expensive": expensive,
            "cheap": cheap,
        },
    }
