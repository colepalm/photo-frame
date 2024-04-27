import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt


class PhotoFrameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")
        self.showFullScreen()

        # Create a central widget and set a main vertical layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)

        # Image label
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        main_layout.addWidget(self.image_label, 1)

        # Horizontal layout for the bottom right time display
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)  # Pushes the time label to the right
        self.time_label = QLabel("00:00", self)
        self.time_label.setFont(QFont('Arial', 18))
        self.time_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        bottom_layout.addWidget(self.time_label)

        main_layout.addLayout(bottom_layout)

        # Top right corner for weather information
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)  # Pushes the weather label to the right
        self.weather_label = QLabel("Loading weather...")
        self.weather_label.setFont(QFont('Arial', 16))
        self.weather_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        main_layout.addLayout(top_layout)
        top_layout.addWidget(self.weather_label)

        # TODO: Requery weather periodically
        # self.weatherUpdateTimer = QTimer(self)
        # self.weatherUpdateTimer.timeout.connect(self.update_weather)
        # self.weatherUpdateTimer.start(600000)  # 10 minutes in milliseconds

        self.photos_dir = './photos'
        self.photos_list = self.load_photos()
        self.current_photo = 0

        self.update_image()
        self.start_image_loop()

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

        # Scale the pixmap to fit the label while maintaining the aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(scaled_pixmap)

        # Cycle through the photo list
        self.current_photo += 1
        if self.current_photo >= len(self.photos_list):
            self.current_photo = 0

    def start_image_loop(self):
        """Change the photo at intervals."""
        self.timer.start(120000)  # Change image every 120 seconds

    def update_time(self):
        # Update time label
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.timeLabel.setText(current_time)

    def update_weather(self):
        # Fetch and update weather
        # Use your existing logic
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoFrameApp()
    window.show()
    sys.exit(app.exec_())
