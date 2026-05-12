import aiohttp
from config import settings

STATUS_NAMES = {
    "new": "Нова",
    "processing": "В роботі",
    "done": "Виконано",
    "rejected": "Відхилено"
}

async def get_weather(city: str) -> str:
    if not settings.weather_api_key:
        return "API-ключ погоди не налаштовано. Додайте WEATHER_API_KEY у файл .env."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": settings.weather_api_key,
        "units": "metric",
        "lang": "ua"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                return "Не вдалося отримати погоду. Перевірте назву міста."
            data = await response.json()

    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    wind = data["wind"]["speed"]
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"]

    return (
        f"🌤 Погода у місті {city}:\n"
        f"🌡 Температура: {temp} °C\n"
        f"🤗 Відчувається як: {feels_like} °C\n"
        f"🌬 Вітер: {wind} м/с\n"
        f"💧 Вологість: {humidity}%\n"
        f"📝 Опис: {description}\n"
    )
