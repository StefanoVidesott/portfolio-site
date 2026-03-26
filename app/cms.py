import os
import uuid

from fastapi import HTTPException

UPLOAD_DIR = os.path.join("app", "static", "images", "uploaded")
PDF_UPLOAD_DIR = os.path.join("app", "static", "docs", "uploaded")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_PDF_EXTENSION = {".pdf"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


def _is_valid_pdf(data: bytes) -> bool:
    """Check PDF magic bytes (%PDF-)."""
    return data[:5] == b"%PDF-"


def _is_allowed_image(data: bytes) -> bool:
    """Return True if the first bytes match a known safe image format.

    imghdr was removed in Python 3.13, so we check magic bytes directly.
    Recognised formats: JPEG, PNG, GIF87a, GIF89a, WebP.
    """
    if data[:3] == b"\xff\xd8\xff":                          # JPEG
        return True
    if data[:8] == b"\x89PNG\r\n\x1a\n":                    # PNG
        return True
    if data[:6] in (b"GIF87a", b"GIF89a"):                  # GIF
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":       # WebP
        return True
    return False


def generate_form_schema(model_class, instance=None) -> dict:
    schema: dict = {}

    for column in model_class.__table__.columns:
        if column.name == "id":
            continue

        info = column.info or {}
        group_name = info.get("group", "Altro")

        if group_name not in schema:
            schema[group_name] = []

        val: object = ""
        if instance and hasattr(instance, column.name):
            val = getattr(instance, column.name)
            if val is None:
                val = ""
        elif column.default is not None:
            val = column.default.arg if not callable(column.default.arg) else ""

        # A column is "required" only when it is non-nullable AND has no default —
        # columns with defaults (e.g. order=0, is_featured=False) don't need user input.
        required = not column.nullable and column.default is None

        schema[group_name].append({
            "name": column.name,
            "type": info.get("type", "text"),
            "required": required,
            "value": val,
            "size": info.get("size", "12" if info.get("type") == "textarea" else "6"),
        })

    return schema


def populate_instance_from_form(instance, model_class, form_data) -> None:
    for column in model_class.__table__.columns:
        if column.name == "id":
            continue

        # --- File upload (image or PDF) ---
        file_field_name = f"{column.name}_file"
        if file_field_name in form_data:
            uploaded_file = form_data[file_field_name]
            if hasattr(uploaded_file, "filename") and uploaded_file.filename:
                field_type = (column.info or {}).get("type", "")
                ext = os.path.splitext(uploaded_file.filename)[1].lower()

                contents = uploaded_file.file.read(MAX_UPLOAD_BYTES + 1)
                if len(contents) > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413, detail="File too large (max 5 MB)."
                    )

                if field_type == "pdf_upload":
                    if ext not in ALLOWED_PDF_EXTENSION:
                        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
                    if not _is_valid_pdf(contents):
                        raise HTTPException(status_code=400, detail="Invalid PDF content.")

                    old_val = getattr(instance, column.name, None)
                    if old_val and str(old_val).startswith("/static/docs/uploaded/"):
                        old_path = os.path.join("app", old_val.lstrip("/"))
                        if os.path.isfile(old_path):
                            os.remove(old_path)

                    unique_filename = f"{uuid.uuid4().hex}{ext}"
                    file_path = os.path.join(PDF_UPLOAD_DIR, unique_filename)
                    with open(file_path, "wb") as buffer:
                        buffer.write(contents)

                    setattr(instance, column.name, f"/static/docs/uploaded/{unique_filename}")
                else:
                    # image_upload
                    if ext not in ALLOWED_EXTENSIONS:
                        raise HTTPException(
                            status_code=400, detail=f"File type not allowed: {ext}"
                        )
                    if not _is_allowed_image(contents):
                        raise HTTPException(
                            status_code=400, detail="Invalid image content."
                        )

                    old_val = getattr(instance, column.name, None)
                    if old_val and str(old_val).startswith("/static/images/uploaded/"):
                        old_path = os.path.join("app", old_val.lstrip("/"))
                        if os.path.isfile(old_path):
                            os.remove(old_path)

                    unique_filename = f"{uuid.uuid4().hex}{ext}"
                    file_path = os.path.join(UPLOAD_DIR, unique_filename)
                    with open(file_path, "wb") as buffer:
                        buffer.write(contents)

                    setattr(instance, column.name, f"/static/images/uploaded/{unique_filename}")
                continue

        # --- Boolean ---
        if getattr(column.type, "python_type", None) is bool or str(column.type) == "BOOLEAN":
            val = form_data.get(column.name)
            setattr(instance, column.name, val in ["true", "on", "1"])
            continue

        # --- JSON (stored as list, edited as one-item-per-line textarea) ---
        if str(column.type) == "JSON":
            val = form_data.get(column.name, "")
            if val:
                lines = [line.strip() for line in val.split("\n") if line.strip()]
                setattr(instance, column.name, lines)
            else:
                setattr(instance, column.name, [])
            continue

        # --- Scalar fields ---
        if column.name in form_data:
            val = form_data.get(column.name)
            if val == "":
                if column.nullable:
                    setattr(instance, column.name, None)
                elif getattr(column.type, "python_type", None) is int:
                    setattr(instance, column.name, 0)
                else:
                    setattr(instance, column.name, "")
            else:
                # Coerce to the column's native Python type (handles int, float, etc.)
                col_python_type = getattr(column.type, "python_type", str)
                try:
                    setattr(instance, column.name, col_python_type(val))
                except (ValueError, TypeError):
                    setattr(instance, column.name, val)
