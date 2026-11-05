[English](README.md) | [Bahasa Indonesia](README_ID.md)

---

# cOCR Workbench

Aplikasi desktop dan baris perintah (CLI) untuk mengekstrak teks dari gambar dokumen (soal ujian, lembar kerja, naskah pindaian buku, materi presentasi, dan tangkapan layar kuis) ke dalam format Microsoft Word (.docx), PDF (.pdf), atau Markdown (.md).

Seluruh pemrosesan berjalan luring (offline) di komputer lokal menggunakan runtime ONNX. Berkas gambar maupun teks hasil ekstraksi tidak dikirim ke server luar atau layanan komputasi awan.

---

## Daftar Isi

1. [Pilih Jalur Penggunaan](#pilih-jalur-penggunaan)
2. [Panduan Pengguna Non-Developer (Aplikasi Desktop)](#panduan-pengguna-non-developer-aplikasi-desktop)
   - [Cara Membuka Aplikasi](#1-cara-membuka-aplikasi)
   - [Langkah Ekstraksi Dokumen](#2-langkah-ekstraksi-dokumen)
   - [Panduan Memilih Mode Dokumen](#3-panduan-memilih-mode-dokumen)
   - [Menemukan Berkas Hasil Ekstraksi](#4-menemukan-berkas-hasil-ekstraksi)
3. [Panduan Pengembang: Instalasi dan Menjalankan dari Kode Sumber](#panduan-pengembang-instalasi-dan-menjalankan-dari-kode-sumber)
   - [Kebutuhan Sistem](#kebutuhan-sistem)
   - [Instalasi via Pip](#opsi-a-instalasi-standar-pip)
   - [Instalasi via uv](#opsi-b-instalasi-cepat-uv)
   - [Akselerasi GPU (NVIDIA CUDA dan DirectML)](#akselerasi-gpu-opsional)
   - [Menjalankan GUI Pengembang](#menjalankan-gui-pengembang)
4. [Panduan Lengkap Baris Perintah (CLI)](#panduan-lengkap-baris-perintah-cli)
   - [Sintaks dan Contoh Perintah](#sintaks-dan-contoh-perintah)
   - [Tabel Parameter CLI](#tabel-parameter-cli)
   - [Alur Kerja Otomasi dan Batch Script](#alur-kerja-otomasi-dan-batch-script)
5. [Panduan Kompilasi Executable Mandiri (Build)](#panduan-kompilasi-executable-mandiri-build)
   - [Pilihan Arsitektur Build (onedir vs onefile)](#pilihan-arsitektur-build)
   - [Build di Windows](#1-build-di-windows)
   - [Build di Linux](#2-build-di-linux)
   - [Build di macOS](#3-build-di-macos)
   - [Build Linux Menggunakan Docker](#4-build-linux-dari-windows-menggunakan-docker)
   - [Otomasi Rilis GitHub Actions](#5-otomasi-rilis-github-actions)
6. [Kustomisasi dan Konfigurasi Lanjutan](#kustomisasi-dan-konfigurasi-lanjutan)
   - [Penyaringan Watermark (watermarks.json)](#penyaringan-watermark-watermarksjson)
   - [Konfigurasi Server dan Keamanan (.env)](#konfigurasi-server-dan-keamanan-env)
7. [Logika Pembersihan dan Pengolahan OCR](#logika-pembersihan-dan-pengolahan-ocr)
8. [Tanya Jawab dan Solusi Masalah (Troubleshooting)](#tanya-jawab-dan-solusi-masalah-troubleshooting)
9. [Struktur Proyek](#struktur-proyek)
10. [Lisensi](#lisensi)

---

## Pilih Jalur Penggunaan

Tentukan cara penggunaan yang paling sesuai dengan kebutuhan Anda:

- **Pengguna Non-Developer**: Anda tidak perlu memasang Python, tidak perlu membuka terminal, dan tidak perlu memahami pemrograman. Cukup unduh paket aplikasi siap pakai atau jalankan pintasan berkas `.bat`, lalu gunakan antarmuka visual desktop. Lanjut ke [Panduan Pengguna Non-Developer](#panduan-pengguna-non-developer-aplikasi-desktop).
- **Pengembang / Teknis**: Anda ingin menjalankan aplikasi dari repositori Git, mengintegrasikan CLI ke skrip Python/bash, mengaktifkan akselerasi GPU CUDA/DirectML, atau mengompilasi biner executable sendiri. Lanjut ke [Panduan Pengembang](#panduan-pengembang-instalasi-dan-menjalankan-dari-kode-sumber).

---

## Panduan Pengguna Non-Developer (Aplikasi Desktop)

Panduan ini ditujukan bagi pengguna yang ingin mengekstrak dokumen naskah secara praktis melalui tampilan visual.

### 1. Cara Membuka Aplikasi

Pilih salah satu cara berikut sesuai paket yang Anda miliki di komputer:

#### Opsi 1: Menggunakan Berkas Aplikasi Siap Pakai (Rilis Executable)
1. Unduh arsip rilis (misalnya `cOCR_Workbench_Windows_x64.zip`) dari halaman rilis proyek.
2. Ekstrak arsip zip tersebut ke folder pilihan Anda di komputer (misalnya di `D:\cOCR`).
3. Buka folder hasil ekstrak, lalu klik ganda berkas **`cOCR.exe`** (pada Windows), **`cOCR Workbench.app`** (pada macOS), atau **`cOCR`** (pada Linux).
4. Jendela aplikasi desktop cOCR Workbench akan langsung terbuka di layar komputer Anda.

> [!NOTE]
> Paket aplikasi macOS (`cOCR Workbench.app`) belum tersedia untuk diunduh karena masih dalam tahap pengujian (membutuhkan tester). Sementara itu, pengguna macOS dapat menjalankan cOCR dari kode sumber (lihat [Panduan Pengembang](#panduan-pengembang-instalasi-dan-menjalankan-dari-kode-sumber)).

#### Opsi 2: Menggunakan Repositori Lokal di Windows
Jika Anda memiliki salinan folder proyek ini di Windows:
1. Buka folder proyek cOCR.
2. Klik ganda berkas **`run_gui.bat`**.
3. Sistem akan otomatis menyiapkan lingkungan lokal dan membuka jendela aplikasi desktop.

> [!NOTE]
> Saat pertama kali dijalankan, sistem akan mengunduh model pembaca karakter ONNX RapidOCR berukuran ringan ke komputer Anda. Proses ini hanya terjadi satu kali dan setelahnya aplikasi berjalan sepenuhnya secara luring.

---

### 2. Langkah Ekstraksi Dokumen

Setelah jendela cOCR Workbench terbuka, ikuti lima langkah berikut:

```
[1. Pilih Gambar/Folder] -> [2. Pilih Mode Tata Letak] -> [3. Pilih Format] -> [4. Klik Mulai] -> [5. Unduh Hasil]
```

1. **Menentukan Sumber Gambar Dokumen**:
   - **Pilih Folder**: Gunakan opsi ini jika seluruh foto naskah sudah tersimpan rapi dalam satu folder di komputer Anda. Klik tombol **Pilih Folder**, lalu cari folder naskah Anda.
   - **Unggah / Tarik Berkas (Drag and Drop)**: Gunakan opsi ini jika Anda ingin memilih beberapa berkas foto secara fleksibel. Tarik berkas gambar dari File Explorer langsung ke kotak abu-abu di aplikasi, atau klik area tersebut untuk memilih berkas. Format yang didukung meliputi `.jpg`, `.jpeg`, `.png`, `.webp`, dan `.bmp`.
2. **Memilih Format Keluaran**:
   - Anda dapat mencentang salah satu atau beberapa format sekaligus:
     - **Word (.docx)**: Cocok jika naskah ingin diedit, dirapikan, atau ditambah catatan di Microsoft Word atau Google Docs.
     - **PDF (.pdf)**: Cocok jika naskah ingin langsung dicetak atau dibagikan dengan tata letak dokumen yang bersih.
     - **Markdown (.md)**: Format teks terstruktur yang ringan untuk catatan digital (Notion, Obsidian, atau dokumentasi teknis).
3. **Memilih Mode Tata Letak Dokumen**:
   - Sesuaikan dengan jenis naskah fisik yang sedang Anda proses (lihat panduan detail di bawah). Jika ragu, biarkan pada pilihan **Deteksi Otomatis**.
4. **Memilih Perangkat Komputasi**:
   - Biarkan pada opsi **CPU** untuk penggunaan standar di semua komputer.
   - Pilih **GPU** jika komputer Anda memiliki kartu grafis tambahan yang kompatibel untuk pemrosesan yang lebih cepat pada ratusan lembar foto.
5. **Memulai Proses dan Mengambil Hasil**:
   - Klik tombol biru **Mulai Ekstraksi Dokumen**.
   - Perhatikan bar kemajuan (progress bar) dan status gambar yang sedang diproses.
   - Setelah status menunjukkan 100% selesai, periksa hasil pada tab **Pratinjau Hasil** atau **Markdown Mentah**.
   - Klik tombol unduh dokumen (Word, PDF, atau Markdown) untuk menyimpan berkas jadi ke komputer Anda.

---

### 3. Panduan Memilih Mode Tata Letak

Pemilihan mode tata letak membantu mesin cOCR mengelompokkan teks sesuai struktur dokumen aslinya:

| Mode Dokumen | Nama di Aplikasi | Kapan Harus Memilih Mode Ini? |
| :--- | :--- | :--- |
| **`auto`** | Deteksi Otomatis | **Pilihan umum terbaik.** Pilih mode ini jika berkas gambar Anda bervariasi atau Anda belum yakin struktur naskahnya. Sistem akan menganalisis bentuk gambar secara mandiri. |
| **`document_mcq`** | Naskah Ujian & Pilihan Ganda | **Khusus lembar ujian sekolah, SBMPTN, atau bank soal.** Mengurutkan nomor soal (1, 2, 3...) dan merapikan butir opsi jawaban (A, B, C, D, E) agar tidak bercampur dengan teks narasi soal. |
| **`worksheet`** | Lembar Kerja Berseksi | **Untuk Lembar Kerja Siswa (LKS), modul praktikum, atau diktat belajar.** Membaca struktur dokumen yang terbagi menjadi penanda bagian (Bagian A, B, C), petunjuk pengerjaan tugas, dan daftar pertanyaan isian. |
| **`quiz`** | Tangkapan Layar Kuis Ponsel | **Khusus foto tangkapan layar (screenshot) vertikal dari aplikasi ponsel edukasi atau kuis.** Memisahkan bagian atas (kartu pertanyaan) dan bagian bawah (pilihan jawaban) secara teratur. |
| **`full`** | Dokumen Bebas & Teks Penuh | **Untuk halaman buku bacaan, artikel, pindaian makalah, surat, atau materi slide.** Menyusun seluruh baris teks secara berurutan dari atas ke bawah tanpa membedah nomor soal ujian. |

---

### 4. Menemukan Berkas Hasil Ekstraksi

Selain melalui tombol unduh pada antarmuka aplikasi, berkas hasil pemrosesan otomatis tersimpan di media penyimpanan komputer:

- **Jika menggunakan mode Pilih Folder**: Berkas hasil disimpan di dalam subfolder bernama `output` tepat di dalam folder gambar yang Anda pilih (contoh: `D:\Naskah_Scan\output\hasil_ekstraksi_dokumen.docx`).
- **Jika menggunakan mode Unggah / Drag and Drop**: Berkas hasil disimpan di dalam folder kerja `outputs/` yang berada di samping berkas aplikasi `cOCR.exe`.

---

## Panduan Pengembang: Instalasi dan Menjalankan dari Kode Sumber

Bagian ini ditujukan bagi pengembang perangkat lunak, data engineer, atau pengguna teknis yang ingin menjalankan proyek cOCR Workbench dari lingkungan Python lokal.

### Kebutuhan Sistem

- **Python**: Versi 3.9, 3.10, 3.11, atau 3.12 (disarankan Python 3.10 atau 3.11).
- **Sistem Operasi**: Windows 10/11 (x64), Linux (Ubuntu, Debian, Fedora, Arch), atau macOS (Intel dan Apple Silicon).
- **Memori RAM**: Minimal 4 GB (disarankan 8 GB ke atas untuk pemrosesan gambar beresolusi tinggi).
- **Ruang Disk**: Sekitar 500 MB untuk dependensi dan berkas model bobot ONNX.

---

### Opsi A: Instalasi Standar (Pip)

1. Kloning repositori atau buka direktori kerja proyek di terminal:
   ```bash
   cd e:\py\cocr
   ```

2. Buat dan aktifkan virtual environment agar paket dependensi terisolasi rapi:
   ```bash
   # Di Windows (Command Prompt atau PowerShell)
   python -m venv .venv
   .venv\Scripts\activate

   # Di Linux atau macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Pasang seluruh dependensi pustaka:
   ```bash
   pip install -r requirements.txt
   ```

---

### Opsi B: Instalasi Cepat (uv)

Jika Anda menggunakan package manager Python modern `uv`:

1. Buat virtual environment dan pasang dependensi sekaligus:
   ```bash
   uv venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate # Linux/macOS
   uv pip install -r requirements.txt
   ```

2. Jalankan aplikasi langsung melalui perintah `uv run`:
   ```bash
   uv run python main.py
   ```

---

### Akselerasi GPU (Opsional)

Secara bawaan, pemrosesan OCR berjalan menggunakan CPU multi-threading berkecepatan tinggi. Jika komputer Anda memiliki kartu grafis dan Anda ingin memproses ribuan halaman dokumen dalam waktu singkat, pasang runtime GPU tambahan:

#### 1. Kartu Grafis NVIDIA (CUDA)
Dapat digunakan di Windows maupun Linux dengan GPU NVIDIA dan driver CUDA terkini:
```bash
pip install onnxruntime-gpu
# atau via uv:
uv pip install onnxruntime-gpu
```

#### 2. Universal Windows via DirectML (AMD Radeon, Intel Arc / Iris Xe, dan NVIDIA)
Sangat ideal untuk pengguna Windows dengan kartu grafis non-NVIDIA (misalnya AMD atau GPU terintegrasi Intel):
```bash
pip install onnxruntime-directml
# atau via uv:
uv pip install onnxruntime-directml
```

> [!TIP]
> Anda tidak perlu mengubah konfigurasi kode. Saat opsi `-d gpu` dipanggil, cOCR mendeteksi ketersediaan runtime GPU tersebut secara otomatis. Jika pustaka GPU belum terpasang atau perangkat tidak mendukung, sistem otomatis beralih kembali ke CPU tanpa menyebabkan aplikasi berhenti (crash).

---

### Menjalankan GUI Pengembang

Pilihan cara menjalankan antarmuka desktop berbasis Python:

1. **Jendela Desktop Bawaan (Default)**:
   Membuka antarmuka grafis dalam jendela aplikasi desktop mandiri menggunakan WebKit/Edge WebView2 via `pywebview`:
   ```bash
   python main.py
   # atau
   python main.py --gui
   ```

2. **Membuka di Peramban Web Eksternal**:
   Jika Anda lebih nyaman menggunakan tab Google Chrome, Microsoft Edge, atau Mozilla Firefox:
   ```bash
   python main.py --browser
   ```
   Aplikasi akan otomatis meluncurkan peramban dan mengarah ke alamat `http://127.0.0.1:8765`.

3. **Mode Server Latar Belakang (Headless)**:
   Berguna jika Anda menaruh cOCR di server lokal atau kontainer dan hanya ingin menyediakan antarmuka web tanpa memunculkan jendela apa pun:
   ```bash
   python main.py --headless --host 0.0.0.0 --port 8765
   ```

---

## Panduan Lengkap Baris Perintah (CLI)

Mode CLI memungkinkan pemrosesan dokumen secara instan tanpa perlu memuat antarmuka grafis. Sangat tepat digunakan untuk skrip otomasi harian, pemrosesan folder otomatis, maupun integrasi ke dalam sistem lain.

### Sintaks dan Contoh Perintah

Format dasar perintah CLI:
```bash
python main.py --cli -i <FOLDER_GAMBAR> [OPSI_LAINNYA]
```

Berikut beberapa contoh skenario penggunaan praktis:

#### Contoh 1: Ekstraksi Folder dengan Deteksi Otomatis ke Semua Format (MD, Word, PDF)
Memindai seluruh foto di folder `samples` dan mengekspor hasilnya ke subfolder `output`:
```bash
python main.py --cli -i samples -o output -f all -m auto
```

#### Contoh 2: Ekstraksi Naskah Ujian Soal Pilihan Ganda ke Berkas Word (.docx)
Mengekstrak naskah soal ujian dengan tata letak pilihan ganda bernomor dan menyimpannya sebagai berkas Word:
```bash
python main.py --cli -i "D:\Koleksi_Ujian\Soal_Matematika" -f docx -m document_mcq
```

#### Contoh 3: Ekstraksi Buku / Makalah ke Format Markdown (.md)
Memproses pindaian buku atau catatan panjang menjadi dokumen Markdown bersih untuk aplikasi catatan:
```bash
python main.py --cli -i "D:\Buku_Scan\Bab_1" -f md -m full
```

#### Contoh 4: Ekstraksi Tangkapan Layar Kuis Ponsel Menggunakan Akselerasi GPU
Memproses gambar kuis vertikal secara cepat menggunakan kartu grafis:
```bash
python main.py --cli -i "D:\Screenshot_Kuis" -f all -d gpu -m quiz
```

#### Contoh 5: Menjalankan CLI Menggunakan Executable Mandiri (cOCR.exe)
Jika Anda menggunakan paket biner hasil build tanpa Python:
```powershell
.\cOCR.exe --cli -i "C:\Users\Nama\Documents\Naskah" -f docx -m auto
```

---

### Tabel Parameter CLI

| Parameter | Alias | Pilihan Nilai | Nilai Bawaan | Penjelasan Fungsi |
| :--- | :--- | :--- | :--- | :--- |
| `--input-dir` | `-i` | Path folder | *(Wajib)* | Lokasi folder di komputer yang berisi kumpulan gambar dokumen (.jpg, .jpeg, .png, .webp, .bmp). |
| `--output-dir` | `-o` | Path folder | `<input-dir>/output` | Folder tujuan penyimpanan dokumen hasil ekstraksi. Jika belum ada, folder akan dibuat secara otomatis. |
| `--format` | `-f` | `md`, `docx`, `pdf`, `all` | `all` | Format berkas keluaran yang dihasilkan. Pilih `all` untuk membuat ketiga jenis berkas sekaligus. |
| `--device` | `-d` | `cpu`, `gpu` | `cpu` | Perangkat komputasi OCR yang digunakan. |
| `--mode` | `-m` | `auto`, `quiz`, `document_mcq`, `worksheet`, `full` | `auto` | Algoritma segmentasi tata letak naskah yang diterapkan pada gambar. |
| `--cli` | | Flag | | Menegaskan eksekusi mode terminal tanpa meluncurkan server atau jendela antarmuka visual. |
| `--gui` | | Flag | | Membuka antarmuka jendela desktop (berlaku saat tidak ada opsi `-i`). |
| `--browser` | | Flag | | Membuka antarmuka web di peramban eksternal bawaan sistem operasi. |
| `--headless` | | Flag | | Menjalankan server web cOCR di latar belakang tanpa memunculkan jendela apa pun. |
| `--host` | | IP Address | `127.0.0.1` | Alamat host server web antarmuka. |
| `--port` | | Angka Port | `8765` | Nomor port jaringan yang digunakan oleh server antarmuka. |

---

### Alur Kerja Otomasi dan Batch Script

Saat CLI dijalankan, terminal akan menampilkan progres pemrosesan secara langsung:

```text
cOCR Workbench
Perangkat : CPU Multi-threading
Format    : Markdown (.md), Word (.docx), PDF (.pdf)

Memulai inisialisasi mesin OCR (CPU)...
Mesin siap berjalan menggunakan: CPU
Ditemukan 12 berkas gambar untuk diproses.
Mode Segmentasi : auto
Direktori Output: D:\Dokumen\output

[========================] 100% | Pemrosesan selesai.

Ekstraksi selesai dalam 8.45 detik.
- Total berkas dipindai: 12
- Berkas unik diproses : 12
- Berkas duplikat lewati: 0

Berkas keluaran berhasil dibuat:
  -> D:\Dokumen\output\hasil_ekstraksi_dokumen.md (14.2 KB)
  -> D:\Dokumen\output\hasil_ekstraksi_dokumen.docx (28.7 KB)
  -> D:\Dokumen\output\hasil_ekstraksi_dokumen.pdf (45.1 KB)

Selesai.
```

Anda dapat menyematkan perintah ini ke dalam skrip batch Windows (`.bat`), skrip PowerShell (`.ps1`), atau skrip Bash Linux untuk memproses naskah harian secara otomatis.

---

## Panduan Kompilasi Executable Mandiri (Build)

Proyek ini dilengkapi alat pembangun PyInstaller terintegrasi untuk mengompilasi kode sumber Python menjadi aplikasi biner mandiri yang dapat langsung didistribusikan ke komputer lain tanpa memerlukan instalasi Python.

### Pilihan Arsitektur Build

Skrip builder menyediakan dua opsi arsitektur paket:

1. **`--mode onedir` (Sangat Disarankan)**:
   - Menghasilkan satu folder mandiri bernama `cOCR_Workbench/` yang berisi berkas eksekusi utama dan dependensi pendukung di sampingnya.
   - **Kelebihan**: Aplikasi terbuka secara instan (startup cepat) karena sistem tidak perlu mengekstrak ratusan megabita pustaka ke folder temporary setiap kali aplikasi diklik.
2. **`--mode onefile`**:
   - Menghasilkan satu berkas biner tunggal (misal `cOCR.exe`).
   - Setiap kali dijalankan, sistem operasi akan mengekstrak runtime ke `%TEMP%` terlebih dahulu sebelum jendela terbuka.

---

### 1. Build di Windows

Pastikan dependensi build telah terpasang:
```powershell
pip install pyinstaller pywebview
```

Jalankan salah satu cara berikut:

- **Cara Praktis**: Klik ganda berkas **`build.bat`** di direktori proyek.
- **Cara Baris Perintah**:
  ```powershell
  python build_exe.py --mode onedir
  ```

Parameter tambahan yang dapat digunakan:
- `--clean`: Menghapus folder `build/` dan `dist/` lama sebelum mulai mengompilasi ulang.
- `--console`: Membiarkan jendela konsol hitam tetap muncul saat aplikasi dijalankan (berguna untuk melihat log saat melakukan debugging).

Hasil kompilasi akan tersimpan di dalam direktori **`dist/cOCR_Workbench/`** dengan berkas utama **`cOCR.exe`**.

---

### 2. Build di Linux (Ubuntu / Debian / Linux Mint / Fedora)

Di sistem operasi Linux, antarmuka grafis desktop terintegrasi memerlukan pustaka sistem WebKitGTK.

1. Pasang paket WebKitGTK pada sistem Linux Anda:
   ```bash
   # Di Debian, Ubuntu, atau Linux Mint:
   sudo apt-get update
   sudo apt-get install -y libwebkit2gtk-4.1-dev gir1.2-webkit2-4.1

   # Di Fedora atau Red Hat Enterprise Linux:
   sudo dnf install webkit2gtk4.1-devel
   ```

2. Jalankan skrip pembangun:
   ```bash
   chmod +x build.sh
   ./build.sh --mode onedir
   ```

Hasil kompilasi akan tersimpan di **`dist/cOCR_Workbench/cOCR`**.

---

### 3. Build di macOS (Apple Silicon M-Series dan Intel)

> [!WARNING]
> Build macOS **belum tersedia** di halaman rilis karena masih dalam tahap pengujian. Kami membutuhkan tester macOS (Intel maupun Apple Silicon). Jika Anda bersedia membantu, silakan build dari kode sumber dengan langkah di bawah ini dan laporkan masalah yang ditemukan.

macOS telah menyertakan mesin WebKit Cocoa bawaan secara langsung dari sistem operasi:

1. Jalankan skrip pembangun:
   ```bash
   chmod +x build.sh
   ./build.sh --mode onedir
   ```

2. Hasil kompilasi akan menghasilkan berkas bundle aplikasi **`dist/cOCR Workbench.app`** yang dapat langsung dipindahkan ke folder `/Applications`.

---

### 4. Build Linux dari Windows Menggunakan Docker

Jika Anda bekerja di komputer Windows dan ingin membuat berkas biner Linux tanpa memerlukan mesin virtual terpisah, gunakan kontainer Docker yang telah disediakan:

```powershell
docker build -t cocr-linux-builder -f build_tools/Dockerfile.build .
docker run --rm -v ${PWD}/dist_linux:/output cocr-linux-builder
```
Hasil kompilasi biner Linux akan langsung tersimpan di folder `dist_linux/`.

---

### 5. Otomasi Rilis GitHub Actions

Alur kerja integrasi berkelanjutan (CI/CD) tersedia pada berkas [`.github/workflows/build.yml`](.github/workflows/build.yml).

Setiap kali Anda membuat tag rilis Git (misalnya `v1.2.0`) dan mendorongnya ke repositori GitHub:
```bash
git tag v1.2.0
git push origin v1.2.0
```

Anda juga dapat mempublikasikan rilis secara manual: jalankan workflow dari tab **Actions** (Run workflow) dan isi input `release_tag` (misalnya `v1.2.0`). Build yang dijalankan tanpa tag dan tanpa `release_tag` hanya menghasilkan arsip di halaman run workflow, tanpa membuat GitHub Release.
Server GitHub Actions akan secara otomatis:
1. Membangun berkas executable untuk Windows x64 dan Linux x64. Target macOS (ARM64/Apple Silicon dan Intel) dinonaktifkan sementara selama build macOS masih dalam tahap pengujian — lihat [Build di macOS](#3-build-di-macos).
2. Memaketkannya menjadi arsip `.zip` dan `.tar.gz`.
3. Memublikasikan arsip biner siap unduh langsung ke halaman rilis repositori (GitHub Releases).

---

## Kustomisasi dan Konfigurasi Lanjutan

### Penyaringan Watermark (watermarks.json)

Sering kali dokumen naskah ujian atau modul pindaian memuat teks promosi bimbingan belajar, watermark diagonal, tautan situs web, atau nomor kontak yang mengganggu keterbacaan naskah utama.

cOCR Workbench menyediakan penyaring teks berbasis pola ekspresi reguler (regex) melalui berkas **`watermarks.json`** pada direktori utama.

Cara mengonfigurasi:
1. Salin berkas contoh `watermarks.example.json` menjadi `watermarks.json`.
2. Masukkan daftar kata kunci atau pola regex yang ingin disaring:
   ```json
   [
     "bimbingan_belajar_xyz",
     "koleksi_pribadi",
     "\\.com",
     "\\.id",
     "whatsapp",
     "dilarang memperbanyak",
     "^halaman\\s+\\d+"
   ]
   ```
3. Simpan berkas. Setiap teks yang cocok dengan salah satu pola di atas akan otomatis dibersihkan dari dokumen hasil akhir.

> [!NOTE]
> Berkas `watermarks.json` sudah tercantum di dalam `.gitignore`, sehingga konfigurasi kata kunci internal Anda tidak akan terunggah secara tidak sengaja ke repositori publik.

---

### Konfigurasi Server dan Keamanan (.env)

cOCR Workbench dapat dikonfigurasi menggunakan variabel lingkungan melalui berkas `.env` (template tersedia di `.env.example`). Hal ini sangat berguna jika Anda menjalankan aplikasi ini di jaringan intranet sekolah, kampus, atau kantor:

| Variabel | Nilai Default | Penjelasan |
| :--- | :--- | :--- |
| `COCR_HOST` | `127.0.0.1` | Alamat IP binding server. Atur ke `0.0.0.0` jika aplikasi ingin diakses oleh komputer lain dalam satu jaringan lokal. |
| `COCR_PORT` | `8765` | Nomor port jaringan untuk antarmuka web. |
| `COCR_ALLOWED_ORIGINS` | `http://localhost:8765,...` | Daftar domain asal (CORS) yang diizinkan mengakses antarmuka API. |
| `COCR_CLOUD_MODE` | `0` | Jika diatur ke `1` atau `true`, sistem beralih ke mode sandbox server murni. Tombol pemilihan folder lokal di server akan dinonaktifkan, sehingga klien hanya dapat memproses berkas yang diunggah secara sah ke ruang sesi mereka sendiri. |
| `COCR_API_KEY` | *(Kosong)* | Kunci rahasia autentikasi. Jika diisi, setiap permintaan ke server wajib menyertakan header `X-API-Key` atau `Authorization: Bearer <key>`. |

Mekanisme perlindungan bawaan yang aktif:
- **Isolasi Sesi Pengguna**: Berkas unggahan dan dokumen hasil dipisahkan ke dalam direktori sandbox sesi masing-masing (`temp_uploads/<session_id>` dan `outputs/<session_id>`).
- **Validasi Jalur Berkas (Path Traversal Protection)**: Mencegah pembacaan direktori sensitif sistem (misalnya folder `C:\Windows`, `/etc`, atau kunci otentikasi `.ssh`).
- **Batas Beban Gambar**: Membatasi ukuran berkas maksimal 100 MB per batch, resolusi maksimum 8192x8192 piksel, serta batas 25 megapiksel per gambar guna mencegah lonjakan memori tak terduga.
- **Header Keamanan**: Menyertakan header standar industri seperti `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, dan `X-Frame-Options: DENY`.

---

## Logika Pembersihan dan Pengolahan OCR

cOCR Workbench mengimplementasikan serangkaian algoritma terstruktur untuk memastikan teks hasil ekstraksi tetap rapi:

1. **Penyaringan Watermark Sudut Miring**: Kotak teks yang memiliki kemiringan kontur di atas 16 derajat otomatis diabaikan, sehingga cap naskah diagonal tidak merusak kalimat soal utama.
2. **Pembersihan Elemen Layar Ponsel**: Memotong bilah status atas (indikator baterai, sinyal, jam), tombol navigasi bawah, serta nomor paginasi aplikasi kuis secara otomatis.
3. **Pengurutan Baris Baca Berkelompok**: Menyortir blok teks dari atas ke bawah dan menggabungkan teks sebaris secara horizontal dengan menghitung ambang batas tinggi huruf secara adaptif.
4. **Pendeteksian Nomor Halaman Otomatis**: Membaca penanda format halaman (seperti `Halaman 12 dari 40` atau `12/40`) untuk menyusun urutan bab naskah secara kronologis meskipun berkas gambar tidak berurutan nama filenya.
5. **Deduplikasi Berkas Kembar**: Menggunakan komputasi checksum MD5 untuk mengenali dan melewati gambar duplikat yang tidak sengaja terunggah dua kali.
6. **Sanitasi Format Dokumen**: Mengamankan karakter reserved XML/HTML (`<`, `>`, `&`) agar pembuatan dokumen Word dan PDF melalui ReportLab tidak mengalami galat parsing.

---

## Tanya Jawab dan Solusi Masalah (Troubleshooting)

### 1. Windows SmartScreen menampilkan peringatan saat `cOCR.exe` dibuka
- **Penyebab**: Berkas biner baru dikompilasi secara lokal dan belum ditandatangani sertifikat digital berbayar (EV Code Signing Certificate).
- **Solusi**: Klik tautan **More info** (Informasi selengkapnya) pada jendela peringatan biru Windows, lalu klik tombol **Run anyway** (Tetap jalankan). Aplikasi aman dijalankan karena 100% luring.

### 2. Port 8765 sedang digunakan oleh aplikasi lain
- **Solusi**: cOCR Workbench memiliki logika penanganan port otomatis. Jika port 8765 sedang terpakai, sistem akan secara mandiri mencoba port berikutnya (8766, 8767, dst). Jika Anda ingin menentukan port tertentu secara manual, tambahkan parameter `--port <nomor_port>` saat menjalankan perintah.

### 3. Akselerasi GPU tidak terdeteksi padahal komputer memiliki kartu grafis NVIDIA
- **Solusi**: Pastikan Anda telah memasang pustaka runtime yang sesuai di lingkungan Python Anda (`pip install onnxruntime-gpu`) dan driver kartu grafis telah diperbarui. Jika pustaka ini belum tersedia, sistem akan tetap memproses dokumen dengan aman menggunakan CPU.

### 4. Di Linux, jendela desktop tidak muncul saat mengetik `python main.py`
- **Solusi**: Pastikan paket WebKitGTK terpasang di sistem Linux Anda (`sudo apt-get install libwebkit2gtk-4.1-dev gir1.2-webkit2-4.1`). Sebagai alternatif cepat tanpa memasang paket sistem tambahan, jalankan dengan opsi peramban web: `python main.py --browser`.

### 5. Sebagian teks atau nomor soal ujian bertukar posisi
- **Solusi**: Jika Anda memproses naskah soal ujian dengan opsi `auto` dan urutan opsi kurang pas, alihkan pilihan mode tata letak ke **`document_mcq`** (Naskah Ujian & Pilihan Ganda). Mode ini memiliki aturan pengelompokan khusus untuk nomor soal dan butir opsi jawaban (A, B, C, D, E).

---

## Struktur Proyek

```
cocr/
├── assets/                       # Aset ikon dan logo aplikasi (.ico dan .png)
│   ├── cocr.ico                  # Ikon aplikasi format Windows ICO
│   └── cocr.png                  # Ikon aplikasi format PNG
│
├── src/                          # Kode sumber inti paket cOCR
│   └── cocr/
│       ├── __init__.py           # Inisialisasi modul paket
│       ├── engine.py             # Mesin OCR, segmentasi tata letak, dan filter teks
│       ├── server.py             # Server FastAPI dan manajemen jendela aplikasi webview
│       ├── cli.py                # Penanganan antarmuka baris perintah (CLI)
│       ├── i18n.py               # Kamus lokalisasi & pembantu internasionalisasi CLI
│       └── exporters.py          # Modul generator dokumen (Markdown, DOCX, dan PDF)
│
├── web/                          # Antarmuka web frontend desktop
│   ├── index.html                # Struktur halaman visual
│   ├── style.css                 # Penataan gaya antarmuka
│   ├── app.js                    # Logika interaksi frontend dan pemantauan progres
│   ├── i18n.js                   # Mesin internasionalisasi (i18n) ringan
│   └── locales/                  # Berkas kamus multibahasa antarmuka
│       ├── en.js                 # String lokalisasi Bahasa Inggris
│       ├── id.js                 # String lokalisasi Bahasa Indonesia
│       └── README.md             # Panduan lokalisasi & penambahan bahasa
│
├── build_tools/                  # Alat bantu kompilasi biner executable
│   ├── build_exe.py              # Skrip builder PyInstaller lintas sistem operasi
│   ├── cocr.spec                 # Berkas spesifikasi packaging PyInstaller
│   └── Dockerfile.build          # Kontainer Docker untuk build Linux dari Windows
│
├── scripts/                      # Skrip utilitas tambahan
│   └── scan_and_extract.py       # Skrip pengujian indeks ekstraksi lokal
│
├── samples/                      # Berkas gambar contoh untuk pengujian
├── .github/                      # Konfigurasi otomasi CI/CD
│   └── workflows/
│       └── build.yml             # Workflow kompilasi rilis multi-platform GitHub Actions
│
├── main.py                       # Titik masuk utama aplikasi (CLI dan GUI)
├── run_gui.bat                   # Pintasan peluncur GUI cepat di Windows
├── build.bat                     # Pintasan build executable mandiri di Windows
├── build.sh                      # Pintasan build executable mandiri di Linux/macOS
├── build_exe.py                  # Pintasan peluncur skrip build dari direktori root
├── requirements.txt              # Daftar pustaka dependensi Python
├── watermarks.example.json       # Template contoh konfigurasi penyaring watermark
├── .env.example                  # Template contoh konfigurasi variabel lingkungan
├── LICENSE                       # Lisensi berkas proyek
├── README.md                     # Dokumentasi panduan utama (Bahasa Inggris)
└── README_ID.md                  # Dokumentasi Bahasa Indonesia
```

---

## Lisensi

Proyek ini dilisensikan di bawah **GNU General Public License v3.0 (GPL-3.0)**.

Copyright © 2026 Dika Ardianta
Copyright © 2026 Hisoka Labs

Anda bebas menggunakan, mempelajari, memodifikasi, dan mendistribusikan ulang perangkat lunak ini, dengan syarat karya turunannya juga didistribusikan di bawah lisensi yang sama. Silakan lihat berkas [LICENSE](LICENSE) untuk teks lisensi lengkap.
