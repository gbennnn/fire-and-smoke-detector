# Fire and Smoke Detection - Kelompok 12

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
        print("❌ Gagal konek WiFi")
        break

if station.isconnected():
    print("✅ Koneksi sukses, IP:", station.ifconfig()[0])

# === Inisialisasi Sensor dan Buzzer ===
buzzer = PWM(Pin(5), freq=1000)
buzzer.duty(0)

mq2_analog = ADC(Pin(34))  # MQ2 ke pin analog
mq2_analog.atten(ADC.ATTN_11DB)

flame_digital = Pin(13, Pin.IN)  # Gunakan GPIO13, bukan GPIO2

# === Fungsi Deteksi ===
def read_flame():
    return flame_digital.value()

def read_gas():
    return mq2_analog.read()

def activate_buzzer(active):
    buzzer.duty(512 if active else 0)

# === Variabel Status ===
status_api = "Tidak terdeteksi"
status_asap = "Tidak terdeteksi"
gas_value = 0
data_log = []

# === Update Sensor ===
async def update_sensor():
    global status_api, status_asap, gas_value, data_log
    while True:
        flame = read_flame()
        gas = read_gas()
        gas_value = gas

        # Debugging print
        print("Raw flame sensor value:", flame)

        status_api = "TERDETEKSI!" if flame == 0 else "Tidak terdeteksi"
        status_asap = "TERDETEKSI!" if gas > 800 else "Tidak terdeteksi"

        activate_buzzer(flame == 0 or gas > 800)

        data_log.append({
            "gas": gas,
            "flame": 0 if flame == 0 else 1
        })

        if len(data_log) > 10:
            data_log.pop(0)

        print(f"[Sensor] Api: {status_api}, Gas: {gas} ({status_asap})")
        await asyncio.sleep(3)

# === Halaman Web ===
def web_page():
    return f"""
<html>
<head>
    <title>Fire & Smoke Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h2>🚨 Fire & Smoke Detection</h2>
    <p>Status Api: <strong>{status_api}</strong></p>
    <p>Status Asap: <strong>{status_asap}</strong></p>
    <p>Gas Level (MQ2): <strong>{gas_value}</strong></p>

    <canvas id="gasChart"></canvas>

    <script>
    const ctx = document.getElementById('gasChart').getContext('2d');
    const chart = new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: [],
            datasets: [{{
                label: 'Gas Level',
                borderColor: 'red',
                data: [],
                fill: false
            }}]
        }},
        options: {{
            responsive: true,
            animation: false
        }}
    }});

    function fetchData() {{
        fetch('/data')
            .then(res => res.json())
            .then(data => {{
                chart.data.labels = data.map((_, i) => i + 1);
                chart.data.datasets[0].data = data.map(d => d.gas);
                chart.update();
            }});
    }}

    setInterval(fetchData, 3000);
    fetchData();
    </script>
</body>
</html>
"""

# === Web Server ===
async def serve_client(reader, writer):
    request_line = await reader.readline()
    request = str(request_line)
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

# === Main Program ===
async def main():
    print("Server aktif di http://%s" % station.ifconfig()[0])
    asyncio.create_task(update_sensor())
    server = await asyncio.start_server(serve_client, "0.0.0.0", 80)
    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
except Exception as e:
    print("❌ Error utama:", e)