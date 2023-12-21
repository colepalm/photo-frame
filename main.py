import os
import random
import tkinter as tk

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

    # Load the selected image using PIL
    image = Image.open(selected_image)
    image = image.resize((800, 600), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    # Display the image
    image_label.config(image=photo)
    image_label.image = photo


def update_image_loop():
    update_image()
    # Set the timer (e.g., 120 seconds)
    root.after(120000, update_image_loop)


def update_time():
    # Update and display the current time
    pass


def update_weather():
    # Fetch and display the current weather
    pass


def update_calendar():
    # Fetch and display calendar events
    pass


# Set up the main window using Tkinter
root = tk.Tk()
root.attributes('-fullscreen', True)

# Set up a label for the image
image_label = tk.Label(root)
image_label.pack()

update_image_loop()

# Start the loop for updating content
root.mainloop()
