import os
import random
import tkinter as tk
import requests

from datetime import datetime

from PIL import Image, ImageTk


def update_image():
    # Get a list of files in the directory
    photo_dir = './photos'
    files = [os.path.join(photo_dir, f) for f in os.listdir(photo_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not files:
        print("No images found in the directory.")
        return

    # Select a random image file
    selected_image = random.choice(files)
    image = Image.open(selected_image)

    # Calculate the optimal resize ratio to maintain aspect ratio
    screen_ratio = screen_width / screen_height
    image_ratio = image.width / image.height
    if image_ratio > screen_ratio:
        # Image is wider than the screen, scale by width
        scale_factor = screen_width / image.width
    else:
        # Image is taller than the screen, scale by height
        scale_factor = screen_height / image.height

    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    photo = ImageTk.PhotoImage(image)

    # Display the image
    image_label.config(image=photo)
    image_label.image = photo

    image_label.pack(padx=0, pady=0, expand=True)


def update_image_loop():
    update_image()
    root.after(120000, update_image_loop)


def update_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)


def update_weather():
    city = "Denver"
    api_key = "87204bf6c88fe982ed5dc01c861e633c"
    weather_data = fetch_weather(api_key, city)
    if weather_data:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        weather_label.config(text=f"{temperature}°F, {description}")
    # Update weather every 10 minutes
    root.after(600000, update_weather)


def fetch_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city}&units=imperial"
    response = requests.get(complete_url)
    weather_data = response.json()
    if weather_data['cod'] == 200:
        return weather_data
    else:
        return None


def update_calendar():
    # Fetch and display calendar events
    pass


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)


root = tk.Tk()
root.attributes('-fullscreen', True)

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

canvas = tk.Canvas(root, width=200, height=100, bg='grey', highlightthickness=0)
canvas.place(relx=1.0, rely=1.0, anchor='se')

# Set up a label for the image
image_label = tk.Label(root)
image_label.pack()

bg_image = Image.open("bg.png")
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relx=1.0, rely=0, anchor='ne')

canvas = tk.Canvas(root, width=400, height=100, bg='black', highlightthickness=0)
canvas.pack()
# create_rounded_rectangle(canvas, 10, 10, 390, 90, radius=20, fill='#44444480')

time_label = tk.Label(root, text="00:00", font=('Arial', 48), bg='black', fg='white')
time_label.place(relx=1.0, rely=1.0, anchor='se')

weather_label = tk.Label(root, text="25°C, Sunny", font=('Arial', 16), bg='black', fg='white')
weather_label.place(relx=1.0, rely=0, anchor='ne')

update_image_loop()
update_time()
update_weather()

# Start the loop for updating content
root.mainloop()
