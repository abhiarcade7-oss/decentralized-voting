import hashlib

def encode_face_to_hash(encoding):
    # encoding: numpy array
    return hashlib.sha256(encoding.tobytes()).hexdigest()