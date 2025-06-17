import os
import requests
import datetime

from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase as moon_phase

from config import photos_dir


def load_photos():
    files = [os.path.join(photos_dir, f) for f in os.listdir(photos_dir) if
             f.lower().endswith(('.png', '.jpg', '.jpeg', '.heic'))]
    return files


def fetch_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_calendar_events(service, max_results=1):
    import datetime
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    calendar_ids = [
        'palm.cole@gmail.com',
    ]

    all_events = []

    for calendar_id in calendar_ids:
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            all_events.extend(events)

        except Exception as e:
            print(f"Error fetching from {calendar_id}: {e}")

    all_events.sort(key=lambda x: x.get('start', {}).get('dateTime', x.get('start', {}).get('date', '')))

    return all_events[:max_results]

def list_calendars(service):
    """Get all calendars accessible to the service account"""
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])
    return calendars

def fetch_astral_data(city_name, region_name, timezone_name, latitude, longitude):
    """Returns today's sunrise, sunset, and moon phase for the given location."""
    location = LocationInfo(city_name, region_name, timezone_name, latitude, longitude)
    today = datetime.date.today()

    sun_data = sun(location.observer, date=today, tzinfo=location.timezone)
    sunrise = sun_data["sunrise"]
    sunset = sun_data["sunset"]

    moon_phase_number = moon_phase(date=today)
    phase_name = interpret_moon_phase(moon_phase_number)

    return sunrise, sunset, phase_name

def interpret_moon_phase(phase_number):
    """Convert the numeric moon phase to a rough name."""
    if phase_number < 1:
        return "New Moon"
    elif phase_number < 7:
        return "Waxing Crescent"
    elif phase_number == 7:
        return "First Quarter"
    elif phase_number < 14:
        return "Waxing Gibbous"
    elif phase_number == 14:
        return "Full Moon"
    elif phase_number < 21:
        return "Waning Gibbous"
    elif phase_number == 21:
        return "Last Quarter"
    else:
        return "Waning Crescent"
