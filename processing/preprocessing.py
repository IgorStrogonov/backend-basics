def is_warm_clothes_needed(temp_c: float) -> bool:
    return temp_c < 0


def is_umbrella_needed(description: str) -> bool:
    desc = description.lower()
    rain_keywords = ["rain", "drizzle", "thunderstorm"]
    return any(i in desc for i in rain_keywords)


def is_rate_expensive(rate: float, threshold: float = 85.0) -> bool:
    return rate > threshold


def is_rate_cheap(rate: float, threshold: float = 70.0) -> bool:
    return rate < threshold
