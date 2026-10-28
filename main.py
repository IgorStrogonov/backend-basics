import argparse
import sys
import json

from processing.service import build_city_summary
from clients.weather import CityNotFoundError
from clients.rates import CurrencyNotFoundError
from clients.http import ExternalServiceError


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--city", type=str, required=True)
    parser.add_argument("--currency", type=str, default="USD")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    try:
        summary = build_city_summary(args.city, args.currency)

        if args.json:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            sys.exit(0)
        weather = summary["weather"]
        rates = summary["rates"]
        print(f"Город: {summary['city']}")
        print(f"Погода: {weather['temp_c']}°C, {weather['description']}")

        warm_text = "да" if weather["warm_clothes"] else "нет"
        umbrella_text = "да" if weather.get("umbrella") else "нет"
        expensive_text = "да" if rates["expensive"] else "нет"
        cheap_text = "да" if rates.get("cheap") else "нет"

        print(f"Тёплая одежда: {warm_text}")
        print(f"Зонт: {umbrella_text}")
        print(f"{rates['currency']} → RUB: {rates['rate_to_rub']}")
        print(f"Дорогой курс: {expensive_text}")
        print(f"Дешёвый курс: {cheap_text}")

        sys.exit(0)

    except (CityNotFoundError, CurrencyNotFoundError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(3)

    except ExternalServiceError as e:
        print(f"Ошибка внешнего сервиса: {e}", file=sys.stderr)
        sys.exit(4)

    except Exception as e:
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
