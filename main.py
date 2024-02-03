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

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set up a label for the image
image_label = tk.Label(root)
image_label.pack()

update_image_loop()

# Start the loop for updating content
root.mainloop()
