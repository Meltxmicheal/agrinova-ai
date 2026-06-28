"""
Weather Codes — Open-Meteo WMO Code Mapping
Converts numeric WMO weather codes to human-readable descriptions and icon names.

WMO Weather Interpretation Codes (WW):
https://open-meteo.com/en/docs#weathervariables
"""

from typing import TypedDict


class WeatherCodeInfo(TypedDict):
    description: str
    icon: str
    severity: str  # "clear" | "cloudy" | "rain" | "snow" | "storm" | "fog"


# Full mapping of WMO weather interpretation codes
WEATHER_CODE_MAP: dict[int, WeatherCodeInfo] = {
    0:  {"description": "Clear Sky",          "icon": "sun",              "severity": "clear"},
    1:  {"description": "Mainly Clear",        "icon": "sun",              "severity": "clear"},
    2:  {"description": "Partly Cloudy",       "icon": "cloud-sun",        "severity": "cloudy"},
    3:  {"description": "Overcast",            "icon": "clouds",           "severity": "cloudy"},
    45: {"description": "Fog",                 "icon": "fog",              "severity": "fog"},
    48: {"description": "Rime Fog",            "icon": "fog",              "severity": "fog"},
    51: {"description": "Light Drizzle",       "icon": "cloud-drizzle",    "severity": "rain"},
    53: {"description": "Moderate Drizzle",    "icon": "cloud-drizzle",    "severity": "rain"},
    55: {"description": "Dense Drizzle",       "icon": "cloud-drizzle",    "severity": "rain"},
    56: {"description": "Freezing Drizzle",    "icon": "cloud-snow",       "severity": "snow"},
    57: {"description": "Heavy Freezing Drizzle", "icon": "cloud-snow",    "severity": "snow"},
    61: {"description": "Slight Rain",         "icon": "cloud-rain",       "severity": "rain"},
    63: {"description": "Moderate Rain",       "icon": "cloud-rain",       "severity": "rain"},
    65: {"description": "Heavy Rain",          "icon": "cloud-showers-heavy", "severity": "rain"},
    66: {"description": "Freezing Rain",       "icon": "cloud-snow",       "severity": "snow"},
    67: {"description": "Heavy Freezing Rain", "icon": "cloud-snow",       "severity": "snow"},
    71: {"description": "Slight Snow",         "icon": "snowflake",        "severity": "snow"},
    73: {"description": "Moderate Snow",       "icon": "snowflake",        "severity": "snow"},
    75: {"description": "Heavy Snow",          "icon": "snowflake",        "severity": "snow"},
    77: {"description": "Snow Grains",         "icon": "snowflake",        "severity": "snow"},
    80: {"description": "Slight Rain Showers", "icon": "cloud-sun-rain",   "severity": "rain"},
    81: {"description": "Moderate Rain Showers", "icon": "cloud-rain",    "severity": "rain"},
    82: {"description": "Violent Rain Showers", "icon": "cloud-showers-heavy", "severity": "rain"},
    85: {"description": "Slight Snow Showers", "icon": "cloud-snow",      "severity": "snow"},
    86: {"description": "Heavy Snow Showers",  "icon": "cloud-snow",       "severity": "snow"},
    95: {"description": "Thunderstorm",        "icon": "cloud-lightning",  "severity": "storm"},
    96: {"description": "Thunderstorm w/ Slight Hail", "icon": "cloud-lightning", "severity": "storm"},
    99: {"description": "Thunderstorm w/ Heavy Hail",  "icon": "cloud-lightning", "severity": "storm"},
}

_UNKNOWN: WeatherCodeInfo = {
    "description": "Unknown Conditions",
    "icon": "cloud-question",
    "severity": "cloudy",
}


def get_weather_info(code: int) -> WeatherCodeInfo:
    """
    Return description, icon name, and severity for a WMO weather code.

    Args:
        code: WMO weather interpretation code from Open-Meteo response.

    Returns:
        WeatherCodeInfo dict with ``description``, ``icon``, and ``severity`` keys.
    """
    return WEATHER_CODE_MAP.get(code, _UNKNOWN)


def get_description(code: int) -> str:
    """Return only the human-readable description for a WMO code."""
    return get_weather_info(code)["description"]


def get_icon(code: int) -> str:
    """Return only the icon name for a WMO code."""
    return get_weather_info(code)["icon"]


def get_severity(code: int) -> str:
    """Return only the severity level for a WMO code."""
    return get_weather_info(code)["severity"]
