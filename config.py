import os

api_key = os.getenv('OPENWEATHER_API_KEY')
if not api_key:
    raise RuntimeError("Please set the OPENWEATHER_API_KEY environment variable")

photos_dir = './photos'
city_name = 'Denver'