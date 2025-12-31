# backend/services/user_service.py

import json
from backend.models import Voter, Admin
from backend.database import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:

    # ======================================================
    # CREATE VOTER
    # ======================================================
    def create_voter(self, name, enrollment, face_encodings):
        """
        Creates voter with:
        - name
        - enrollment
        - face_encodings: list of numpy arrays
        """

        face_enc_json = json.dumps([
            enc.tolist() if hasattr(enc, "tolist") else enc
            for enc in face_encodings
        ])

        voter = Voter(
            name=name,
            enrollment=enrollment,
            face_encodings=face_enc_json,
            has_voted=False
        )

        db.session.add(voter)
        db.session.commit()
        return voter

    # ======================================================
    # GET VOTER BY ID
    # ======================================================
    def get_by_id(self, voter_id):
        return Voter.query.get(voter_id)

    # ======================================================
    # GET VOTER BY ENROLLMENT
    # ======================================================
    def get_by_enrollment(self, enrollment):
        return Voter.query.filter_by(enrollment=enrollment).first()

    # ======================================================
    # GET ALL VOTERS
    # ======================================================
    def get_all_voters(self):
        return Voter.query.all()

    # ======================================================
    # MARK VOTER AS VOTED
    # ======================================================
    def set_voted(self, voter):
        voter.has_voted = True
        db.session.commit()

    # ======================================================
    # 🔥 RESET VOTED STATUS (THIS IS THE FIX)
    # ======================================================
    def reset_all_voters_voted_status(self):
        """
        Call this when:
        - Election is deleted
        - New election is created
        """
        Voter.query.update({Voter.has_voted: False})
        db.session.commit()

    # ======================================================
    # ================= ADMIN SECTION ======================
    # ======================================================

    # GET ADMIN BY USERNAME
    def get_admin_by_username(self, username):
        return Admin.query.filter_by(username=username).first()

    # GET ANY ADMIN
    def get_any_admin(self):
        return Admin.query.first()

    # ======================================================
    # CREATE ADMIN (ONE TIME ONLY)
    # ======================================================
    def create_admin(self, username, password, face_encodings):

        if Admin.query.first():
            raise Exception("Admin already exists!")

        password_hash = generate_password_hash(password)

        face_enc_json = json.dumps([
            enc.tolist() if hasattr(enc, "tolist") else enc
            for enc in face_encodings
        ])

        admin = Admin(
            username=username,
            password_hash=password_hash,
            face_encodings=face_enc_json
        )

        db.session.add(admin)
        db.session.commit()

        return admin

    # ======================================================
    # UPDATE ADMIN
    # ======================================================
    def update_admin(self, admin, password=None, new_face_encodings=None):

        if password:
            admin.password_hash = generate_password_hash(password)

        if new_face_encodings:
            admin.face_encodings = json.dumps([
                enc.tolist() if hasattr(enc, "tolist") else enc
                for enc in new_face_encodings
            ])

        db.session.commit()
        return admin

    # ======================================================
    # PASSWORD CHECK
    # ======================================================
    def check_password(self, stored_hash, password):
        return check_password_hash(stored_hash, password)
