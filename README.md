# Flask + MinIO Image Gallery

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
- Cara Install dengan Helm Charts

```helm
helm upgrade --install gallery ./charts \
  -n gallery-app --create-namespace \
  --set image.repository=lethisaputri/flask-minio-gallery \
  --set image.tag=v3.0.0 \
  --set ingress.hosts[0].host=sample.local \
  --set ingress.hosts[0].paths[0].path="/" \
  --set ingress.hosts[0].paths[0].pathType="Prefix" \
  --set serviceAccount.name=gallery-vault \
  --set vaultInjector.role=gallery \
  --set vaultInjector.authPath=auth/gallery-app-k8s \
  --set vaultInjector.serviceURL=http://192.168.1.19:8200 \
  --set vaultInjector.secretMount=gallery \
  --set vaultInjector.secretPath=minio/config
```

Selamat mencoba! 🎉