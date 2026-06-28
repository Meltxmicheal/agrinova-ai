"""
Tests for the Open-Meteo weather integration.

Covers
------
1. Farm without coordinates -> 400 response
2. Invalid coordinates (out of range) -> 400 response
3. API timeout / connection error -> 503 graceful degradation
4. Successful weather fetch -> 200 + correct structure
5. Cache hit -> returns cached payload without hitting the API
6. Cache miss -> calls the API and stores result in cache

Run with::

    cd backend
    ..\.venv\Scripts\python.exe -m unittest tests.test_weather -v
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure backend/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_open_meteo_response() -> dict:
    """Return a minimal valid Open-Meteo API JSON payload."""
    return {
        "latitude": 13.0827,
        "longitude": 77.5877,
        "timezone": "Asia/Kolkata",
        "current": {
            "temperature_2m": 28.5,
            "relative_humidity_2m": 65.0,
            "apparent_temperature": 32.1,
            "rain": 0.0,
            "precipitation": 0.0,
            "windspeed_10m": 12.4,
            "winddirection_10m": 180,
            "surface_pressure": 1010.2,
            "weathercode": 1,
        },
        "daily": {
            "time": [
                "2026-06-28", "2026-06-29", "2026-06-30",
                "2026-07-01", "2026-07-02", "2026-07-03", "2026-07-04",
            ],
            "temperature_2m_max": [31, 30, 29, 32, 33, 28, 27],
            "temperature_2m_min": [22, 21, 20, 23, 24, 19, 18],
            "weathercode": [1, 2, 3, 61, 61, 80, 0],
            "precipitation_probability_max": [5, 20, 40, 70, 80, 60, 10],
            "precipitation_sum": [0, 0.5, 2.1, 8.3, 12.0, 5.5, 0],
        },
    }


# ---------------------------------------------------------------------------
# Unit tests for OpenMeteoClient
# ---------------------------------------------------------------------------

class TestOpenMeteoClient(unittest.TestCase):
    """Unit tests for the HTTP client layer."""

    def setUp(self):
        from app.weather.weather_client import OpenMeteoClient
        self.client = OpenMeteoClient()

    # -- Coordinate validation --

    def test_invalid_latitude_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.client.get_weather(latitude=95.0, longitude=77.5)

    def test_invalid_longitude_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.client.get_weather(latitude=13.0, longitude=200.0)

    def test_negative_out_of_range_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.client.get_weather(latitude=-91.0, longitude=0.0)

    # -- Successful parse --

    @patch("app.weather.weather_client.requests.get")
    def test_successful_fetch_returns_expected_keys(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = _make_open_meteo_response()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = self.client.get_weather(13.08, 77.59)

        self.assertIn("current", result)
        self.assertIn("forecast", result)
        self.assertIn("alerts", result)

    @patch("app.weather.weather_client.requests.get")
    def test_current_block_has_required_fields(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = _make_open_meteo_response()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = self.client.get_weather(13.08, 77.59)
        current = result["current"]

        required = [
            "temp", "humidity", "apparent_temp", "wind_speed",
            "wind_direction", "surface_pressure", "rain", "precipitation",
            "weather_code", "description", "icon", "severity",
            "rain_probability", "weather_condition",
        ]
        for field in required:
            self.assertIn(field, current, msg=f"Missing field: {field}")

    @patch("app.weather.weather_client.requests.get")
    def test_forecast_has_seven_entries(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = _make_open_meteo_response()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        result = self.client.get_weather(13.08, 77.59)
        self.assertEqual(len(result["forecast"]), 7)

    # -- API timeout handling --

    @patch("app.weather.weather_client.requests.get")
    def test_timeout_raises_open_meteo_error_after_retries(self, mock_get):
        import requests as req_lib
        from app.weather.weather_client import OpenMeteoError
        mock_get.side_effect = req_lib.exceptions.Timeout("timed out")

        with self.assertRaises(OpenMeteoError):
            self.client.get_weather(13.08, 77.59)

    @patch("app.weather.weather_client.requests.get")
    def test_connection_error_raises_open_meteo_error(self, mock_get):
        import requests as req_lib
        from app.weather.weather_client import OpenMeteoError
        mock_get.side_effect = req_lib.exceptions.ConnectionError("no route")

        with self.assertRaises(OpenMeteoError):
            self.client.get_weather(13.08, 77.59)


# ---------------------------------------------------------------------------
# Unit tests for WeatherService (service layer + cache)
# ---------------------------------------------------------------------------

class TestWeatherService(unittest.TestCase):
    """Unit tests for WeatherService -- mocks both the client and DB."""

    def _make_weather_info(self) -> dict:
        """Build minimal weather_info dict as returned by OpenMeteoClient."""
        return {
            "current": {
                "temp": 28.5,
                "humidity": 65.0,
                "apparent_temp": 32.1,
                "wind_speed": 12.4,
                "wind_direction": 180,
                "surface_pressure": 1010.2,
                "rain": 0.0,
                "precipitation": 0.0,
                "weather_code": 1,
                "description": "Mainly Clear",
                "icon": "sun",
                "severity": "clear",
                "rain_probability": 0.0,
                "weather_condition": "Mainly Clear",
            },
            "forecast": [
                {
                    "date": f"2026-07-0{i+1}",
                    "temp_day": 30.0, "temp_night": 22.0,
                    "rain_probability": float(i * 10),
                    "precipitation_sum": 0.0,
                    "weather_code": 1,
                    "description": "Mainly Clear",
                    "icon": "sun",
                    "severity": "clear",
                }
                for i in range(7)
            ],
            "alerts": [],
        }

    def setUp(self):
        """Clear the module-level cache before each test."""
        import app.weather.service as svc_module
        svc_module._cache._store.clear()

    # -- Farm without coordinates --

    def test_farm_without_coordinates_returns_400(self):
        from app.weather.service import WeatherService
        response, code = WeatherService.get_weather_by_coords(
            lat=None, lon=None, farm_id="farm-001"
        )
        self.assertEqual(code, 400)
        self.assertFalse(response["success"])

    # -- Invalid coordinates --

    def test_invalid_lat_returns_400(self):
        from app.weather.service import WeatherService
        response, code = WeatherService.get_weather_by_coords(
            lat=999.0, lon=77.0, farm_id="farm-001"
        )
        self.assertEqual(code, 400)
        self.assertFalse(response["success"])

    def test_invalid_lon_returns_400(self):
        from app.weather.service import WeatherService
        response, code = WeatherService.get_weather_by_coords(
            lat=13.0, lon=-999.0, farm_id="farm-001"
        )
        self.assertEqual(code, 400)
        self.assertFalse(response["success"])

    # -- API timeout -> graceful degradation --

    @patch("app.weather.service.WeatherRepository.save_weather_history")
    @patch("app.weather.service._client")
    def test_api_timeout_returns_503_without_crash(self, mock_client, _mock_save):
        from app.weather.weather_client import OpenMeteoError
        from app.weather.service import WeatherService
        mock_client.get_weather.side_effect = OpenMeteoError("timeout")

        response, code = WeatherService.get_weather_by_coords(
            lat=13.08, lon=77.59, farm_id="farm-001"
        )
        self.assertEqual(code, 503)
        self.assertFalse(response["success"])
        self.assertIn("temporarily unavailable", response["message"].lower())

    # -- Successful fetch --

    @patch("app.weather.service.WeatherRepository.save_weather_history")
    @patch("app.weather.service._client")
    def test_successful_fetch_returns_200(self, mock_client, _mock_save):
        from app.weather.service import WeatherService
        mock_client.get_weather.return_value = self._make_weather_info()

        response, code = WeatherService.get_weather_by_coords(
            lat=13.08, lon=77.59, farm_id="farm-001"
        )
        self.assertEqual(code, 200)
        self.assertTrue(response["success"])
        self.assertEqual(response["source"], "Open-Meteo API")
        self.assertFalse(response["cached"])
        self.assertIn("weather", response)

    @patch("app.weather.service.WeatherRepository.save_weather_history")
    @patch("app.weather.service._client")
    def test_successful_response_contains_summary(self, mock_client, _mock_save):
        from app.weather.service import WeatherService
        mock_client.get_weather.return_value = self._make_weather_info()

        response, _ = WeatherService.get_weather_by_coords(
            lat=13.08, lon=77.59, farm_id="farm-001"
        )
        summary = response["weather"]["summary"]
        self.assertIn("temperature", summary)
        self.assertIn("humidity", summary)
        self.assertIn("wind_speed", summary)
        self.assertIn("rain_probability", summary)
        self.assertIn("weather_condition", summary)
        self.assertIn("forecast", summary)

    # -- Cache hit / miss --

    @patch("app.weather.service.WeatherRepository.save_weather_history")
    @patch("app.weather.service._client")
    def test_cache_miss_calls_api_once(self, mock_client, _mock_save):
        from app.weather.service import WeatherService
        mock_client.get_weather.return_value = self._make_weather_info()

        WeatherService.get_weather_by_coords(lat=13.08, lon=77.59, farm_id="farm-001")
        mock_client.get_weather.assert_called_once()

    @patch("app.weather.service.WeatherRepository.save_weather_history")
    @patch("app.weather.service._client")
    def test_cache_hit_skips_api(self, mock_client, _mock_save):
        from app.weather.service import WeatherService
        mock_client.get_weather.return_value = self._make_weather_info()

        # First call -- cache miss, hits API
        WeatherService.get_weather_by_coords(lat=13.08, lon=77.59, farm_id="farm-001")
        # Second call -- should be served from cache
        response, code = WeatherService.get_weather_by_coords(
            lat=13.08, lon=77.59, farm_id="farm-001"
        )

        # API should have been called only once (first call)
        mock_client.get_weather.assert_called_once()
        self.assertEqual(code, 200)
        self.assertTrue(response["cached"])
        self.assertEqual(response["source"], "Cache")


# ---------------------------------------------------------------------------
# Weather code mapping tests
# ---------------------------------------------------------------------------

class TestWeatherCodes(unittest.TestCase):
    """Spot-check key WMO code mappings."""

    def test_code_0_is_clear_sky(self):
        from app.weather.weather_codes import get_description
        self.assertEqual(get_description(0), "Clear Sky")

    def test_code_95_is_thunderstorm(self):
        from app.weather.weather_codes import get_description
        self.assertEqual(get_description(95), "Thunderstorm")

    def test_code_61_is_slight_rain(self):
        from app.weather.weather_codes import get_description
        self.assertIn("Rain", get_description(61))

    def test_unknown_code_returns_fallback(self):
        from app.weather.weather_codes import get_description
        self.assertEqual(get_description(9999), "Unknown Conditions")

    def test_icon_returned_for_known_code(self):
        from app.weather.weather_codes import get_icon
        self.assertNotEqual(get_icon(3), "")

    def test_severity_for_storm_code(self):
        from app.weather.weather_codes import get_severity
        self.assertEqual(get_severity(95), "storm")


if __name__ == "__main__":
    unittest.main(verbosity=2)
