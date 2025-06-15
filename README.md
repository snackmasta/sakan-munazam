# Penjelasan Arsitektur SCADA Sakan Munazam

Sakan Munazam adalah sistem kontrol ruangan cerdas yang mengadopsi arsitektur **SCADA** (Supervisory Control and Data Acquisition) untuk mengelola perangkat lampu dan kunci secara terpusat dan terintegrasi. Sistem ini terdiri dari beberapa komponen utama yang saling terhubung melalui berbagai protokol komunikasi:

## Komponen Utama

### 1. Master Server (Python)

- Berfungsi sebagai pusat pengendali (**supervisory**), menjalankan logika kontrol, HMI (Human Machine Interface), serta manajemen perangkat.
- Berkomunikasi dengan perangkat slave (lampu & kunci) menggunakan protokol **UDP** untuk kontrol dan monitoring secara real-time.
- Terhubung ke **KEPServerEX/OPC** untuk integrasi dengan sistem SCADA industri.

### 2. Slave Devices (ESP8266)

- Terdiri dari perangkat pengendali lampu (`light_207`, `light_208`) dan kunci (`lock_207`, `lock_208`).
- Menerima perintah dan mengirim status ke Master Server melalui **UDP**.
- Mendukung update firmware **OTA** (Over The Air) melalui HTTP dari OTA Server.

### 3. OTA Server (Node.js)

- Menyediakan layanan update firmware untuk seluruh perangkat slave secara terpusat melalui **HTTP**.

### 4. Web Interface

- Menyediakan antarmuka pengguna berbasis web untuk monitoring dan kontrol, serta melakukan relay HTTP/UDP ke Master dan OTA Server.

### 5. KEPServerEX/OPC

- Bertindak sebagai jembatan antara sistem Sakan Munazam dan sistem SCADA/industri eksternal.
- Master Server mengirim data ke KEPServerEX menggunakan protokol **HTTP/OPC UA**, sehingga data perangkat dapat diakses oleh sistem SCADA lain.

## Alur Komunikasi SCADA

- **Master Server ↔ KEPServerEX/OPC:**
  - Master Server mengirimkan data status dan kontrol ke KEPServerEX menggunakan **HTTP/OPC UA**. Dengan ini, data dari perangkat slave (lampu/kunci) dapat dimonitor dan dikendalikan dari sistem SCADA eksternal.

- **Master Server ↔ Slave Devices:**
  - Komunikasi dua arah menggunakan **UDP** untuk memastikan kontrol dan monitoring perangkat secara real-time.

- **Web Interface ↔ Master/OTA/KEPServerEX:**
  - Web Interface dapat mengakses data dan mengirim perintah ke Master Server, OTA Server, dan KEPServerEX melalui **HTTP**, sehingga pengguna dapat melakukan monitoring dan kontrol dari browser.

- **OTA Server → Slave Devices:**
  - Update firmware dikirim ke perangkat slave melalui **HTTP**, memastikan perangkat selalu up-to-date.

## System Configuration

Sistem Sakan Munazam menggunakan beberapa file konfigurasi untuk mengatur parameter jaringan, tipe perangkat, dan perintah yang digunakan oleh master server dan perangkat slave. Berikut adalah ringkasan konfigurasi utama:

### Struktur & Lokasi File Konfigurasi

- **Master Server Configuration**
  - Lokasi: `master/config/settings.py`
  - Berisi pengaturan port UDP, buffer size, tipe perangkat (`light`, `lock`), dan definisi perintah (`ON`, `OFF`, `LOCK`, `UNLOCK`).
  - Contoh isi:
    ```python
    UDP_PORT = 4210
    BUFFER_SIZE = 1024
    DEVICE_TYPE_LIGHT = "light"
    DEVICE_TYPE_LOCK = "lock"
    CMD_ON = "ON"
    CMD_OFF = "OFF"
    CMD_LOCK = "LOCK"
    CMD_UNLOCK = "UNLOCK"
    ```

- **Device Mapping**
  - Lokasi: Hardcoded di beberapa file Python (misal: `master_hmi.py`)
  - Mendefinisikan mapping antara nama perangkat (`lock_207`, `light_207`, dll) dengan IP address dan tipe perangkat.

- **OTA Server Configuration**
  - Lokasi: `Web/OTA/server.js`
  - Pengaturan port HTTP OTA (`PORT = 5000`), path file firmware, dan struktur data perangkat (`devices.json`).

- **Slave Device Configuration**
  - Lokasi: Di setiap file `main.cpp` pada folder slave (misal: `slave/lock_207/src/main.cpp`)
  - Mendefinisikan parameter seperti SSID WiFi, password, alamat server OTA, port, device ID, dan pengaturan heartbeat.

