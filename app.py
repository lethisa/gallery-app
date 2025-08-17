import os
import io
import uuid
import mimetypes
from datetime import timedelta
from configparser import ConfigParser

from flask import Flask, render_template, request, redirect, url_for, flash
from minio import Minio
from minio.error import S3Error

# -------- Configuration --------
CONFIG_PATH = os.environ.get("CONFIG_PATH", "config.ini")

def load_config(path: str):
    parser = ConfigParser()
    read_files = parser.read(path)
    if not read_files:
        raise FileNotFoundError(f"Config file not found: {path}")
    if not parser.has_section("MINIO"):
        raise ValueError("Config file must contain a [MINIO] section")

    def as_bool(v: str) -> bool:
        return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}

    endpoint   = parser.get("MINIO", "ENDPOINT", fallback="127.0.0.1:9000")
    access_key = parser.get("MINIO", "ACCESS_KEY")
    secret_key = parser.get("MINIO", "SECRET_KEY")
    bucket     = parser.get("MINIO", "BUCKET", fallback="gallery")
    secure     = as_bool(parser.get("MINIO", "SECURE", fallback="false"))

    return {
        "endpoint": endpoint,
        "access_key": access_key,
        "secret_key": secret_key,
        "bucket": bucket,
        "secure": secure,
    }

cfg = load_config(CONFIG_PATH)

# Flask app
app = Flask(__name__)
# Limit uploads to 32 MB (adjust as needed)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024
# Optional secret key (needed only if you use flash/messages). Autogenerate if missing.
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# MinIO client
minio_client = Minio(
    cfg["endpoint"],
    access_key=cfg["access_key"],
    secret_key=cfg["secret_key"],
    secure=cfg["secure"],
)

# Ensure bucket exists
if not minio_client.bucket_exists(cfg["bucket"]):
    minio_client.make_bucket(cfg["bucket"])

# Allowed extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def guess_content_type(filename: str, fallback: str = "application/octet-stream") -> str:
    typ, _ = mimetypes.guess_type(filename)
    return typ or fallback

@app.route("/", methods=["GET"])
def index():
    # List all objects in the bucket and generate presigned URLs for display
    objects = list(minio_client.list_objects(cfg["bucket"], recursive=True))
    images = []
    for obj in objects:
        # Skip non-image objects (by simple extension check)
        if not any(obj.object_name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            continue
        url = minio_client.presigned_get_object(cfg["bucket"], obj.object_name, expires=timedelta(days=7))
        images.append({
            "name": obj.object_name,
            "url": url,
            "size": obj.size
        })
    images.sort(key=lambda x: x["name"])
    return render_template("index.html", images=images, bucket=cfg["bucket"])

@app.route("/upload", methods=["POST"])
def upload():
    # Support both single and multiple file inputs named "images"
    files = request.files.getlist("images")
    if not files:
        flash("Tidak ada file yang diunggah.", "error")
        return redirect(url_for("index"))

    uploaded = 0
    errors = []

    for file in files:
        if not file or not file.filename:
            continue
        filename = file.filename
        if not allowed_file(filename):
            errors.append(f"Format tidak didukung: {filename}")
            continue

        ext = os.path.splitext(filename)[1].lower()
        object_name = f"uploads/{uuid.uuid4().hex}{ext}"

        # Read file into memory to know content length (simple & safe for mid-sized images)
        data = file.read()
        length = len(data)
        if length == 0:
            errors.append(f"File kosong: {filename}")
            continue

        content_type = guess_content_type(filename, "application/octet-stream")
        try:
            minio_client.put_object(
                bucket_name=cfg["bucket"],
                object_name=object_name,
                data=io.BytesIO(data),
                length=length,
                content_type=content_type,
            )
            uploaded += 1
        except S3Error as e:
            errors.append(f"Gagal unggah {filename}: {str(e)}")

    if uploaded:
        flash(f"Berhasil mengunggah {uploaded} file.", "success")
    if errors:
        flash(" | ".join(errors), "error")

    return redirect(url_for("index"))

if __name__ == "__main__":
    # For development only; use a proper WSGI server in production
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)