# backend/utils/image_utils.py

import base64
import io
from PIL import Image
import numpy as np
import cv2
from werkzeug.datastructures import FileStorage


def save_file_to_disk(file_storage: FileStorage, dest_path: str):
    """
    Save a Flask FileStorage object to disk.
    """
    file_storage.save(dest_path)


def pil_image_from_bytes(bts: bytes) -> Image.Image:
    """
    Convert raw bytes → PIL RGB image.
    """
    return Image.open(io.BytesIO(bts)).convert("RGB")


def base64_to_image(base64_str: str):
    """
    Convert base64 string → OpenCV BGR image (numpy array).
    Required for correct face_recognition encoding.
    """

    if not isinstance(base64_str, str):
        raise ValueError("base64_to_image expects a base64 string")

    # Remove data URL prefix if present (e.g. "data:image/png;base64,...")
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]

    # Decode base64 → raw bytes
    img_bytes = base64.b64decode(base64_str)

    # Convert bytes → numpy array
    np_arr = np.frombuffer(img_bytes, np.uint8)

    # Decode numpy → OpenCV BGR image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Failed to decode image from base64")

    return img
