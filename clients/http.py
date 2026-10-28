import requests
import time
import random


class ExternalServiceError(Exception):
    pass


def get_request(
    url: str, params: dict = None, headers: dict = None
) -> requests.Response:
    attempts = 3
    timeout = (3, 10)

    for i in range(1, attempts + 1):
        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=timeout
            )
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-after")
                if retry_after and retry_after.isdigit():
                    delay = int(retry_after)
                else:
                    delay = 2 ** (i - 1) + random.uniform(0, 0.5)
                if i == attempts:
                    raise ExternalServiceError(
                        f"Превышен лимит запросов (429) после {attempts} попыток"
                    )
                time.sleep(delay)
                continue
            if response.status_code in (500, 502, 503, 504):
                if i == attempts:
                    response.raise_for_status()
                delay = 2 ** (i - 1) + random.uniform(0, 0.5)
                time.sleep(delay)
                continue
            return response

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if i == attempts:
                raise ExternalServiceError(
                    f"Сервис недоступен после {attempts} попыток: {e}"
                )
            delay = 2 ** (i - 1) + random.uniform(0, 0.5)
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Ошибка при запросе: {e}")
