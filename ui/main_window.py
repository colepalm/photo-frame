import random

from PIL import Image, ExifTags
from PIL.ImageQt import ImageQt

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget

from config import api_key, city_name
from ui.calendar_module import CalendarWidget
from ui.moon_sun_widget import MoonSunWidget
from ui.time_module import TimeWidget
from ui.weather_module import WeatherWidget
from utils import load_photos


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pixmap = None
        self.setWindowTitle("Digital Photo Frame")

        self.initial_setup_done = False  # Flag to ensure setup is done before handling resize events

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")

        self.image_label = QLabel(central_widget)
        self.image_label.setGeometry(0, 0, self.width(), self.height())
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.weather_widget = WeatherWidget(central_widget, api_key, city_name)
        self.weather_widget.setGeometry(self.width() - 300, 20, 280, 60)

        self.time_widget = TimeWidget(central_widget)
        self.time_widget.setGeometry(650, self.height() - 100, 200, 100)

        self.calendar_widget = CalendarWidget(central_widget)

        self.moon_sun_widget = MoonSunWidget(
            city="Denver",
            region="USA",
            timezone="America/Denver",
            lat=39.7872326,
            lon=-104.9973032,
            parent=central_widget
        )

        self.photos_list = load_photos()
        random.shuffle(self.photos_list)
        self.current_photo = 0

        self.timer = QTimer(self)
        self.start_image_loop()

        self.update_image()
        self.update_positions()  # Update positions based on the full screen size

        self.initial_setup_done = True  # Mark the setup as complete
        self.showFullScreen()

    @staticmethod
    def get_exif_orientation(image_path):
        """Get the EXIF orientation value from an image."""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        if ExifTags.TAGS.get(tag) == 'Orientation':
                            return value
        except Exception as e:
            print(f"Error reading EXIF data from {image_path}: {e}")
        return 1  # Default orientation (no rotation needed)

    @staticmethod
    def apply_exif_rotation(image, orientation):
        """Apply rotation based on EXIF orientation value."""
        rotation_map = {
            1: 0,  # Normal
            2: 0,  # Mirrored horizontally
            3: 180,  # Rotated 180°
            4: 180,  # Mirrored vertically
            5: 90,  # Mirrored horizontally and rotated 90° CCW
            6: 270,  # Rotated 90° CW
            7: 270,  # Mirrored horizontally and rotated 90° CW
            8: 90,  # Rotated 90° CCW
        }

        rotation = rotation_map.get(orientation, 0)
        if rotation != 0:
            image = image.rotate(-rotation, expand=True)

        # Handle mirroring for orientations 2, 4, 5, 7
        if orientation in [2, 4, 5, 7]:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        return image

    def load_and_process_image(self, image_path):
        """Load an image and apply EXIF orientation correction."""
        try:
            # Get orientation from EXIF
            orientation = self.get_exif_orientation(image_path)

            # Load image with PIL
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (handles RGBA, P, etc.)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Apply EXIF rotation
                img = self.apply_exif_rotation(img, orientation)

                # Convert PIL image to QPixmap
                qt_image = ImageQt(img)
                pixmap = QPixmap.fromImage(qt_image)

                return pixmap

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            # Fallback to original method
            return QPixmap(image_path)

    @staticmethod
    def get_best_fit_scaling(image_size, container_size):
        """Calculate the best scaling to fit image in container while maintaining aspect ratio."""
        img_width, img_height = image_size
        container_width, container_height = container_size

        # Calculate scaling factors for both dimensions
        scale_x = container_width / img_width
        scale_y = container_height / img_height

        # Use the smaller scale to ensure the image fits completely
        scale = min(scale_x, scale_y)

        return scale

    def resizeEvent(self, event):
        """Handle the resize event to update widget positions."""
        if self.initial_setup_done:
            print("Resizing window")
            self.update_positions()
            # Update the current image to fit the new size
            self.update_current_image_size()
        super().resizeEvent(event)

    def update_current_image_size(self):
        """Update the current image to fit the new window size."""
        if hasattr(self, 'current_pixmap') and self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def update_positions(self):
        """ Update positions of labels based on the current size of the window """
        screen_size = self.size()
        self.image_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
        weather_widget_width = 220
        self.weather_widget.setGeometry(
            screen_size.width() - weather_widget_width - 20,
            20,
            weather_widget_width,
            50
        )

        time_widget_height = 60
        time_widget_width = 200
        self.time_widget.setGeometry(
            screen_size.width() - time_widget_width - 20,
            screen_size.height() - time_widget_height - 20,
            time_widget_width,
            time_widget_height
        )

        calendar_widget_width = 200
        calendar_widget_height = 90
        self.calendar_widget.setGeometry(
            20,
            screen_size.height() - calendar_widget_height - 20,
            calendar_widget_width,
            calendar_widget_height
        )

        moon_sun_width = 200
        moon_sun_height = 60
        self.moon_sun_widget.setGeometry(
            20,
            20,
            moon_sun_width,
            moon_sun_height
        )

    def update_image(self):
        """Update the image displayed on the label."""
        if not self.photos_list:
            print("No images found in the directory.")
            return

        photo_path = self.photos_list[self.current_photo]
        print(f"Loading image: {photo_path}")

        # Load and process the image with EXIF orientation correction
        pixmap = self.load_and_process_image(photo_path)

        # Store the original pixmap for resizing
        self.current_pixmap = pixmap

        # Scale the image to fit the label
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.current_photo = (self.current_photo + 1) % len(self.photos_list)

    def start_image_loop(self):
        """Change the photo at intervals."""
        self.timer.timeout.connect(self.update_image)
        self.timer.start(120000)  # Change image every 120 seconds