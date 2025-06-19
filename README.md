# 🔥 Fire and Smoke Detector

Proyek ini merupakan bagian dari tugas kuliah Internet of Things (IoT) yang bertujuan untuk mendeteksi asap dan api menggunakan sensor dan mengirimkan peringatan beserta lokasi melalui internet. Proyek ini juga mendukung Tujuan Pembangunan Berkelanjutan (Sustainable Development Goals / SDG) nomor 11: **Sustainable Cities and Communities**.

## 🎯 Tujuan Proyek

- Mendeteksi asap dan/atau api di lingkungan sekitar menggunakan sensor MQ2 dan flame sensor.
- Mengirimkan peringatan (alert) ke pengguna secara real-time menggunakan internet.
- Menyertakan lokasi kejadian melalui integrasi dengan Google Maps API.
- Mendukung kontrol dan monitoring jarak jauh.

## 📦 Komponen yang Digunakan

| Komponen     | Fungsi                                |
| ------------ | ------------------------------------- |
| ESP32        | Mikrokontroler utama (WiFi + kontrol) |
| MQ2          | Sensor pendeteksi gas/asap            |
| Flame Sensor | Sensor pendeteksi api                 |
| Buzzer       | Menghasilkan bunyi sebagai alarm      |
| Breadboard   | Perakitan sementara                   |
| Kabel jumper | Koneksi antar komponen                |

## 🧱 Diagram Sistem Blok

Perangkat keras (sensor dan ESP32) → Internet → Pengguna (notifikasi / dashboard)
![ilustrasi-sistem](images/ilustrasi-sistem.png)

<br>

![alur-kerja-sistem](images/alur-blok-sistem.png)

<!-- ## 📅 Timeline Proyek

Tasks deadline: <br>
✅ Task 1 (topik dan repo) : https://forms.office.com/r/8tWUJSvWU9 <br>
✅ Task 2 (diagram blok sistem) : 25 Mei 2025 <br>
✅ Task 3 (desain sistem lengkap UI/UX software dan hardware) : 1 Juni 2025 <br>
✅ Task 4 (Implementasi hardware) : 8 Juni 2025 <br>
✅ Task 5 (Implementasi software) : 15 Juni 2025 <br>
🔳 Task 6 (Integrasi software + hardware) : 22 Juni 2025 <br>
🔳 Task 7 (Pengujian sistem dan penyempurnaan) : 29 Juni 2025 <br>
🔳 Task 8 (Laporan akhir) via e learning : 6 Juli 2025 <br> -->

## 📜 Lisensi

Proyek ini dilisensikan di bawah MIT License. Silakan gunakan dan modifikasi dengan tetap memberikan atribusi.

---

📍 **Dibuat oleh Kelompok 12:**

1. Benony Gabriel (NIM: 105222002)
2. Senopati Baruna Pasha (NIM: 10522023)

**Universitas Pertamina, 2025**
