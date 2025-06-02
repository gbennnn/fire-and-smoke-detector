# Fire and Smoke Detection - Kelompok 12 (versi revisi)

try:
    import usocket as socket
except:
    import socket

import network
import gc
import esp
esp.osdebug(None)

gc.collect()

from machine import Pin, PWM, ADC
import uasyncio as asyncio
import ujson
import time

# === Koneksi WiFi ===
ssid = "hp"
password = "password"

print("Menghubungkan ke WiFi...")
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

start = time.time()
timeout = 15
while not station.isconnected():
    if time.time() - start > timeout:
        print("Gagal konek WiFi")
        break

if station.isconnected():
    print("Koneksi sukses, IP:", station.ifconfig()[0])

# === Inisialisasi Sensor dan Buzzer ===
buzzer = PWM(Pin(5), freq=1000)
buzzer.duty(0)

mq2_analog = ADC(Pin(34))  # MQ2 ke pin analog
mq2_analog.atten(ADC.ATTN_11DB)

flame_digital = Pin(13, Pin.IN)  # Sensor flame di GPIO13

# === Fungsi Deteksi ===
def read_flame():
    return flame_digital.value()  # Flame sensor: 1 = api terdeteksi, 0 = tidak ada api

def read_gas():
    return mq2_analog.read()

def activate_buzzer(active):
    buzzer.duty(512 if active else 0)

# === Variabel Global ===
status_api = "Tidak terdeteksi"
status_asap = "Tidak terdeteksi"
gas_value = 0
data_log = []

# === Update Sensor Secara Periodik ===
async def update_sensor():
    global status_api, status_asap, gas_value, data_log
    while True:
        flame = read_flame()
        gas = read_gas()
        gas_value = gas

        # Logika: flame == 1 artinya api TERDETEKSI
        status_api = "TERDETEKSI!" if flame == 1 else "Tidak terdeteksi"
        status_asap = "TERDETEKSI!" if gas > 800 else "Tidak terdeteksi"

        activate_buzzer(flame == 1 or gas > 800)

        data_log.append({
            "gas": gas,
            "flame": flame
        })

        if len(data_log) > 10:
            data_log.pop(0)

        print(f"[Sensor] Api: {status_api}, Gas: {gas} ({status_asap})")
        await asyncio.sleep(3)

# === Halaman Web Sederhana ===
def web_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Fire & Smoke Detection</title>
    <style>
        body { font-family: sans-serif; text-align: center; }
        canvas { max-width: 600px; margin: 20px auto; }
        .danger { color: red; font-weight: bold; }
        #map-container { display: none; margin-top: 24px; }
    </style>
</head>
<body>
    <h2>Fire & Smoke Monitor</h2>
    <p>Status Api: <span id="status_api">Memuat...</span></p>
    <p>Status Asap: <span id="status_asap">Memuat...</span></p>
    <p>Gas Value: <span id="gas_value">-</span></p>

    <canvas id="gasChart"></canvas>
    <canvas id="flameChart"></canvas>

    <div id="map-container">
        <h2>Lokasi Kebakaran</h2>
        <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d247.89161242341785!2d106.7887656064085!3d-6.2286460054432355!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e69f13094c83677%3A0x1f4300031365732b!2sUniversitas%20Pertamina!5e0!3m2!1sen!2sid!4v1748236595439!5m2!1sen!2sid" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const gasData = [];
        const flameData = [];
        const labels = [];

        const gasCtx = document.getElementById('gasChart').getContext('2d');
        const flameCtx = document.getElementById('flameChart').getContext('2d');

        const gasChart = new Chart(gasCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Gas Value',
                    data: gasData,
                    borderColor: 'orange',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        const flameChart = new Chart(flameCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Flame',
                    data: flameData,
                    borderColor: 'red',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 1
                    }
                }
            }
        });

        async function fetchData() {
            try {
                const res = await fetch('/data');
                const data = await res.json();

                const latest = data[data.length - 1];
                // Status Api
                const statusApi = document.getElementById('status_api');
                if (latest.flame) {
                    statusApi.innerText = "TERDETEKSI!";
                    statusApi.className = "danger";
                } else {
                    statusApi.innerText = "Tidak terdeteksi";
                    statusApi.className = "";
                }
                // Status Asap
                const statusAsap = document.getElementById('status_asap');
                if (latest.gas > 800) {
                    statusAsap.innerText = "TERDETEKSI!";
                    statusAsap.className = "danger";
                } else {
                    statusAsap.innerText = "Tidak terdeteksi";
                    statusAsap.className = "";
                }
                document.getElementById('gas_value').innerText = latest.gas;

                // Tampilkan map jika api/asap terdeteksi
                const mapContainer = document.getElementById('map-container');
                if (latest.flame || latest.gas > 800) {
                    mapContainer.style.display = "block";
                } else {
                    mapContainer.style.display = "none";
                }

                const waktu = new Date().toLocaleTimeString();
                if (labels.length > 10) {
                    labels.shift();
                    gasData.shift();
                    flameData.shift();
                }

                labels.push(waktu);
                gasData.push(latest.gas);
                flameData.push(latest.flame);

                gasChart.update();
                flameChart.update();
            } catch (e) {
                console.error(e);
            }
        }

        setInterval(fetchData, 3000); // Update setiap 3 detik
    </script>
</body>
</html>
"""

# === Web Server ===
async def serve_client(reader, writer):
    request_line = await reader.readline()
    if not request_line:
        return

    request = request_line.decode()
    print("Request:", request)

    while await reader.readline() != b"\r\n":
        pass

    if "GET /data" in request:
        response = ujson.dumps(data_log)
        writer.write("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n")
        writer.write(response)
    else:
        response = web_page()
        writer.write("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        writer.write(response)

    await writer.drain()
    await writer.aclose()

# === Program Utama ===
async def main():
    print("Server aktif di http://%s" % station.ifconfig()[0])
    asyncio.create_task(update_sensor())
    server = await asyncio.start_server(serve_client, "0.0.0.0", 80)
    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
except Exception as e:
    print("Error utama:", e)
