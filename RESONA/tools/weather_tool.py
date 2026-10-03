"""
RESONA - Weather Intelligence Tool

Provides optional weather information for emergency-response
analysis.

The tool uses Open-Meteo because it does not require an API key
for standard non-commercial usage.

If external weather information is unavailable, the tool
returns a structured error instead of breaking the workflow.
"""

from typing import Any, Dict, Optional

import requests


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

DEFAULT_TIMEOUT_SECONDS = 10


class WeatherToolError(Exception):
    """Raised when weather information cannot be retrieved."""


# ============================================================
# LOCATION
# ============================================================

def geocode_location(
    location: str,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Convert a human-readable location into latitude and longitude.
    """

    if not location or not location.strip():
        raise WeatherToolError(
            "Location cannot be empty."
        )

    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": location.strip(),
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=timeout,
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as exc:
        raise WeatherToolError(
            f"Weather location service unavailable: {exc}"
        ) from exc

    except ValueError as exc:
        raise WeatherToolError(
            "Weather location service returned invalid data."
        ) from exc

    results = data.get(
        "results",
        [],
    )

    if not results:
        raise WeatherToolError(
            f"Could not locate: {location}"
        )

    result = results[0]

    return {
        "name": result.get(
            "name",
            location,
        ),
        "latitude": result.get(
            "latitude"
        ),
        "longitude": result.get(
            "longitude"
        ),
        "country": result.get(
            "country",
            "",
        ),
        "admin1": result.get(
            "admin1",
            "",
        ),
        "timezone": result.get(
            "timezone",
            "",
        ),
    }


# ============================================================
# WEATHER
# ============================================================

def get_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 3,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Retrieve current and forecast weather information.
    """

    forecast_days = min(
        max(int(forecast_days), 1),
        7,
    )

    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "rain,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "hourly": (
                    "temperature_2m,"
                    "precipitation_probability,"
                    "precipitation,"
                    "rain,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "forecast_days": forecast_days,
                "timezone": "auto",
            },
            timeout=timeout,
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as exc:
        raise WeatherToolError(
            f"Weather service unavailable: {exc}"
        ) from exc

    except ValueError as exc:
        raise WeatherToolError(
            "Weather service returned invalid data."
        ) from exc

    current = data.get(
        "current",
        {}
    )

    hourly = data.get(
        "hourly",
        {}
    )

    return {
        "latitude": data.get(
            "latitude",
            latitude,
        ),
        "longitude": data.get(
            "longitude",
            longitude,
        ),
        "timezone": data.get(
            "timezone",
            "",
        ),
        "current": current,
        "hourly": hourly,
        "forecast_days": forecast_days,
    }


# ============================================================
# LOCATION + WEATHER
# ============================================================

def get_weather_for_location(
    location: str,
    forecast_days: int = 3,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Geocode a location and retrieve weather information.

    Returns a structured success/error response so callers
    can safely continue when external data is unavailable.
    """

    try:
        coordinates = geocode_location(
            location=location,
            timeout=timeout,
        )

        weather = get_weather(
            latitude=float(
                coordinates["latitude"]
            ),
            longitude=float(
                coordinates["longitude"]
            ),
            forecast_days=forecast_days,
            timeout=timeout,
        )

        return {
            "success": True,
            "location": coordinates,
            "weather": weather,
            "error": None,
        }

    except WeatherToolError as exc:

        return {
            "success": False,
            "location": {
                "query": location,
            },
            "weather": None,
            "error": str(exc),
        }

    except (
        TypeError,
        ValueError,
        KeyError,
    ) as exc:

        return {
            "success": False,
            "location": {
                "query": location,
            },
            "weather": None,
            "error": (
                "Weather data could not be processed: "
                f"{exc}"
            ),
        }


# ============================================================
# WEATHER INTERPRETATION
# ============================================================

def build_weather_context(
    weather_result: Dict[str, Any],
) -> str:
    """
    Convert weather data into concise contextual text.

    This function does not make emergency decisions. It only
    presents available weather observations in a readable form.
    """

    if not weather_result.get(
        "success",
        False,
    ):
        return (
            "Weather information is unavailable. "
            "No weather-based assumption should be made."
        )

    location = weather_result.get(
        "location",
        {}
    )

    weather = weather_result.get(
        "weather",
        {}
    )

    current = weather.get(
        "current",
        {}
    )

    location_name = location.get(
        "name",
        location.get(
            "query",
            "Unknown location",
        ),
    )

    lines = [
        f"Weather location: {location_name}",
    ]

    country = location.get(
        "country"
    )

    if country:
        lines.append(
            f"Country: {country}"
        )

    temperature = current.get(
        "temperature_2m"
    )

    if temperature is not None:
        lines.append(
            f"Current temperature: {temperature} °C"
        )

    apparent_temperature = current.get(
        "apparent_temperature"
    )

    if apparent_temperature is not None:
        lines.append(
            "Feels-like temperature: "
            f"{apparent_temperature} °C"
        )

    humidity = current.get(
        "relative_humidity_2m"
    )

    if humidity is not None:
        lines.append(
            f"Relative humidity: {humidity}%"
        )

    precipitation = current.get(
        "precipitation"
    )

    if precipitation is not None:
        lines.append(
            f"Current precipitation: {precipitation} mm"
        )

    rain = current.get(
        "rain"
    )

    if rain is not None:
        lines.append(
            f"Current rain: {rain} mm"
        )

    wind = current.get(
        "wind_speed_10m"
    )

    if wind is not None:
        lines.append(
            f"Wind speed: {wind} km/h"
        )

    weather_code = current.get(
        "weather_code"
    )

    if weather_code is not None:
        lines.append(
            f"Weather code: {weather_code}"
        )

    lines.append(
        "Weather observations are contextual information "
        "and should be evaluated alongside verified "
        "emergency reports."
    )

    return "\n".join(lines)


# ============================================================
# TOOL REGISTRY
# ============================================================

def get_weather_tools() -> Dict[str, callable]:
    """
    Return weather functions in a simple registry.
    """

    return {
        "geocode_location": geocode_location,
        "get_weather": get_weather,
        "get_weather_for_location": (
            get_weather_for_location
        ),
        "build_weather_context": (
            build_weather_context
        ),
    }
