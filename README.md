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
