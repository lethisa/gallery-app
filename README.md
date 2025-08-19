# Flask MinIO Image Gallery

[![Build, Deploy & Release Chart](https://github.com/lethisa/gallery-app/actions/workflows/build-push-deploy.yml/badge.svg)](https://github.com/lethisa/gallery-app/actions/workflows/build-push-deploy.yml)

Aplikasi web sederhana berbasis **Flask** untuk **upload** dan **menampilkan** gambar yang disimpan di **MinIO Object Storage**.

## Fitur
- Upload banyak gambar sekaligus (multi-upload)
- Validasi ekstensi gambar (PNG, JPG, JPEG, GIF, WEBP)
- Menyimpan objek di bucket MinIO
- Menampilkan galeri dengan presigned URL (berlaku 7 hari; sesuaikan bila perlu)
- Auto-create bucket jika belum ada

## Struktur Proyek
```
flask-minio-gallery/
├── app.py
├── config.ini.example
├── requirements.txt
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    └── style.css
```

## Konfigurasi
1. Salin berkas contoh konfigurasi:
   ```bash
   cp config.ini.example config.ini
   ```
2. Edit `config.ini` dan isi:
   - `ENDPOINT`  : host:port MinIO (tanpa http/https)
   - `ACCESS_KEY`: access key
   - `SECRET_KEY`: secret key
   - `BUCKET`    : nama bucket (akan dibuat otomatis jika belum ada)
   - `SECURE`    : `true` jika MinIO diakses via HTTPS, `false` jika HTTP

> Anda juga dapat mengubah lokasi berkas konfigurasi dengan environment variable:
> `CONFIG_PATH=/path/ke/config.ini`

## Menjalankan Secara Lokal
1. Buat dan aktifkan virtual env (opsional tapi dianjurkan)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python app.py
   ```
   Aplikasi default di `http://127.0.0.1:5000`

## Catatan
- Pastikan MinIO dapat diakses dari browser jika menggunakan **presigned URL** (alamat `ENDPOINT` harus terlihat dari sisi klien).
- Untuk lingkungan produksi, jalankan Flask di balik WSGI server (gunicorn/uwsgi) + reverse proxy (nginx) sesuai best practice.
- Batas ukuran unggahan default 32MB per file. Ubah di `app.config["MAX_CONTENT_LENGTH"]`.

## Troubleshooting
- **Permission denied / Access denied**: cek kredensial dan kebijakan bucket (walaupun presigned URL umumnya tidak perlu kebijakan publik).
- **Gagal resolusi host atau koneksi**: pastikan `ENDPOINT` benar dan jalur jaringan (firewall/proxy) mengizinkan.
- **Gambar tidak muncul**: Coba perbesar durasi presigned URL (aturnya di `timedelta(days=...)` pada `index()`).

## Helm Chart Install
- **Cara Install dengan Helm Charts**

```helm
helm upgrade --install <name> ./charts \
  -n <namespace> --create-namespace \
  --set image.repository=<image> \
  --set image.tag=<tag> \
  --set ingress.hosts[0].host=<dns> \
  --set ingress.hosts[0].paths[0].path="/" \
  --set ingress.hosts[0].paths[0].pathType="Prefix" \
  --set serviceAccount.name=<service account> \
  --set vaultInjector.role=<role> \
  --set vaultInjector.authPath=<auth path> \
  --set vaultInjector.serviceURL=<vault address> \
  --set vaultInjector.secretMount=<secret mount> \
  --set vaultInjector.secretPath=<secret path>
```

Selamat mencoba! kawan 🎉