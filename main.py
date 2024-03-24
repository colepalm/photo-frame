import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage


class PhotoFrameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")
        self.showFullScreen()

        # Main widget and layout
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)

        # Image label
        self.imageLabel = QLabel()
        self.layout.addWidget(self.imageLabel)

        # Update image every 2 minutes
        self.imageUpdateTimer = QTimer(self)
        self.imageUpdateTimer.timeout.connect(self.update_image)
        self.imageUpdateTimer.start(120000)  # 2 minutes in milliseconds

        self.timeLabel = QLabel("00:00:00")
        self.layout.addWidget(self.timeLabel)
        self.timeUpdateTimer = QTimer(self)
        self.timeUpdateTimer.timeout.connect(self.update_time)
        self.timeUpdateTimer.start(1000)  # 1 second in milliseconds

        # Weather label
        self.weatherLabel = QLabel("Loading weather...")
        self.layout.addWidget(self.weatherLabel)
        self.weatherUpdateTimer = QTimer(self)
        self.weatherUpdateTimer.timeout.connect(self.update_weather)
        self.weatherUpdateTimer.start(600000)  # 10 minutes in milliseconds

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
        self.imageLabel.setPixmap(pixmap)

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
