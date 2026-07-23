# J.A.R.V.I.S Google Bot

Asisten cerdas berbasis AI dengan integrasi Google Workspace (Calendar, Tasks, Gmail, Drive), penglihatan mesin (Vision), dan kemampuan terminal interaktif.

## 🏗 Arsitektur Bersih (Clean Architecture)

Proyek ini menggunakan arsitektur tersentralisasi di mana **semua state, rahasia, dan virtual environment** secara eksklusif dikelola di dalam direktori profil Linux Anda.
- **`~/.jarvish/venv/`** — Tempat instalasi *virtual environment* ultra-cepat menggunakan `uv`.
- **`~/.jarvish/data/`** — Tempat penyimpanan memori AI (SQLite), riwayat obrolan, dan token OAuth Google.
- **`~/.jarvish/.env`** — File konfigurasi rahasia (Token Telegram, Kunci API, dll.) yang 100% aman dan tidak akan pernah ter-*commit* ke Git.

Hanya satu tautan perintah global (`jarvish`) yang diizinkan keluar menuju `/usr/local/bin/jarvish`, memastikan sistem VPS Anda tetap perawan dan tidak tercemar oleh pustaka acak.

---

## 🚀 Instalasi Cepat di VPS/Server (Linux)

Untuk menginstal J.A.R.V.I.S dan mendaftarkannya sebagai *Background Service* otomatis di Linux (Ubuntu/Debian):

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/yayangkasep/jarvish.git
   cd jarvish
   ```

2. **Jalankan Instalator Otomatis:**
   ```bash
   sudo bash install.sh
   ```

*Skrip ini akan menginstal `uv`, membuat environment, menautkan perintah global, dan menyalakan servis `jarvish.service`.*

---

## ⚙️ Perintah Operasional (CLI)

Setelah diinstal, Anda dapat mengelola J.A.R.V.I.S dari mana saja di terminal Anda menggunakan perintah global `jarvish`:

- **Konfigurasi Token (Telegram, API Z.ai, dsb):**
  ```bash
  jarvish configure
  ```
- **Memperbarui Kode dari GitHub & Restart Otomatis:**
  *(Jika ada rilis fitur baru, cukup ketik ini)*
  ```bash
  jarvish upgrade
  ```
- **Mengecek Status AI (Service):**
  ```bash
  sudo systemctl status jarvish.service
  ```
- **Melihat Log Percakapan secara Real-time:**
  ```bash
  sudo journalctl -u jarvish.service -f
  ```

---

## 💻 Instalasi Manual (Windows / Local)

Jika Anda ingin ikut mengembangkan proyek ini di Windows:

1. **Clone Repositori & Masuk ke Folder:**
   ```powershell
   git clone https://github.com/yayangkasep/jarvish.git
   cd jarvish-google
   ```

2. **Gunakan `uv` untuk Sinkronisasi Cepat (Direkomendasikan):**
   ```powershell
   uv venv
   uv pip install -e .
   ```

3. **Jalankan Bot secara Manual:**
   ```powershell
   # Melalui CLI entry point:
   jarvish-server
   
   # Atau langsung menggunakan Python:
   python src/main.py
   ```
*(Semua data lokal di Windows Anda akan aman tersimpan di `C:\Users\NamaUser\.jarvish\`)*
