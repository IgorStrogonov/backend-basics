from clients.http import get_request, ExternalServiceError


class CurrencyNotFoundError(Exception):
    pass


def get_rate(currency: str) -> float:
    currency = currency.upper()
    url = f"https://api.frankfurter.dev/v2/rate/{currency}/RUB"

    try:
        response = get_request(url)
        if response.status_code == 404:
            raise CurrencyNotFoundError(f"Валюта {currency} не найдена")
        response.raise_for_status()
        data = response.json()
        if "rate" not in data:
            raise ExternalServiceError(f"В ответе API нет ключа 'rate'.")
        rate = data["rate"]
        return float(rate)

    except (CurrencyNotFoundError, ExternalServiceError):
        raise
    except Exception as e:
        raise ExternalServiceError(f"Ошибка обработки данных от API курсов: {e}")
