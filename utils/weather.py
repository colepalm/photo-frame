"""
OpenWeatherMap current-conditions helper
"""

import requests


_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
_TIMEOUT  = 10  # seconds


def fetch_weather(city_name: str, api_key: str) -> dict:
    """
    Fetch current weather conditions for *city_name* from OpenWeatherMap.

    Returns the parsed JSON dict on success.  Raises on any network or
    API-level error so callers can catch and handle gracefully.

    Parameters
    ----------
    city_name : str
        City name accepted by OWM, e.g. "Denver" or "London,GB".
    api_key : str
        Your OpenWeatherMap API key.

    Returns
    -------
    dict
        Raw OWM response; typical keys include "main", "weather", "wind".

    Raises
    ------
    requests.HTTPError
        If the API returns a non-2xx status (e.g. 401 bad key, 404 city).
    requests.RequestException
        On network timeouts or connection errors.
    ValueError
        If the response body is not valid JSON.
    """
    params = {
        "q":     city_name,
        "appid": api_key,
        "units": "imperial",
    }

    response = requests.get(_BASE_URL, params=params, timeout=_TIMEOUT)
    response.raise_for_status()   # raises HTTPError on 4xx / 5xx

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError(
            f"OWM returned non-JSON response (status {response.status_code})"
        ) from exc