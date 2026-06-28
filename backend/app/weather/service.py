"""
Weather Service — AgriNova AI
Replaces the previous mock/OpenWeather implementation with a production-ready
Open-Meteo integration backed by an in-process 15-minute cache.

Architecture
------------
WeatherService          ← routes.py / AI services call this
  └─ OpenMeteoClient    ← makes the actual HTTP request
  └─ WeatherCache       ← lightweight TTL cache (no Redis dependency)
  └─ WeatherRepository  ← persists weather history to PostgreSQL

The public interface is **unchanged** so all existing callers continue to work.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from app.models.weather import WeatherHistory
from app.weather.repository import WeatherRepository
from app.weather.weather_client import OpenMeteoClient, OpenMeteoError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-process weather cache
# ---------------------------------------------------------------------------
_CACHE_TTL_MINUTES = 15


class _WeatherCache:
    """
    Simple dictionary-backed TTL cache keyed by ``(lat, lon)`` rounded to
    4 decimal places (~11 m precision — good enough for farm-level caching).

    Not thread-safe for concurrent writes, but Flask's development server and
    most WSGI workers share state via process memory which is acceptable here.
    """

    def __init__(self) -> None:
        self._store: dict[tuple[float, float], tuple[dict, datetime]] = {}

    @staticmethod
    def _key(lat: float, lon: float) -> tuple[float, float]:
        return (round(lat, 4), round(lon, 4))

    def get(self, lat: float, lon: float) -> dict | None:
        """Return cached weather or *None* if missing / expired."""
        entry = self._store.get(self._key(lat, lon))
        if entry is None:
            return None
        payload, expires_at = entry
        if datetime.utcnow() > expires_at:
            del self._store[self._key(lat, lon)]
            logger.debug("[WeatherCache] Cache expired for (%.4f, %.4f).", lat, lon)
            return None
        logger.debug("[WeatherCache] Cache hit for (%.4f, %.4f).", lat, lon)
        return payload

    def set(self, lat: float, lon: float, payload: dict) -> None:
        """Store *payload* in the cache with a TTL of ``_CACHE_TTL_MINUTES``."""
        expires_at = datetime.utcnow() + timedelta(minutes=_CACHE_TTL_MINUTES)
        self._store[self._key(lat, lon)] = (payload, expires_at)
        logger.debug("[WeatherCache] Cache stored for (%.4f, %.4f).", lat, lon)


# Module-level singleton — shared across all requests in the same process
_cache = _WeatherCache()
_client = OpenMeteoClient()


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class WeatherService:
    """
    Weather Service
    Fetches live weather from Open-Meteo, caches results for 15 minutes,
    logs history to PostgreSQL, and returns a unified response envelope.

    Public method signature is unchanged from the previous implementation
    so existing callers (routes, AI services) require no modifications.
    """

    @staticmethod
    def get_weather_by_coords(lat: float, lon: float, farm_id: str) -> tuple[dict, int]:
        """
        Return current weather + 7-day forecast for the given coordinates.

        Args:
            lat:     Farm latitude (stored in PostgreSQL ``farms`` table).
            lon:     Farm longitude (stored in PostgreSQL ``farms`` table).
            farm_id: UUID string of the farm — used for DB logging only.

        Returns:
            Tuple of ``(response_dict, http_status_code)``.  The response
            follows AgriNova's standard weather envelope::

                {
                    "success": True,
                    "source": "Open-Meteo API" | "Cache" | "Unavailable",
                    "weather": {
                        "current":  { ... },
                        "forecast": [ {...} × 7 ],
                        "alerts":   [ {...} ],
                        "summary":  { ... },
                    }
                }
        """
        # ── 1. Validate coordinates ────────────────────────────────────────
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "Invalid coordinates: lat/lon must be numeric.",
            }, 400

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return {
                "success": False,
                "message": (
                    f"Coordinates out of range — lat={lat}, lon={lon}. "
                    "Expected lat ∈ [-90,90] and lon ∈ [-180,180]."
                ),
            }, 400

        # ── 2. Check cache ─────────────────────────────────────────────────
        cached = _cache.get(lat, lon)
        if cached is not None:
            WeatherService._log_weather(farm_id, cached["current"])
            return {
                "success": True,
                "source": "Cache",
                "cached": True,
                "weather": cached,
            }, 200

        # ── 3. Call Open-Meteo ─────────────────────────────────────────────
        try:
            weather_info = _client.get_weather(lat, lon)
        except OpenMeteoError as exc:
            logger.error("[WeatherService] Open-Meteo API failure: %s", exc)
            return WeatherService._unavailable_response(), 503
        except ValueError as exc:
            logger.error("[WeatherService] Coordinate validation error: %s", exc)
            return {
                "success": False,
                "message": str(exc),
            }, 400
        except Exception as exc:
            logger.exception("[WeatherService] Unexpected error calling Open-Meteo.")
            return WeatherService._unavailable_response(), 503

        # ── 4. Enrich with weather summary ─────────────────────────────────
        weather_info["summary"] = WeatherService._build_summary(weather_info)

        # ── 5. Store in cache ──────────────────────────────────────────────
        _cache.set(lat, lon, weather_info)

        # ── 6. Persist weather history ─────────────────────────────────────
        WeatherService._log_weather(farm_id, weather_info["current"])

        return {
            "success": True,
            "source": "Open-Meteo API",
            "cached": False,
            "weather": weather_info,
        }, 200

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(weather_info: dict[str, Any]) -> dict[str, Any]:
        """
        Derive a compact summary object for AI modules (crop/disease/yield).

        Returns:
            Dict with fields that downstream AI services can consume directly
            without parsing the full weather response.
        """
        current  = weather_info["current"]
        forecast = weather_info.get("forecast", [])

        # Average rain probability over the 7-day forecast
        rain_probs = [f["rain_probability"] for f in forecast if "rain_probability" in f]
        avg_rain_prob = round(sum(rain_probs) / len(rain_probs), 1) if rain_probs else 0.0

        return {
            # Fields used by CropService, AIService, PredictionService
            "temperature": current["temp"],
            "humidity": current["humidity"],
            "wind_speed": current["wind_speed"],
            "rain_probability": avg_rain_prob,
            "weather_condition": current["weather_condition"],
            "forecast": forecast,
        }

    @staticmethod
    def _log_weather(farm_id: str, current: dict[str, Any]) -> None:
        """
        Persist a weather poll record in ``weather_history``.
        Never raises — database errors are logged and swallowed so the HTTP
        response is never blocked by a logging failure.
        """
        try:
            log = WeatherHistory(
                farm_id=farm_id,
                temperature=current["temp"],
                humidity=current["humidity"],
                wind_speed=current["wind_speed"],
                rain_probability=current.get("rain_probability", 0.0),
                weather_description=current["description"],
            )
            WeatherRepository.save_weather_history(log)
        except Exception as exc:
            WeatherRepository.rollback()
            logger.error(
                "[WeatherService] DB logging failed for farm %s: %s",
                farm_id, exc,
            )

    @staticmethod
    def _unavailable_response() -> dict[str, Any]:
        """
        Return a graceful degradation envelope instead of crashing Flask.
        Frontend receives a ``success: False`` flag so it can display the
        'Weather service temporarily unavailable' message.
        """
        return {
            "success": False,
            "source": "Unavailable",
            "message": (
                "Weather service temporarily unavailable. "
                "Please try again in a few minutes."
            ),
        }
