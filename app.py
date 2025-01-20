import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta, timezone
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, 
    QFileDialog, QLineEdit, QListWidget, QScrollArea, QSizePolicy, QSpinBox, QComboBox, QDateTimeEdit, QDialog
)
from PyQt5.QtGui import QIcon

from PyQt5.QtCore import QTimer, Qt
from threading import Thread
import webbrowser

class CreditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Tentang Aplikasi")
        self.setFixedSize(400, 300)

        # Set the window icon
        self.setWindowIcon(QIcon("icon.ico"))

        layout = QVBoxLayout()

        # Informasi pembuat
        creator_label = QLabel("Dibuat oleh: Ahwanulm")
        layout.addWidget(creator_label)

        # Deskripsi aplikasi
        description_label = QLabel(
            "Aplikasi BOT Upload Video Otomatis BETA v1.0"
        )
        layout.addWidget(description_label)

        # Tautan ke media sosial
        social_label = QLabel("Ikuti kami di:")
        layout.addWidget(social_label)

        # Tombol ke tautan sosial media
        facebook_btn = QPushButton("Facebook")
        facebook_btn.clicked.connect(lambda: self.open_link("https://www.facebook.com/a0m9997/"))
        layout.addWidget(facebook_btn)
        
        instagram_btn = QPushButton("FB Group")
        instagram_btn.clicked.connect(lambda: self.open_link("https://www.facebook.com/groups/androhardcore1/"))
        layout.addWidget(instagram_btn)
        instagram_btn = QPushButton("FB Group")
        instagram_btn.clicked.connect(lambda: self.open_link("https://www.facebook.com/groups/androhardcore1/"))
        layout.addWidget(instagram_btn)

        github_btn = QPushButton("GitHub")
        github_btn.clicked.connect(lambda: self.open_link("https://github.com/androhardcore2"))
        layout.addWidget(github_btn)

        self.setLayout(layout)

    def open_link(self, url):
        webbrowser.open(url)

class FacebookVideoUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.video_folder = None
        self.auto_upload_running = False
        self.scheduled_upload_time = None
        self.upload_delay = 0
        self.delay_unit = "Menit"
        self.upload_thread = None
        self.uploading_video_index = 0  # Menyimpan indeks video yang sedang diUpload
        self.upload_status = "Berhenti"  # Status Uploadan (Berjalan, Berhenti, Ditunda)

        # Load pengaturan dari file eksternal
        self.settings_file = "settings.json"
        self.access_token, self.page_id = self.load_settings()

        # Set timezone default ke WITA (UTC+8)
        self.wita_timezone = timezone(timedelta(hours=8))

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
                return settings.get("access_token"), settings.get("page_id")
        except FileNotFoundError:
            self.log(f"File pengaturan '{self.settings_file}' tidak ditemukan.")
            sys.exit()
        except json.JSONDecodeError:
            self.log(f"Format JSON tidak valid di '{self.settings_file}'.")
            sys.exit()

    def init_ui(self):
        self.setWindowTitle("Aplikasi BOT Upload Video Otomatis BETA v1.0")
        self.setFixedSize(600, 600)
        
        # Set the window icon
        self.setWindowIcon(QIcon("icon.ico"))

        main_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area_widget = QWidget()
        scroll_area_layout = QVBoxLayout()

        # Bagian Pemilihan Folder
        self.folder_label = QLabel("Path Folder: Tidak ada")
        self.select_folder_btn = QPushButton("Pilih Folder Video")
        self.select_folder_btn.clicked.connect(self.select_folder)
        scroll_area_layout.addWidget(self.folder_label)
        scroll_area_layout.addWidget(self.select_folder_btn)

        # Bagian Input Caption dan Deskripsi
        self.caption_label = QLabel("Caption Video:")
        self.caption_input = QLineEdit()
        scroll_area_layout.addWidget(self.caption_label)
        scroll_area_layout.addWidget(self.caption_input)

        self.description_label = QLabel("Deskripsi Video:")
        self.description_input = QLineEdit()
        scroll_area_layout.addWidget(self.description_label)
        scroll_area_layout.addWidget(self.description_input)

        # Bagian Penjadwalan Uploadan
        self.scheduled_upload_label = QLabel("Atur Waktu Penjadwalan Upload:")
        self.scheduled_datetime_picker = QDateTimeEdit()
        self.scheduled_datetime_picker.setCalendarPopup(True)
        self.scheduled_datetime_picker.setDateTime(datetime.now())  # No timezone needed here
        self.scheduled_upload_btn = QPushButton("Atur Penjadwalan Upload")
        self.scheduled_upload_btn.clicked.connect(self.set_scheduled_upload)
        scroll_area_layout.addWidget(self.scheduled_upload_label)
        scroll_area_layout.addWidget(self.scheduled_datetime_picker)
        scroll_area_layout.addWidget(self.scheduled_upload_btn)

        # Bagian pengaturan delay Uploadan
        self.delay_label = QLabel("Atur Jeda Antar Uploadan:")
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(1, 1440)
        self.delay_spinbox.setValue(10)
        self.delay_unit_combobox = QComboBox()
        self.delay_unit_combobox.addItems(["Menit", "Jam"])
        scroll_area_layout.addWidget(self.delay_label)
        scroll_area_layout.addWidget(self.delay_spinbox)
        scroll_area_layout.addWidget(self.delay_unit_combobox)

        # Bagian Tombol Uploadan Otomatis
        self.auto_upload_label = QLabel("Upload Otomatis Semua Video:")
        self.auto_upload_btn = QPushButton("Mulai Upload Otomatis")
        self.auto_upload_btn.clicked.connect(self.start_auto_upload_and_upload)
        scroll_area_layout.addWidget(self.auto_upload_label)
        scroll_area_layout.addWidget(self.auto_upload_btn)

        # Tombol Berhenti dan Jeda
        self.stop_upload_btn = QPushButton("Berhenti Upload")
        self.stop_upload_btn.clicked.connect(self.stop_upload)
        self.stop_upload_btn.setEnabled(False)
        self.pause_resume_btn = QPushButton("Jeda Upload")
        self.pause_resume_btn.clicked.connect(self.pause_or_resume_upload)
        self.pause_resume_btn.setEnabled(False)
        scroll_area_layout.addWidget(self.stop_upload_btn)
        scroll_area_layout.addWidget(self.pause_resume_btn)

        # Bagian Tampilan Log
        self.log_list = QListWidget()
        scroll_area_layout.addWidget(self.log_list)

        scroll_area_widget.setLayout(scroll_area_layout)
        scroll_area.setWidget(scroll_area_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Timer untuk penjadwalan
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_schedule)
        self.timer.start(1000)

        # Tombol atau menu untuk membuka informasi kredit
        self.credit_btn = QPushButton("Tentang Aplikasi")
        self.credit_btn.clicked.connect(self.open_credit_dialog)
        scroll_area_layout.addWidget(self.credit_btn)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Video")
        if folder:
            self.video_folder = folder
            video_count = len([f for f in os.listdir(folder) if f.lower().endswith(('mp4', 'mov', 'avi'))])
            short_path = self.shorten_path(folder)
            self.folder_label.setText(f"Folder Terpilih: {short_path}")
            self.log(f"Folder terpilih: {folder}")
            self.log(f"Total Video: {video_count}")

    def shorten_path(self, path, max_length=40):
        if len(path) > max_length:
            return f"{path[:15]}...{path[-15:]}"
        return path

    def start_auto_upload_and_upload(self):
        if self.upload_status == "Berjalan":
            self.stop_upload()
        else:
            if not self.video_folder:
                self.log("Silakan pilih folder video terlebih dahulu!")
                return
            if self.scheduled_upload_time:
                self.log("Penjadwalan Uploadan telah diatur. Menunggu waktu penjadwalan.")
            else:
                self.start_auto_upload()
                self.upload_videos_threaded()

    def start_auto_upload(self):
        self.log("Memulai Uploadan otomatis.")
        self.auto_upload_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(True)
        self.stop_upload_btn.setEnabled(True)
        self.upload_status = "Berjalan"
        self.upload_delay = self.delay_spinbox.value()
        self.delay_unit = self.delay_unit_combobox.currentText()

    def stop_upload(self):
        self.upload_status = "Berhenti"
        self.auto_upload_btn.setText("Mulai Upload Otomatis")
        self.auto_upload_btn.setEnabled(True)
        self.stop_upload_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        self.pause_resume_btn.setText("Jeda Upload")
        self.log("Uploadan telah dihentikan.")

        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_thread.join()

    def pause_or_resume_upload(self):
        if self.upload_status == "Berjalan":
            self.upload_status = "Ditunda"
            self.pause_resume_btn.setText("Lanjutkan Upload")
            self.log("Uploadan dijeda.")
        elif self.upload_status == "Ditunda":
            self.upload_status = "Berjalan"
            self.pause_resume_btn.setText("Jeda Upload")
            self.log("Uploadan dilanjutkan.")
            self.upload_videos_threaded()

    def upload_videos_threaded(self):
        self.upload_thread = Thread(target=self.upload_videos)
        self.upload_thread.start()

    def upload_videos(self):
        video_files = [f for f in os.listdir(self.video_folder) if f.lower().endswith(('mp4', 'mov', 'avi'))]
        total_videos = len(video_files)

        for index, video in enumerate(video_files[self.uploading_video_index:], start=self.uploading_video_index):
            if self.upload_status == "Berhenti":
                break

            if self.upload_status == "Ditunda":
                while self.upload_status == "Ditunda":
                    time.sleep(1)

            video_path = os.path.join(self.video_folder, video)
            self.log(f"MengUpload video {index + 1}/{total_videos}: {video}")

            try:
                self.upload_to_facebook(video_path)
            except Exception as e:
                self.log(f"Kesalahan Upload video: {str(e)}")

            self.uploading_video_index = index + 1

            if self.uploading_video_index < total_videos and self.upload_status != "Berhenti":
                self.log(f"Menunggu {self.upload_delay} {self.delay_unit.lower()} sebelum mengUpload video berikutnya.")
                if self.delay_unit == "Menit":
                    time.sleep(self.upload_delay * 60)
                elif self.delay_unit == "Jam":
                    time.sleep(self.upload_delay * 3600)

        self.upload_status = "Berhenti"
        self.auto_upload_btn.setText("Mulai Upload Otomatis")
        self.auto_upload_btn.setEnabled(True)
        self.pause_resume_btn.setEnabled(False)
        self.stop_upload_btn.setEnabled(False)
        self.log("Semua video selesai diUpload.")

    def upload_to_facebook(self, video_path):
        caption = self.caption_input.text()
        description = self.description_input.text()

        url = f"https://graph-video.facebook.com/v18.0/{self.page_id}/videos"
        params = {
            'access_token': self.access_token,
            'title': caption,
            'description': description
        }
        files = {
            'file': open(video_path, 'rb')
        }

        response = requests.post(url, params=params, files=files)

        if response.status_code == 200:
            self.log(f"Video '{os.path.basename(video_path)}' berhasil diUpload.")
        else:
            self.log(f"Uploadan gagal untuk video '{os.path.basename(video_path)}'. Status: {response.status_code}, Pesan: {response.text}")

    def set_scheduled_upload(self):
        self.scheduled_upload_time = self.scheduled_datetime_picker.dateTime().toPyDateTime().replace(tzinfo=self.wita_timezone)
        self.log(f"Penjadwalan Uploadan diatur pada {self.scheduled_upload_time}")

    def run_schedule(self):
        if self.scheduled_upload_time and datetime.now(self.wita_timezone) >= self.scheduled_upload_time:
            self.log("Waktu penjadwalan tercapai. Memulai Uploadan otomatis.")
            self.scheduled_upload_time = None  # Reset setelah penjadwalan berjalan
            self.start_auto_upload()
            self.upload_videos_threaded()

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = f"[{timestamp}] {message}"
        self.log_list.addItem(item)

        # Scroll ke item terakhir (catatan terbaru)
        self.log_list.setCurrentRow(self.log_list.count() - 1)
        self.log_list.scrollToItem(self.log_list.item(self.log_list.count() - 1))

    def open_credit_dialog(self):
        dialog = CreditDialog()
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FacebookVideoUploader()
    window.show()
    sys.exit(app.exec_())
