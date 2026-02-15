import os

"""
all site-specific settings for the photo-frame display.

"""

# ---------------------------------------------------------------------------
# Photos
# ---------------------------------------------------------------------------

photos_dir = os.environ.get('PHOTOS_DIR', './photos')


# ---------------------------------------------------------------------------
# Location  (used for sunrise/sunset and moon phase)
# ---------------------------------------------------------------------------

CITY     = "Denver"
REGION   = "Colorado"
TIMEZONE = "America/Denver"
LATITUDE  = 39.7392
LONGITUDE = -104.9903


# ---------------------------------------------------------------------------
# Weather  (OpenWeatherMap)
# ---------------------------------------------------------------------------

WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not WEATHER_API_KEY:
    raise RuntimeError("Please set the OPENWEATHER_API_KEY environment variable")

# City name as OWM expects it; append ",US" or a country code to disambiguate.
WEATHER_CITY = "Denver,US"


# ---------------------------------------------------------------------------
# Google Calendar
# ---------------------------------------------------------------------------

# Path to your OAuth2 credentials file downloaded from Google Cloud Console.
GOOGLE_CREDENTIALS_FILE = "service-account-key.json"

# Calendar IDs to aggregate events from.
calendar_ids = [
    "palm.cole@gmail.com",
    "shannon.melvina@gmail.com",
]


# ---------------------------------------------------------------------------
# Display timings  (all values in milliseconds)
# ---------------------------------------------------------------------------

# How long each photo is displayed before advancing to the next.
PHOTO_INTERVAL_MS = 120 * 1000               # 2 minutes

# How often the forecast overlay pops up automatically.
FORECAST_SHOW_INTERVAL_MS = 30 * 60 * 1000   # every 30 minutes

# How long the forecast overlay stays visible before auto-hiding.
FORECAST_DISPLAY_DURATION_MS = 30 * 1000     # 30 seconds

# How often each data-fetching widget refreshes from its source.
WEATHER_REFRESH_MS  = 10 * 60 * 1000         # 10 minutes
ASTRAL_REFRESH_MS   =  1 * 60 * 60 * 1000    # 1 hour
CALENDAR_REFRESH_MS = 15 * 60 * 1000         # 15 minutes


# ---------------------------------------------------------------------------
# Display resolution
# ---------------------------------------------------------------------------

DISPLAY_WIDTH  = 1920
DISPLAY_HEIGHT = 1080


# ---------------------------------------------------------------------------
# Widget sizing
# ---------------------------------------------------------------------------

MOON_SUN_WIDTH  = 220
MOON_SUN_HEIGHT = 140