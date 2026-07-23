# J.A.R.V.I.S Google Bot

Asisten Telegram cerdas berbasis AI dengan integrasi Google Workspace (Calendar, Tasks, Gmail, Drive) dan kemampuan terminal.

## 🚀 Instalasi Cepat di VPS/Server (One-Liner)

Gunakan perintah `curl` berikut di terminal server Linux Anda (Ubuntu/Debian) untuk menginstal J.A.R.V.I.S secara otomatis ke direktori `/opt/jarvish-google/` dan mendaftarkannya sebagai *Background Service* (`systemd`).

```bash
curl -sSL https://raw.githubusercontent.com/yayangkasep/jarvish-google/master/install.sh | sudo bash
```

> **Perhatian:**
> 1. Pastikan server sudah terinstal `python3`, `python3-venv`, `python3-pip`, dan `git`.
> 2. Skrip ini akan secara otomatis melakukan kloning (*download*) repositori ini langsung ke *server* Anda tanpa meminta *password*.

## 📁 Apa yang dilakukan Installer?

1. **Membuat Folder:** Menyiapkan tempat khusus di `/opt/jarvish-google/`.
2. **Kloning Repo:** Menarik kode sumber versi terbaru dari GitHub secara otomatis.
3. **Environment:** Membuat *Virtual Environment* Python (`.venv`) dan menginstal seluruh pustaka (`requirements.txt`).
4. **Backend (Docker):** Mengunduh *image* `antigravity-manager` dan `searxng`, lalu menyalakannya (jika server memiliki Docker).
5. **Systemd Service:** Mengonfigurasi `jarvish.service` sehingga bot otomatis berjalan di latar belakang dan *auto-restart* jika server mati.

## ⚙️ Perintah Operasional

Setelah J.A.R.V.I.S terinstal, Anda bisa mengelolanya dengan perintah *systemd* standar:

- **Cek Status Bot:** 
  `sudo systemctl status jarvish`
- **Melihat Log Obrolan/Error secara Real-time:** 
  `sudo journalctl -u jarvish -f`
- **Merestart Bot:** 
  `sudo systemctl restart jarvish`
- **Menghentikan Bot:** 
  `sudo systemctl stop jarvish`

## 💻 Instalasi Manual (Windows / Local)

Jika Anda ingin menjalankan J.A.R.V.I.S secara manual di komputer lokal (misalnya di Windows), ikuti langkah-langkah berikut:

1. **Clone Repositori:**
   ```powershell
   git clone https://github.com/yayangkasep/jarvish-google.git
   cd jarvish-google
   ```

2. **Buat Virtual Environment:**
   Pastikan Anda sudah menginstal Python (disarankan versi 3.10+).
   ```powershell
   python -m venv .venv
   ```

3. **Aktifkan Virtual Environment:**
   Ini adalah langkah yang paling penting. Anda harus mengaktifkan *environment* sebelum menginstal modul.
   ```powershell
   # Untuk Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   
   # Untuk Windows Command Prompt (CMD):
   .\.venv\Scripts\activate.bat
   ```
   *(Jika berhasil, akan ada tulisan `(.venv)` di sebelah kiri input terminal Anda).*

4. **Instal Modul / Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Jalankan J.A.R.V.I.S:**
   ```powershell
   python main.py
   ```
