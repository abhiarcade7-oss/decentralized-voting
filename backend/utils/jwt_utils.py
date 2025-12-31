import jwt
import os
from datetime import datetime, timedelta
SECRET = os.getenv("SECRET_KEY", "supersecretkey")

def create_token(payload, minutes=60):
    exp = datetime.utcnow() + timedelta(minutes=minutes)
    payload2 = payload.copy()
    payload2.update({"exp": exp})
    return jwt.encode(payload2, SECRET, algorithm="HS256")

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return data
    except Exception:
        return None