### Parameter Penting

- **UDP_PORT**: Port utama untuk komunikasi UDP antara master dan slave (default: 4210).
- **HEARTBEAT_PORT**: Port untuk heartbeat monitoring (default: 4220).
- **OTA_PORT**: Port HTTP untuk update firmware OTA (default: 5000).
- **DEVICE_ID**: ID unik untuk setiap perangkat slave (misal: `lock_207`, `light_208`).
- **SSID & Password**: Kredensial WiFi yang digunakan oleh slave untuk koneksi ke jaringan.
- **Mapping Lock-Light**: Relasi antara perangkat kunci dan lampu untuk logika reservasi.

### Cara Mengubah Konfigurasi

- Untuk mengubah port, device mapping, atau parameter lain, edit file konfigurasi terkait:
  - Ubah `master/config/settings.py` untuk pengaturan master.
  - Ubah variabel di file `main.cpp` pada slave untuk pengaturan perangkat.
  - Ubah `server.js` untuk pengaturan OTA server.

### Cara Mengkonfigurasi Sistem

1. **Konfigurasi Master Server**
   - Edit file: `master/config/settings.py`
   - Ubah parameter seperti `UDP_PORT`, `BUFFER_SIZE`, dan perintah (`CMD_ON`, `CMD_OFF`, dll) sesuai kebutuhan.
   - Simpan perubahan dan restart aplikasi master server.

2. **Konfigurasi Mapping Perangkat**
   - Mapping nama perangkat ke IP dan tipe biasanya di-hardcode di file Python seperti `master_hmi.py`.
   - Pastikan setiap perangkat slave (misal: `lock_207`, `light_208`) sudah memiliki IP dan tipe yang benar.

3. **Konfigurasi OTA Server**
   - Edit file: `Web/OTA/server.js`
   - Ubah port HTTP OTA (`PORT`), path firmware, dan data perangkat di `devices.json` jika diperlukan.
   - Restart OTA server setelah perubahan.

4. **Konfigurasi Slave Device**
   - Edit file: `main.cpp` pada masing-masing folder slave, misal: `slave/lock_207/src/main.cpp`
   - Ubah parameter berikut sesuai kebutuhan:
     - SSID dan password WiFi
     - Alamat server OTA (`OTA_SERVER`)
     - Port (`OTA_PORT`, `HEARTBEAT_PORT`)
     - `DEVICE_ID`
   - Setelah mengubah, upload firmware ke perangkat slave.

5. **Update IP Master Secara Otomatis**
   - Jalankan script `update_master_ip.ps1` untuk mengganti IP master di seluruh file slave (`main.cpp`, `OTAHandler.cpp`) secara otomatis.
   - Ikuti instruksi pada terminal, masukkan IP baru, dan script akan memperbarui semua file yang diperlukan.

6. **Restart Semua Service**
   - Setelah mengubah konfigurasi, restart service terkait (master server, OTA server, dan slave device) agar perubahan diterapkan.

### Catatan

- Pastikan setiap perubahan pada konfigurasi diikuti dengan restart service terkait (master, OTA server, atau slave device).
- Mapping perangkat dan parameter penting lain juga dapat di-hardcode pada beberapa file Python, sehingga perlu konsistensi antar file.

---

## Panduan Setup & Menjalankan GUI

### Prasyarat
- Python 3.10 atau lebih baru sudah terpasang di sistem Anda
- pip sudah terpasang

### 1. Instalasi Dependensi
Buka terminal di folder utama project, lalu jalankan:

```bash
pip install -r requirements.txt
```

### 2. Menjalankan Master HMI (GUI)
Masih di folder utama, jalankan perintah berikut untuk memulai aplikasi GUI:

```bash
python master_hmi.py
```

Atau gunakan task build yang tersedia di VS Code:
- Tekan `Ctrl+Shift+B` lalu pilih `Build master_hmi.py with Python 3.10`

### 3. Berinteraksi dengan GUI
- Setelah perintah di atas dijalankan, jendela GUI Human Machine Interface (HMI) akan muncul.
- Anda dapat melakukan monitoring dan kontrol perangkat (lampu/kunci) langsung dari GUI ini.
- Pastikan semua konfigurasi jaringan dan mapping perangkat sudah benar agar komunikasi berjalan lancar.

### 4. Troubleshooting
- Jika GUI tidak muncul atau ada error, pastikan semua dependensi sudah terinstal dan file konfigurasi sudah benar.
- Cek log pada file `server.log` atau output terminal untuk pesan error lebih detail.
