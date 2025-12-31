# backend/models.py

from backend.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ================================
# ADMIN MODEL
# ================================
class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    # store hashed password only
    password_hash = db.Column(db.String(255), nullable=False)

    # Store face encodings as JSON array (list of floats)
    face_encodings = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    blockchain_hash = db.Column(db.String(66), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ----------------------------
    # PASSWORD HELPERS
    # ----------------------------
    def set_password(self, plain_password: str):
        """
        Hash and store password
        """
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """
        Verify password
        """
        return check_password_hash(self.password_hash, plain_password)

    def __repr__(self):
        return f"<Admin id={self.id} username={self.username}>"


# ================================
# ELECTION MODEL
# ================================
class Election(db.Model):
    __tablename__ = "election"

    # Manual ID allowed (used elsewhere in project)
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    name = db.Column(db.String(100), nullable=False)

    contract_address = db.Column(db.String(42), unique=True, nullable=True)

    is_active = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with candidates
    candidates = db.relationship(
        "Candidate",
        backref="election",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Election id={self.id} name={self.name}>"


# ================================
# CANDIDATE MODEL
# ================================
class Candidate(db.Model):
    __tablename__ = "candidate"

    id = db.Column(db.Integer, primary_key=True)

    # Required
    name = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=True)

    # Optional fields
    age = db.Column(db.String(10), nullable=True)
    qualification = db.Column(db.String(100), nullable=True)

    # Media
    photo = db.Column(db.String(255), nullable=True)
    logo = db.Column(db.String(255), nullable=True)

    # On-chain ID reference
    on_chain_id = db.Column(db.Integer, nullable=True)

    # Election reference
    election_id = db.Column(
        db.Integer,
        db.ForeignKey("election.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Candidate id={self.id} name={self.name}>"


# ================================
# VOTER MODEL
# ================================
class Voter(db.Model):
    __tablename__ = "voter"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    enrollment = db.Column(db.String(50), unique=True, nullable=False)

    # Store face encodings as JSON list
    face_encodings = db.Column(db.JSON, nullable=True)

    has_voted = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Voter id={self.id} enrollment={self.enrollment} name={self.name}>"
