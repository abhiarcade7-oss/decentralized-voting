from flask import Blueprint, request, jsonify, current_app
import json
import os
import io
import base64
import numpy as np
import face_recognition

from backend.services.user_service import UserService
from backend.services.face_service import FaceService
from backend.services.blockchain_service import BlockchainService
from backend.services.election_service import ElectionService
from backend.models import Candidate, Election, Voter

voter_bp = Blueprint("voter", __name__, url_prefix="/voter")

u_service = UserService()
f_service = FaceService()
e_service = ElectionService()
bc_service = BlockchainService()

# ======================================================
# VOTER FACE AUTHENTICATION (UNCHANGED)
# ======================================================
@voter_bp.route("/authenticate", methods=["POST"])
def authenticate_voter():
    try:
        data = request.get_json(force=True)

        username = data.get("username")
        enrollment = data.get("enrollment")
        frames = data.get("frames")

        if not username or not enrollment or not frames:
            return jsonify({"success": False, "error": "Missing data"}), 400

        voter = u_service.get_by_enrollment(enrollment)
        if not voter:
            return jsonify({"success": False, "error": "Voter not found"}), 404

        if voter.has_voted:
            return jsonify({"success": False, "error": "Already voted"}), 403

        stored_encodings = json.loads(voter.face_encodings)
        known_encodings = [np.array(e, dtype=np.float64) for e in stored_encodings]

        verified = False

        for frame in frames:
            _, encoded = frame.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            image = face_recognition.load_image_file(io.BytesIO(img_bytes))

            locs = face_recognition.face_locations(image)
            if not locs:
                continue

            unknowns = face_recognition.face_encodings(image, locs)
            for u in unknowns:
                if True in face_recognition.compare_faces(known_encodings, u, tolerance=0.45):
                    verified = True
                    break
            if verified:
                break

        if not verified:
            return jsonify({"success": False, "error": "Face mismatch"}), 401

        return jsonify({
            "success": True,
            "voter_id": voter.id,
            "voter_name": voter.name
        }), 200

    except Exception:
        current_app.logger.exception("Auth failed")
        return jsonify({"success": False, "error": "Server error"}), 500


# ======================================================
# 🔥 CAST VOTE (FIXED — FINAL VERSION)
# ======================================================
@voter_bp.route("/vote", methods=["POST"])
def cast_vote():
    try:
        data = request.get_json(force=True)

        voter_id = data.get("voter_id")
        on_chain_id = data.get("candidate_id")  # 🔥 THIS IS ON-CHAIN ID

        if voter_id is None or on_chain_id is None:
            return jsonify({"error": "Invalid vote data"}), 400

        voter = Voter.query.get(int(voter_id))
        if not voter:
            return jsonify({"error": "Invalid voter"}), 404

        if voter.has_voted:
            return jsonify({"error": "You have already voted"}), 403

        election = Election.query.filter_by(is_active=True).first()
        if not election or not election.contract_address:
            return jsonify({"error": "No active election"}), 400

        # 🔥 MAP ON-CHAIN ID → DB CANDIDATE
        candidate = Candidate.query.filter_by(
            election_id=election.id,
            on_chain_id=int(on_chain_id)
        ).first()

        if not candidate:
            return jsonify({"error": "Invalid candidate selection"}), 400

        # 🔐 SAME HASH AS USED BEFORE
        stored_encodings = json.loads(voter.face_encodings)
        face_enc = np.array(stored_encodings[0], dtype=np.float64)
        voter_hash = f_service.create_face_data_hash(face_enc)

        owner = os.getenv("OWNER_ADDRESS")
        private_key = os.getenv("PRIVATE_KEY")

        tx_hash = bc_service.vote(
            voter_hash,
            int(on_chain_id),
            election.contract_address,
            owner,
            private_key
        )

        voter.has_voted = True
        u_service.set_voted(voter)

        return jsonify({
            "success": True,
            "tx_hash": tx_hash
        }), 200

    except Exception as e:
        current_app.logger.exception("Vote failed")
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🔥 GET CANDIDATES FOR VOTING (FIXED)
# ======================================================
@voter_bp.route("/get_candidates/<int:election_id>", methods=["GET"])
def get_candidates(election_id):
    try:
        candidates = Candidate.query.filter_by(
            election_id=election_id
        ).all()

        data = []
        for c in candidates:
            if not c.on_chain_id:
                continue

            data.append({
                "id": c.id,
                "name": c.name,
                "party": c.party,
                "photo": c.photo,
                "on_chain_id": c.on_chain_id  # 🔥 REQUIRED
            })

        return jsonify(data), 200

    except Exception as e:
        current_app.logger.exception("Get candidates failed")
        return jsonify({"error": str(e)}), 500


# ======================================================
# CHECK VOTER STATUS (UNCHANGED)
# ======================================================
@voter_bp.route("/status/<int:voter_id>", methods=["GET"])
def voter_status(voter_id):
    voter = u_service.get_by_id(voter_id)

    if not voter:
        return jsonify({"error": "Voter not found"}), 404

    return jsonify({"has_voted": voter.has_voted}), 200
