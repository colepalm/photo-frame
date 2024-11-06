import os
import requests


def load_photos(photos_dir):
    files = [os.path.join(photos_dir, f) for f in os.listdir(photos_dir) if
             f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return files


def fetch_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = response.json()
    return data


def fetch_calendar_events(service, max_results=10):
    import datetime
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=max_results, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events
