import httpx
import os
import logging
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

logger = logging.getLogger("weather_service")
logging.basicConfig(level=logging.INFO)


# ---------------------------
# VALIDATION
# ---------------------------
def _validate_api_key():
    if not API_KEY:
        logger.error("Missing OPENWEATHER_API_KEY in environment")
        raise HTTPException(
            status_code=500,
            detail="Weather API key not configured",
        )


# ---------------------------
# SAFE WEATHER PARSER
# ---------------------------
def _extract_weather(data: dict, rainfall_5day: float = 0.0) -> dict:
    return {
        "city": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "temperature": round(data.get("main", {}).get("temp", 0), 2),
        "humidity": round(data.get("main", {}).get("humidity", 0), 2),

        # real + estimated rainfall
        "rainfall_5day": round(rainfall_5day, 2),
        "rainfall_month_estimate": round((rainfall_5day / 5) * 30, 2),
    }


# ---------------------------
# RAINFALL FROM FORECAST
# ---------------------------
async def _get_5day_rainfall(city: str) -> float:
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(f"{BASE_URL}/forecast", params=params)

    data = res.json()

    if res.status_code != 200:
        raise HTTPException(
            status_code=res.status_code,
            detail=data.get("message", "Forecast API error"),
        )

    total_rain = 0.0

    for item in data.get("list", []):
        rain = item.get("rain", {}).get("3h", 0)
        total_rain += rain

    print(total_rain)

    return total_rain


async def _get_5day_rainfall_by_coords(lat: float, lon: float) -> float:
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(f"{BASE_URL}/forecast", params=params)

    data = res.json()

    if res.status_code != 200:
        logger.error(f"Forecast API error for coords: {data}")
        return 0.0

    total_rain = 0.0
    print("\nExtracted rain values per forecast entry:")
    for item in data.get("list", []):
        rain = float(item.get("rain", {}).get("3h", 0.0))
        if rain > 0:
            print(f"- {item.get('dt_txt', 'Unknown')}: {rain}mm")
        total_rain += rain

    print(f"Final computed rainfall values (5day forecast): {total_rain}")
    return float(total_rain)


# ---------------------------
# CITY WEATHER
# ---------------------------
async def get_weather_by_city(city: str) -> dict:
    _validate_api_key()

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
    }

    try:
        
        print("\n========== CITY WEATHER REQUEST ==========")
        print("CITY:", city)
        print("PARAMS:", params)

        async with httpx.AsyncClient(timeout=10.0) as client:
            weather_res = await client.get(f"{BASE_URL}/weather", params=params)

        weather_data = weather_res.json()

        logger.info("Fetching weather for city: %s", city)
        logger.info("Status: %s", weather_res.status_code)

        if weather_res.status_code != 200:
            raise HTTPException(
                status_code=weather_res.status_code,
                detail=weather_data.get("message", "Weather API error"),
            )

        # 🔥 Get rainfall from forecast
        rainfall_5day = await _get_5day_rainfall(city)

        print(_extract_weather(weather_data, rainfall_5day))

        return _extract_weather(weather_data, rainfall_5day)

    except httpx.RequestError as exc:
        logger.error("Network error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Weather service unreachable",
        )

    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------
# COORDINATES WEATHER
# ---------------------------
async def get_weather_by_coords(lat: float, lon: float) -> dict:
    _validate_api_key()

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
    }

    try:
        print("\n========== COORDS WEATHER REQUEST ==========")
        print("COORDS:", lat, lon)
        print("PARAMS:", params)

        async with httpx.AsyncClient(timeout=10.0) as client:
            weather_res = await client.get(f"{BASE_URL}/weather", params=params)

        weather_data = weather_res.json()
        print("Raw API response summary:", {k: weather_data.get(k) for k in ["name", "sys", "main", "rain"]})

        if weather_res.status_code != 200:
            raise HTTPException(
                status_code=weather_res.status_code,
                detail=weather_data.get("message", "Weather API error"),
            )

        # 1. Location Resolution (Reverse Geocoding fallback if name is empty)
        city_name = weather_data.get("name")
        country = weather_data.get("sys", {}).get("country")
        
        if not city_name or not country:
            geo_params = {"lat": lat, "lon": lon, "limit": 1, "appid": API_KEY}
            async with httpx.AsyncClient(timeout=10.0) as client:
                geo_res = await client.get("https://api.openweathermap.org/geo/1.0/reverse", params=geo_params)
            
            if geo_res.status_code == 200:
                geo_data = geo_res.json()
                if geo_data and isinstance(geo_data, list) and len(geo_data) > 0:
                    weather_data["name"] = geo_data[0].get("name", city_name)
                    if "sys" not in weather_data:
                        weather_data["sys"] = {}
                    weather_data["sys"]["country"] = geo_data[0].get("country", country)

        # 2. Rainfall calculation
        rain_data = weather_data.get("rain", {})
        rain_1h = float(rain_data.get("1h", 0.0))
        rain_3h = float(rain_data.get("3h", 0.0))
        current_rain = rain_1h if rain_1h > 0 else (rain_3h / 3.0)

        rainfall_5day = await _get_5day_rainfall_by_coords(lat, lon)
        
        if rainfall_5day == 0.0 and current_rain > 0:
            print("Extrapolating current rain as forecast returned 0 or no rain.")
            rainfall_5day = current_rain * 24 * 5

        result = _extract_weather(weather_data, rainfall_5day=rainfall_5day)
        print("Final computed rainfall values:", result.get("rainfall_5day"), result.get("rainfall_month_estimate"))
        return result

    except httpx.RequestError as exc:
        logger.error("Network error coords: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Weather service unreachable",
        )

    except Exception as exc:
        logger.error("Unexpected error coords: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )