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

# === Halaman Web Profesional ===
def web_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Fire & Smoke Detection Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    animation: {
                        'pulse-danger': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                        'bounce-slow': 'bounce 2s infinite',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 min-h-screen text-white">
    <!-- Header -->
    <header class="bg-gray-800/50 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-50">
        <div class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="bg-gradient-to-r from-red-500 to-orange-500 p-3 rounded-xl">
                        <i class="fas fa-fire text-white text-xl"></i>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                            Fire & Smoke Detection
                        </h1>
                        <p class="text-gray-400 text-sm">Real-time Safety Monitoring System</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <div id="current-time" class="text-lg font-semibold"></div>
                        <div class="text-gray-400 text-sm">Local Time</div>
                    </div>
                    <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                </div>
            </div>
        </div>
    </header>

    <div class="container mx-auto px-6 py-8">
        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <!-- Fire Status Card -->
            <div class="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 hover:border-red-500/50 transition-all duration-300">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="bg-red-500/20 p-3 rounded-xl">
                            <i class="fas fa-fire text-red-400 text-xl"></i>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold text-gray-200">Fire Detection</h3>
                            <p class="text-gray-400 text-sm">Flame Sensor Status</p>
                        </div>
                    </div>
                </div>
                <div class="text-center">
                    <div id="status_api" class="text-2xl font-bold mb-2 transition-all duration-300">
                        Memuat...
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div id="fire-indicator" class="bg-green-400 h-2 rounded-full transition-all duration-500" style="width: 0%"></div>
                    </div>
                </div>
            </div>

            <!-- Smoke Status Card -->
            <div class="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 hover:border-orange-500/50 transition-all duration-300">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="bg-orange-500/20 p-3 rounded-xl">
                            <i class="fas fa-smog text-orange-400 text-xl"></i>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold text-gray-200">Smoke Detection</h3>
                            <p class="text-gray-400 text-sm">Gas Sensor (MQ2)</p>
                        </div>
                    </div>
                </div>
                <div class="text-center">
                    <div id="status_asap" class="text-2xl font-bold mb-2 transition-all duration-300">
                        Memuat...
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div id="smoke-indicator" class="bg-green-400 h-2 rounded-full transition-all duration-500" style="width: 0%"></div>
                    </div>
                </div>
            </div>

            <!-- Gas Level Card -->
            <div class="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 hover:border-blue-500/50 transition-all duration-300">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="bg-blue-500/20 p-3 rounded-xl">
                            <i class="fas fa-tachometer-alt text-blue-400 text-xl"></i>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold text-gray-200">Gas Level</h3>
                            <p class="text-gray-400 text-sm">Current Reading</p>
                        </div>
                    </div>
                </div>
                <div class="text-center">
                    <div id="gas_value" class="text-3xl font-bold text-blue-400 mb-2">-</div>
                    <div class="text-gray-400 text-sm">PPM</div>
                </div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <!-- Gas Chart -->
            <div class="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700">
                <div class="flex items-center space-x-3 mb-6">
                    <div class="bg-orange-500/20 p-2 rounded-lg">
                        <i class="fas fa-chart-line text-orange-400"></i>
                    </div>
                    <h3 class="text-xl font-semibold">Gas Level Trend</h3>
                </div>
                <div class="relative h-64">
                    <canvas id="gasChart" class="w-full h-full"></canvas>
                </div>
            </div>

            <!-- Flame Chart -->
            <div class="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700">
                <div class="flex items-center space-x-3 mb-6">
                    <div class="bg-red-500/20 p-2 rounded-lg">
                        <i class="fas fa-chart-area text-red-400"></i>
                    </div>
                    <h3 class="text-xl font-semibold">Fire Detection History</h3>
                </div>
                <div class="relative h-64">
                    <canvas id="flameChart" class="w-full h-full"></canvas>
                </div>
            </div>
        </div>

        <!-- Location Section -->
        <div class="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700">
            <div class="flex items-center space-x-3 mb-6">
                <div class="bg-green-500/20 p-2 rounded-lg">
                    <i class="fas fa-map-marker-alt text-green-400"></i>
                </div>
                <h3 class="text-xl font-semibold">Monitoring Location</h3>
            </div>
            <div class="relative rounded-xl overflow-hidden border border-gray-600">
                <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d247.89161242341785!2d106.7887656064085!3d-6.2286460054432355!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e69f13094c83677%3A0x1f4300031365732b!2sUniversitas%20Pertamina!5e0!3m2!1sen!2sid!4v1748236595439!5m2!1sen!2sid" 
                        width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade" class="filter brightness-90">
                </iframe>
            </div>
        </div>
    </div>

    <!-- Emergency Alert Modal -->
    <div id="emergency-modal" class="fixed inset-0 bg-black bg-opacity-75 hidden z-50 flex items-center justify-center">
        <div class="bg-red-600 text-white p-8 rounded-2xl max-w-md mx-4 text-center animate-bounce-slow">
            <i class="fas fa-exclamation-triangle text-6xl mb-4"></i>
            <h2 class="text-2xl font-bold mb-4">EMERGENCY ALERT!</h2>
            <p class="text-lg mb-6">Fire or smoke detected! Please evacuate immediately!</p>
            <button onclick="closeEmergencyModal()" class="bg-white text-red-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Acknowledge
            </button>
        </div>
    </div>

    <script>
        // Time Display
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
        }
        setInterval(updateTime, 1000);
        updateTime();

        // Chart Configuration
        Chart.defaults.color = '#9CA3AF';
        Chart.defaults.borderColor = '#374151';

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
                    label: 'Gas Level (PPM)',
                    data: gasData,
                    borderColor: '#F97316',
                    backgroundColor: 'rgba(249, 115, 22, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#F97316',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: { 
                        beginAtZero: true,
                        grid: {
                            color: '#374151'
                        }
                    },
                    x: {
                        grid: {
                            color: '#374151'
                        }
                    }
                }
            }
        });

        const flameChart = new Chart(flameCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Fire Status',
                    data: flameData,
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#EF4444',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 1,
                        grid: {
                            color: '#374151'
                        }
                    },
                    x: {
                        grid: {
                            color: '#374151'
                        }
                    }
                }
            }
        });

        let emergencyShown = false;

        function showEmergencyModal() {
            if (!emergencyShown) {
                document.getElementById('emergency-modal').classList.remove('hidden');
                emergencyShown = true;
            }
        }

        function closeEmergencyModal() {
            document.getElementById('emergency-modal').classList.add('hidden');
            emergencyShown = false;
        }

        async function fetchData() {
            try {
                const res = await fetch('/data');
                const data = await res.json();

                if (data.length === 0) return;

                const latest = data[data.length - 1];
                
                // Fire Status
                const statusApi = document.getElementById('status_api');
                const fireIndicator = document.getElementById('fire-indicator');
                if (latest.flame) {
                    statusApi.innerText = "DETECTED!";
                    statusApi.className = "text-2xl font-bold mb-2 text-red-400 animate-pulse-danger";
                    fireIndicator.className = "bg-red-500 h-2 rounded-full transition-all duration-500";
                    fireIndicator.style.width = "100%";
                    showEmergencyModal();
                } else {
                    statusApi.innerText = "Safe";
                    statusApi.className = "text-2xl font-bold mb-2 text-green-400";
                    fireIndicator.className = "bg-green-400 h-2 rounded-full transition-all duration-500";
                    fireIndicator.style.width = "0%";
                }

                // Smoke Status
                const statusAsap = document.getElementById('status_asap');
                const smokeIndicator = document.getElementById('smoke-indicator');
                if (latest.gas > 800) {
                    statusAsap.innerText = "DETECTED!";
                    statusAsap.className = "text-2xl font-bold mb-2 text-orange-400 animate-pulse-danger";
                    smokeIndicator.className = "bg-orange-500 h-2 rounded-full transition-all duration-500";
                    smokeIndicator.style.width = "100%";
                    showEmergencyModal();
                } else {
                    statusAsap.innerText = "Safe";
                    statusAsap.className = "text-2xl font-bold mb-2 text-green-400";
                    smokeIndicator.className = "bg-green-400 h-2 rounded-full transition-all duration-500";
                    smokeIndicator.style.width = Math.min((latest.gas / 800) * 100, 100) + "%";
                }

                document.getElementById('gas_value').innerText = latest.gas;

                // Update Charts
                const waktu = new Date().toLocaleTimeString();
                if (labels.length > 10) {
                    labels.shift();
                    gasData.shift();
                    flameData.shift();
                }

                labels.push(waktu);
                gasData.push(latest.gas);
                flameData.push(latest.flame);

                gasChart.update('none');
                flameChart.update('none');

            } catch (e) {
                console.error('Error fetching data:', e);
            }
        }

        // Start data fetch
        setInterval(fetchData, 3000);
        fetchData();
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