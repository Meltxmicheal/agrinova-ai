"""
Open-Meteo Weather Client
Production-ready HTTP client for the Open-Meteo free forecast API.

Endpoint : https://api.open-meteo.com/v1/forecast
Auth     : None (no API key required)
Docs     : https://open-meteo.com/en/docs
"""

import logging
import requests
from typing import Any

from app.weather.weather_codes import get_weather_info

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BASE_URL = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT = 8          # seconds per attempt
_MAX_RETRIES = 1      # retry once before raising

_CURRENT_VARS = ",".join([
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "rain",
    "precipitation",
    "windspeed_10m",
    "winddirection_10m",
    "surface_pressure",
    "weathercode",
])

_DAILY_VARS = ",".join([
    "temperature_2m_max",
    "temperature_2m_min",
    "weathercode",
    "precipitation_probability_max",
    "precipitation_sum",
])


class OpenMeteoError(Exception):
    """Raised when the Open-Meteo API cannot be reached or returns bad data."""


class OpenMeteoClient:
    """
    Thin HTTP client for the Open-Meteo forecast API.

    Usage::

        client = OpenMeteoClient()
        data   = client.get_weather(latitude=13.08, longitude=77.59)

    The returned dict follows AgriNova's internal weather schema so that
    :class:`WeatherService` can consume it directly.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_weather(self, latitude: float, longitude: float) -> dict[str, Any]:
        """
        Fetch current conditions and 7-day forecast from Open-Meteo.

        Args:
            latitude:  Farm latitude (-90 to 90).
            longitude: Farm longitude (-180 to 180).

        Returns:
            Standardised weather dict::

                {
                    "current": { ... },
                    "forecast": [ {...}, ... ],   # 7 entries
                    "alerts": [ {...} ],
                }

        Raises:
            OpenMeteoError: When the API cannot be reached after retries or
                            returns unexpected data.
            ValueError: When coordinates are out of valid range.
        """
        self._validate_coordinates(latitude, longitude)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": _CURRENT_VARS,
            "daily": _DAILY_VARS,
            "timezone": "auto",
            "forecast_days": 7,
        }

        raw = self._request(params)
        return self._parse(raw)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_coordinates(lat: float, lon: float) -> None:
        """Raise *ValueError* for coordinates outside the valid geographic range."""
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat!r} is out of range [-90, 90].")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon!r} is out of range [-180, 180].")

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Perform the HTTP GET with one automatic retry on failure.

        Returns:
            Parsed JSON response body.

        Raises:
            OpenMeteoError: On network failure, timeout, or non-200 HTTP status.
        """
        attempts = 0
        last_exc: Exception | None = None

        while attempts <= _MAX_RETRIES:
            try:
                resp = requests.get(_BASE_URL, params=params, timeout=_TIMEOUT)
                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.Timeout as exc:
                last_exc = exc
                logger.warning(
                    "[OpenMeteoClient] Request timed out (attempt %d/%d).",
                    attempts + 1, _MAX_RETRIES + 1,
                )

            except requests.exceptions.ConnectionError as exc:
                last_exc = exc
                logger.warning(
                    "[OpenMeteoClient] Connection error (attempt %d/%d): %s",
                    attempts + 1, _MAX_RETRIES + 1, exc,
                )

            except requests.exceptions.HTTPError as exc:
                # Non-2xx responses are not worth retrying (bad params etc.)
                raise OpenMeteoError(
                    f"Open-Meteo returned HTTP {exc.response.status_code}: {exc.response.text}"
                ) from exc

            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "[OpenMeteoClient] Unexpected error (attempt %d/%d): %s",
                    attempts + 1, _MAX_RETRIES + 1, exc,
                )

            attempts += 1

        raise OpenMeteoError(
            "Open-Meteo API unreachable after retries."
        ) from last_exc

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse(self, raw: dict[str, Any]) -> dict[str, Any]:
        """
        Convert the raw Open-Meteo JSON into AgriNova's internal schema.

        Args:
            raw: Full JSON response from the API.

        Returns:
            Dict with ``current``, ``forecast``, and ``alerts`` keys.
        """
        current = self._parse_current(raw)
        forecast = self._parse_forecast(raw)
        alerts = self._build_alerts(current)

        return {
            "current": current,
            "forecast": forecast,
            "alerts": alerts,
        }

    @staticmethod
    def _parse_current(raw: dict[str, Any]) -> dict[str, Any]:
        """Extract and normalise the ``current`` block."""
        c: dict[str, Any] = raw.get("current", {})

        code: int = int(c.get("weathercode", 0))
        code_info = get_weather_info(code)

        # rain field from Open-Meteo is mm in last hour; >0 means currently raining
        rain_mm: float = float(c.get("rain", 0.0) or 0.0)

        return {
            # Core fields consumed by the existing frontend
            "temp": round(float(c.get("temperature_2m", 0.0)), 1),
            "humidity": round(float(c.get("relative_humidity_2m", 0.0)), 1),
            "apparent_temp": round(float(c.get("apparent_temperature", 0.0)), 1),
            "wind_speed": round(float(c.get("windspeed_10m", 0.0)), 1),
            "wind_direction": int(c.get("winddirection_10m", 0)),
            "surface_pressure": round(float(c.get("surface_pressure", 0.0)), 1),
            "rain": round(rain_mm, 2),
            "precipitation": round(float(c.get("precipitation", 0.0) or 0.0), 2),
            "weather_code": code,
            "description": code_info["description"],
            "icon": code_info["icon"],
            "severity": code_info["severity"],
            # Derived: treat non-zero rain as 100 % probability, else 0
            # (intraday probability is not a current variable in Open-Meteo)
            "rain_probability": 100.0 if rain_mm > 0 else 0.0,
            # AI-ready fields
            "weather_condition": code_info["description"],
        }

    @staticmethod
    def _parse_forecast(raw: dict[str, Any]) -> list[dict[str, Any]]:
        """Build the 7-day forecast list from the ``daily`` block."""
        daily: dict[str, list] = raw.get("daily", {})

        dates        = daily.get("time", [])
        max_temps    = daily.get("temperature_2m_max", [])
        min_temps    = daily.get("temperature_2m_min", [])
        codes        = daily.get("weathercode", [])
        rain_probs   = daily.get("precipitation_probability_max", [])
        precip_sums  = daily.get("precipitation_sum", [])

        forecast: list[dict[str, Any]] = []
        for i, date in enumerate(dates[:7]):
            code     = int(codes[i]) if i < len(codes) else 0
            code_info = get_weather_info(code)
            rain_prob = float(rain_probs[i]) if i < len(rain_probs) and rain_probs[i] is not None else 0.0

            forecast.append({
                "date": date,
                "temp_day": round(float(max_temps[i]), 1) if i < len(max_temps) else 0.0,
                "temp_night": round(float(min_temps[i]), 1) if i < len(min_temps) else 0.0,
                "rain_probability": round(rain_prob, 1),
                "precipitation_sum": round(float(precip_sums[i]), 2) if i < len(precip_sums) and precip_sums[i] is not None else 0.0,
                "weather_code": code,
                "description": code_info["description"],
                "icon": code_info["icon"],
                "severity": code_info["severity"],
            })

        return forecast

    @staticmethod
    def _build_alerts(current: dict[str, Any]) -> list[dict[str, str]]:
        """
        Derive agronomic weather alerts from current conditions.
        These mirror the alerts the existing mock engine produced.
        """
        alerts: list[dict[str, str]] = []
        temp       = current["temp"]
        wind_speed = current["wind_speed"]
        severity   = current["severity"]
        rain_mm    = current["rain"]

        if temp > 40:
            alerts.append({
                "type": "heat_wave",
                "message": "Extreme heat alert. Irrigate crops regularly and avoid midday fieldwork.",
            })
        elif temp < 5:
            alerts.append({
                "type": "frost",
                "message": "Frost warning. Cover sensitive seedlings and protect irrigation lines.",
            })

        if wind_speed > 15:
            alerts.append({
                "type": "high_winds",
                "message": "High winds detected. High risk of crop lodging in tall crops.",
            })

        if severity == "storm":
            alerts.append({
                "type": "thunderstorm",
                "message": "Thunderstorm forecast. Postpone spraying operations and protect farm equipment.",
            })
        elif rain_mm > 10:
            alerts.append({
                "type": "heavy_rain",
                "message": "Heavy rainfall recorded. Ensure farm drainage is functioning to prevent waterlogging.",
            })

        return alerts
