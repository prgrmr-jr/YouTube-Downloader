####################################################################################################
# Project: Youtube Downloader
# Author: Jose Rey
# Date Created: 2023-07-30
# Description: A simple YouTube downloader using PyQt5 and pytube
####################################################################################################
# Github : https://github.com/joserey-alfante
####################################################################################################
import os
import sys
import urllib.request
from PyQt5.QtCore import QCoreApplication
from pytube import YouTube
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QFileDialog
from PyQt5.uic import loadUi


# Video Length Format
def format_duration(duration_seconds):
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60

    formatted_duration = ""
    if hours > 0:
        if hours == 1:
            formatted_duration += f"{hours} hour :  "
        else:
            formatted_duration += f"{hours} hours :  "
    if minutes > 0:
        formatted_duration += f"{minutes} minutes : "
    formatted_duration += f"{seconds} seconds"

    return formatted_duration


class YoutubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        try:
            loadUi("./assets/ui/youtubedonwloader.ui", self)
            QCoreApplication.setApplicationName("Youtube Downloader")
            self.setWindowTitle("Youtube Downloader")
            self.setWindowIcon(QIcon("./assets/images/logo.png"))

            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon("./assets/images/logo.png"))  # Load your custom image here
            self.tray_icon.setToolTip('YouTube Downloader')
            self.tray_icon.activated.connect(self.on_tray_icon_activated)

            self.tray_icon.show()

            # set items not visible
            self.lblTitle.setVisible(False)
            self.lblViews.setVisible(False)
            self.lblDuration.setVisible(False)
            self.btnMp3.setVisible(False)
            self.btnMp4.setVisible(False)
            self.errorMessage.setVisible(False)

            # set methods for buttons
            self.btnSearch.clicked.connect(self.search_details)
            self.btnMp3.clicked.connect(self.download_mp3)
            self.btnMp4.clicked.connect(self.download_mp4)

        except Exception as e:
            print(e)

    # Hiding Items in the UI
    def unshow_items(self):
        self.lblTitle.setVisible(False)
        self.lblViews.setVisible(False)
        self.lblDuration.setVisible(False)
        self.btnMp3.setVisible(False)
        self.btnMp4.setVisible(False)
        self.imgThumbnail.setPixmap(QPixmap("./assets/images/thnail.png"))

    # Fetching the details of the video
    def search_details(self):
        if self.linkInput.text() == "":
            self.errorMessage.setVisible(True)
            self.errorMessage.setText("Please Enter a Link First")
            self.unshow_items()
            return
        self.errorMessage.setVisible(False)

        try:
            yt_link = self.linkInput.text()
            yt = YouTube(yt_link)
            self.lblTitle.setText(f'Title: {yt.title}')
            self.lblViews.setText(f'Views: {yt.views:,}')
            self.lblDuration.setText(f'Duration: {format_duration(yt.length)}')
            thumbnail_url = yt.thumbnail_url

            thumbnail_data = urllib.request.urlopen(thumbnail_url).read()
            thumbnail_pixmap = QPixmap()
            thumbnail_pixmap.loadFromData(thumbnail_data)
            self.imgThumbnail.setPixmap(thumbnail_pixmap)

            self.show_items()

        except Exception as ex:
            print(ex)
            self.errorMessage.setVisible(True)
            self.errorMessage.setText("Invalid Link Please Try Again")

    # Downloading the yt link as mp3
    def download_mp3(self):
        yt_link = self.linkInput.text()
        try:
            yt = YouTube(yt_link)
            save_location, _ = QFileDialog.getSaveFileName(self, 'Save Video', yt.title, 'Audio Files (*.mp3)')
            if save_location:
                self.download_start_message()
                out_path = yt.streams.filter(only_audio=True).first().download(output_path=os.getcwd(),
                                                                               filename=save_location)
                base, ext = os.path.splitext(out_path)
                new_file = base + '.mp3'
                os.rename(out_path, new_file)
                self.download_complete_message('mp3')
        except Exception as e:
            print(f'Error: {e}')
            self.errorMessage.setVisible(True)
            self.errorMessage.setText("Audio not Available !!")

    # Downloading the yt link as mp4
    def download_mp4(self):
        yt_link = self.linkInput.text()
        try:
            yt = YouTube(yt_link)
            video_stream = yt.streams.get_highest_resolution()
            save_location, _ = QFileDialog.getSaveFileName(self, 'Save Video', yt.title, 'Video Files (*.mp4)')
            if save_location:
                self.download_start_message()
                video_stream.download(output_path=os.getcwd(), filename=save_location)
                self.download_complete_message('mp4')
        except Exception as e:
            print(e)
            self.errorMessage.setVisible(True)
            self.errorMessage.setText("Video not Available to Download because of Age Restriction !!")
            self.tray_icon.showMessage('Youtube Downloader', 'Video not Available to Download !!',
                                       QSystemTrayIcon.Warning, 5000)

    # Tray Icon Messages if Download Started
    def download_start_message(self):
        self.tray_icon.showMessage('Youtube Downloader', 'Download Started....',
                                   QSystemTrayIcon.Information, 1000)

    # Tray Icon Messages if Download Completed
    def download_complete_message(self, dltype):
        self.tray_icon.showMessage('Youtube Downloader', f'The {dltype} file downloaded successfully.',
                                   QSystemTrayIcon.Information, 5000)

    # Showing Items in the UI
    def show_items(self):
        self.lblTitle.setVisible(True)
        self.lblViews.setVisible(True)
        self.lblDuration.setVisible(True)
        self.btnMp3.setVisible(True)
        self.btnMp4.setVisible(True)

    # Tray Icon Double-Click Event
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window()

    # Tray Icon Toggle Window
    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()


# Main Function
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YoutubeDownloader()
    window.show()
    sys.exit(app.exec())
