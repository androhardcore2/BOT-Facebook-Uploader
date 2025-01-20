# Facebook Video Uploader Bot

**Facebook Video Uploader Bot** adalah aplikasi desktop berbasis Python dengan GUI yang dirancang untuk mempermudah proses upload video secara otomatis ke halaman Facebook.
Aplikasi ini memiliki berbagai fitur seperti pengaturan penjadwalan upload, jeda antar upload, dan pengelolaan video dalam folder.

## Fitur Utama
- **Upload Otomatis**: Mengupload semua video dari folder yang dipilih ke halaman Facebook secara otomatis.
- **Penjadwalan Upload**: Menjadwalkan waktu tertentu untuk mulai proses upload.
- **Pengaturan Jeda**: Menentukan jeda waktu antar video yang diupload (dalam menit atau jam).
- **Log Aktivitas**: Melihat log aktivitas upload untuk memantau proses.
- **Pengelolaan Caption dan Deskripsi**: Menambahkan caption dan deskripsi untuk setiap video yang diupload.

## Prasyarat
- Python 3.8 atau lebih baru.
- Token akses Facebook dan ID halaman Facebook.
- Modul Python yang diperlukan:
  - `PyQt5`
  - `requests`
  -  requests
  - import time
    datetime import datetime, timedelta, timezone

## Instalasi
1. **Clone Repository**
   ```bash
   git clone https://github.com/androhardcore2/facebook-video-uploader-bot.git

   cd facebook-video-uploader-bot

2. Install Dependencies Gunakan pip untuk menginstal dependensi yang dibutuhkan:
 ```bash
   pip install -r requirements.txt
