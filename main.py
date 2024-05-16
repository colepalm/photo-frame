import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt, QDateTime


class PhotoFrameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")
        self.showFullScreen()

        # Central widget to hold the image
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")

        # Image label setup
        self.image_label = QLabel(central_widget)
        self.image_label.setGeometry(0, 0, self.width(), self.height())
        self.image_label.setScaledContents(True)

        # Weather label at the top right
        self.weather_label = QLabel("Loading weather...", self.image_label)
        self.weather_label.setFont(QFont('Arial', 16))
        self.weather_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.weather_label.setGeometry(self.width() - 220, 20, 200, 40)

        # TODO: Requery weather periodically
        # self.weatherUpdateTimer = QTimer(self)
        # self.weatherUpdateTimer.timeout.connect(self.update_weather)
        # self.weatherUpdateTimer.start(600000)  # 10 minutes in milliseconds

        # Time label at the bottom right
        self.time_label = QLabel("00:00", self.image_label)
        self.time_label.setFont(QFont('Arial', 24))
        self.time_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setGeometry(650, self.height() - 100, 200, 100)

        self.photos_dir = './photos'
        self.photos_list = self.load_photos()
        self.current_photo = 0

        self.timer = QTimer(self)
        self.start_image_loop()

        self.update_image()
        self.update_time()  # Initial time and date update
        QTimer.singleShot(1000, self.update_time_loop)  # Update time every second

        self.update_positions()  # Update positions based on the full screen size

    def resizeEvent(self, event):
        """Handle the resize event to update widget positions."""
        if hasattr(self, 'image_label') and hasattr(self, 'weather_label') and hasattr(self, 'time_label'):
            self.update_positions()
        super().resizeEvent(event)

    def update_positions(self):
        """ Update positions of labels based on the current size of the window """
        screen_size = self.size()
        screen_size = self.size()
        self.image_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
        self.weather_label.move(screen_size.width() - self.weather_label.width() - 20, 20)
        self.time_label.setGeometry(screen_size.width() - 300 - 20, screen_size.height() - 50 - 20, 300, 50)

    def load_photos(self):
        """Load the paths of photos in the directory."""
        files = [os.path.join(self.photos_dir, f) for f in os.listdir(self.photos_dir) if
                 f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return files

    def update_image(self):
        """Update the image displayed on the label."""
        if not self.photos_list:
            print("No images found in the directory.")
            return

        photo_path = self.photos_list[self.current_photo]
        pixmap = QPixmap(photo_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.current_photo = (self.current_photo + 1) % len(self.photos_list)

    def start_image_loop(self):
        """Change the photo at intervals."""
        self.timer.timeout.connect(self.update_image)
        self.timer.start(120000)  # Change image every 120 seconds

    def update_time_loop(self):
        self.update_time()
        QTimer.singleShot(1000, self.update_time_loop)

    def update_time(self):
        """Update time and date."""
        now = QDateTime.currentDateTime()
        formatted_time = now.toString("hh:mm:ss")
        formatted_date = now.toString("dddd, MMMM dd")
        self.time_label.setText(f"{formatted_time}\n{formatted_date}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoFrameApp()
    sys.exit(app.exec_())
