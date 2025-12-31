# backend/services/face_service.py

import face_recognition
import numpy as np
import hashlib
import cv2
from PIL import Image


class FaceService:
    """
    Handles all face encoding, comparison, and safety checks.
    Works with PIL Images, OpenCV frames, and FileStorage uploads.
    """

    # ------------------------------------------------------------
    # 1️⃣ ENCODE FROM FILE UPLOAD (FileStorage)
    # ------------------------------------------------------------
    def encode_from_image_file(self, file):
        """
        file: werkzeug FileStorage (image upload)
        """
        try:
            image = face_recognition.load_image_file(file)
            encs = face_recognition.face_encodings(image)
            if not encs:
                raise ValueError("No face detected in uploaded image")
            return encs[0]
        except Exception as e:
            raise ValueError(f"Image processing failed: {e}")

    # ------------------------------------------------------------
    # 2️⃣ ENCODE FROM PIL IMAGE
    # ------------------------------------------------------------
    def encode_from_pil_image(self, pil_img: Image.Image):
        """
        For frontend camera (base64 → PIL)
        Returns encoding OR None if no face detected
        """
        try:
            arr = np.array(pil_img)  # RGB
            locations = face_recognition.face_locations(arr, model="hog")
            if not locations:
                return None

            encs = face_recognition.face_encodings(arr, locations)
            if not encs:
                return None

            return encs[0]

        except Exception:
            return None

    # ------------------------------------------------------------
    # 3️⃣ ENCODE FROM OPENCV FRAME (BGR)
    # ------------------------------------------------------------
    def encode_from_image(self, img):
        """
        Takes OpenCV BGR frame.
        Converts to RGB → returns encoding or None.
        """
        try:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception:
            return None

        locations = face_recognition.face_locations(rgb, model="hog")
        if not locations:
            return None

        encs = face_recognition.face_encodings(rgb, locations)
        if not encs:
            return None

        return encs[0]

    # ------------------------------------------------------------
    # 4️⃣ DUPLICATE FACE CHECK
    # ------------------------------------------------------------
    def is_face_duplicate(self, new_encoding, existing_encodings, tolerance=0.45):
        """
        Checks if new face matches ANY existing face encoding.
        """
        if not isinstance(new_encoding, np.ndarray):
            new_encoding = np.array(new_encoding, dtype=np.float64)

        clean_list = []
        for enc in existing_encodings:
            try:
                enc_arr = np.array(enc, dtype=np.float64)
                clean_list.append(enc_arr)
            except:
                pass

        if not clean_list:
            return False

        results = face_recognition.compare_faces(
            clean_list, new_encoding, tolerance
        )
        return True in results

    # ------------------------------------------------------------
    # 5️⃣ ONE-TO-ONE FACE COMPARISON
    # ------------------------------------------------------------
    def compare_face(self, known_encoding, unknown_encoding, tolerance=0.5):
        """
        Checks if two encodings match.
        """
        if not isinstance(known_encoding, np.ndarray):
            known_encoding = np.array(known_encoding, dtype=np.float64)

        if not isinstance(unknown_encoding, np.ndarray):
            unknown_encoding = np.array(unknown_encoding, dtype=np.float64)

        results = face_recognition.compare_faces(
            [known_encoding], unknown_encoding, tolerance
        )
        return results[0]

    # ------------------------------------------------------------
    # 6️⃣ ENCODING → HASH (BLOCKCHAIN)
    # ------------------------------------------------------------
    def create_face_data_hash(self, encoding):
        """
        Convert encoding → sha256 hash (deterministic).
        Accepts list or numpy array.
        """
        if not hasattr(encoding, "tobytes"):
            encoding = np.array(encoding, dtype=np.float64)

        return hashlib.sha256(encoding.tobytes()).hexdigest()

    # ------------------------------------------------------------
    # ✅ BACKWARD-COMPATIBLE ALIAS (IMPORTANT)
    # ------------------------------------------------------------
    def hash_encoding(self, encoding):
        """
        Alias for create_face_data_hash()
        Used by voter_routes.py
        """
        return self.create_face_data_hash(encoding)
