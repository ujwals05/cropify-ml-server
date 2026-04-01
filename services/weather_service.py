import httpx
import os
import logging
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def _validate_api_key() -> None:
    """Raise immediately if the API key is missing or empty."""
    if not API_KEY:
        logger.error("OPENWEATHER_API_KEY is not configured in .env")
        raise HTTPException(
            status_code=500,
            detail="Weather API key not configured. Set OPENWEATHER_API_KEY in .env",
        )


def _extract_weather(data: dict) -> dict:
    """Safely extract weather fields — never crashes on missing keys."""
    return {
        "city": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "temperature": round(data.get("main", {}).get("temp", 0), 2),
        "humidity": round(data.get("main", {}).get("humidity", 0), 2),
        "rainfall": round(data.get("rain", {}).get("1h", 0) * 24, 2),
    }


async def get_weather_by_city(city: str) -> dict:
    _validate_api_key()

    params = {"q": city, "appid": API_KEY, "units": "metric"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/weather", params=params)

        logger.debug("API KEY status: %s", "SET" if API_KEY else "MISSING")
        logger.debug("STATUS: %s", response.status_code)
        logger.debug("RESPONSE: %s", response.text)

        data = response.json()

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=data.get("message", "Weather API error"),
            )

        return _extract_weather(data)

    except HTTPException:
        # Re-raise our own HTTP errors untouched
        raise

    except httpx.RequestError as exc:
        logger.error("Network error fetching weather for city '%s': %s", city, exc)
        raise HTTPException(
            status_code=503,
            detail=f"Weather service unreachable: {exc}",
        )

    except Exception as exc:
        logger.error("Unexpected error fetching weather for city '%s': %s", city, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}",
        )


async def get_weather_by_coords(lat: float, lon: float) -> dict:
    _validate_api_key()

    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/weather", params=params)

        logger.debug("API KEY status: %s", "SET" if API_KEY else "MISSING")
        logger.debug("STATUS: %s", response.status_code)
        logger.debug("RESPONSE: %s", response.text)

        data = response.json()

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=data.get("message", "Weather API error"),
            )

        return _extract_weather(data)

    except HTTPException:
        raise

    except httpx.RequestError as exc:
        logger.error(
            "Network error fetching weather for coords (%s, %s): %s", lat, lon, exc
        )
        raise HTTPException(
            status_code=503,
            detail=f"Weather service unreachable: {exc}",
        )

    except Exception as exc:
        logger.error(
            "Unexpected error fetching weather for coords (%s, %s): %s",
            lat,
            lon,
            exc,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}",
        )