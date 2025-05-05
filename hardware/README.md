```

iot-fire-smoke-detector/
│
├── 📁 docs/                     # Semua dokumentasi proyek
│   ├── proposal.md             # Proposal singkat proyek
│   ├── timeline.md             # Timeline mingguan
│   ├── komponen.md             # Daftar alat dan platform IoT
│   ├── laporan-akhir.pdf       # Laporan akhir (minggu 7)
│   ├── presentasi.pptx         # Slide presentasi akhir
│   └── demo-video.mp4          # Video demo alat
│
├── 📁 images/                   # Gambar diagram & hasil uji
│   ├── sistem-blok.png         # Diagram sistem blok
│   ├── wiring-awal.png         # Wiring diagram awal
│   └── final-setup.jpg         # Foto prototipe jadi
│
├── 📁 hardware/                # Skematik dan desain hardware
│   ├── fritzing.fzz            # File desain dari Fritzing
│   ├── pcb-layout.png          # Desain PCB jika ada
│   └── schematic.pdf           # Rangkuman wiring final
│
├── 📁 firmware/                # Kode ESP32 dan konfigurasi
│   ├── src/
│   │   ├── main.ino            # Program utama ESP32
│   │   ├── wifi\_config.h       # Konfigurasi WiFi
│   │   └── ifttt\_handler.cpp   # Integrasi IFTTT (jika digunakan)
│   └── README.md               # Petunjuk flash kode ke ESP32
│
├── 📁 cloud/                   # Konfigurasi platform IoT
│   ├── ifttt\_webhook.json     # Contoh webhook IFTTT
│   ├── firebase\_config.json   # Config Firebase (opsional)
│   └── mqtt\_example.md        # Petunjuk setup MQTT (opsional)
│
├── 📁 test/                    # Hasil pengujian mingguan
│   ├── minggu2-uji-sensor.md  # Dokumentasi uji komponen
│   ├── minggu3-cloud.md       # Uji koneksi cloud
│   ├── minggu5-integrasi.md   # Hasil integrasi sistem
│   └── minggu6-uji-lapangan.md# Pengujian di lokasi nyata
│
├── .gitignore                  # File untuk mengecualikan file dari Git
├── README.md                   # Penjelasan umum proyek
└── LICENSE                     # Lisensi proyek (misal MIT)

```

