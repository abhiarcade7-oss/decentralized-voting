from flask import Blueprint, request, jsonify, current_app
from backend.services.election_service import ElectionService
from backend.services.user_service import UserService
from backend.services.face_service import FaceService
from backend.services.blockchain_service import BlockchainService
from backend.database import db
from backend.models import Election, Candidate
import os
import random
from werkzeug.utils import secure_filename
import base64
import numpy as np
from backend.utils.image_utils import base64_to_image
from backend.models import Admin
from werkzeug.security import check_password_hash


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# SERVICES
e_service = ElectionService()
u_service = UserService()
f_service = FaceService()
bc_service = BlockchainService()

# ====================================================
# ⭐ REMOVE OLD UPLOAD BLOCK — REPLACED WITH FUNCTION
# ====================================================

def get_upload_folder():
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    return folder


# ====================================================
# GET CURRENT ELECTION
# ====================================================

@admin_bp.route("/current_election", methods=["GET"])
def current_election():
    election = Election.query.first()

    if not election:
        return {"exists": False}, 200

    return {
        "exists": True,
        "id": election.id,
        "title": election.name
    }, 200


# ====================================================
# CREATE ELECTION
# ====================================================

@admin_bp.route("/create_election", methods=["POST"])
def create_election():
    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({
            "success": False,
            "message": "Election title required"
        }), 400

    existing = Election.query.first()

    if existing:
        return jsonify({
            "success": False,
            "exists": True,
            "message": f"Election already exists → ID: {existing.id}, Name: {existing.name}",
            "election_id": existing.id,
            "election_name": existing.name
        }), 200

    try:
        contract_address, tx_hash = bc_service.deploy_new_election_contract()
        unique_id = random.randint(1000, 99999999)

        new_election = Election(
            id=unique_id,
            name=title,
            contract_address=contract_address,
            is_active=True
        )

        db.session.add(new_election)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Election created successfully",
            "election_id": new_election.id,
            "election_name": new_election.name
        }), 201

    except Exception as e:
        current_app.logger.exception("Election creation error")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ====================================================
# DELETE ELECTION
# ====================================================

@admin_bp.route("/delete_election/<int:election_id>", methods=["DELETE"])
def delete_election(election_id):

    try:
        # 🔥 RESET ALL VOTERS (VERY IMPORTANT)
        u_service.reset_all_voters_voted_status()

        # 🗑 DELETE ALL CANDIDATES OF THIS ELECTION
        Candidate.query.filter_by(election_id=election_id).delete()

        # 🗑 DELETE ELECTION
        Election.query.delete()
        db.session.commit()

        return {
            "success": True,
            "message": "🗑 Election deleted successfully & voters reset"
        }, 200

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }, 500



# ====================================================
# REGISTER VOTER
# ====================================================

@admin_bp.route("/register_voter", methods=["POST"])
def register_voter():

    name = request.form.get("name")
    enrollment = request.form.get("enrollment")
    image_file = request.files.get("image")

    if not name or not enrollment or not image_file:
        return jsonify({"error": "All fields required"}), 400

    if u_service.get_by_enrollment(enrollment):
        return jsonify({"error": "Voter already exists"}), 400

    try:
        face_encoding = f_service.encode_from_image_file(image_file)

        voter = u_service.create_voter(
            name=name,
            enrollment=enrollment,
            face_encodings=[face_encoding]
        )

        return jsonify({
            "message": "Voter registered successfully (DB only)",
            "voter_id": voter.id
        }), 201

    except Exception as e:
        current_app.logger.exception("Register voter error")
        return jsonify({"error": str(e)}), 500


# ====================================================
# ADD CANDIDATE (CORRECT UPLOAD PATH)
# ====================================================

@admin_bp.route("/add_candidate", methods=["POST"])
def add_candidate():

    name = request.form.get("name")
    party = request.form.get("party", "Not Provided")
    age = request.form.get("age", "")
    qualification = request.form.get("qualification", "")
    photo = request.files.get("photo")

    if not name:
        return jsonify({"error": "Candidate name is required"}), 400

    election = e_service.get_active()
    if not election:
        return jsonify({"error": "No active election"}), 400

    # ---------- CHECK DUPLICATE ----------
    existing = Candidate.query.filter_by(
        name=name,
        election_id=election.id
    ).first()

    if existing:
        return jsonify({"error": "Candidate already exists!"}), 400

    # ---------- SAVE PHOTO ----------
    photo_url = "/static/default_candidate.png"
    if photo:
        filename = secure_filename(photo.filename)
        upload_dir = get_upload_folder()
        save_path = os.path.join(upload_dir, filename)
        photo.save(save_path)
        photo_url = f"/uploads/{filename}"

    # ---------- 🔥 ADD CANDIDATE ON BLOCKCHAIN ----------
    try:
        on_chain_id = bc_service.add_candidate(
            contract_address=election.contract_address,
            name=name,
            owner=os.getenv("OWNER_ADDRESS"),
            private_key=os.getenv("PRIVATE_KEY")
        )
    except Exception as e:
        return jsonify({"error": f"Blockchain error: {str(e)}"}), 500

    # ---------- SAVE IN DATABASE ----------
    candidate = Candidate(
        name=name,
        party=party,
        age=age,
        qualification=qualification,
        photo=photo_url,
        logo="",
        election_id=election.id,
        on_chain_id=on_chain_id   # 🔥 MOST IMPORTANT LINE
    )

    db.session.add(candidate)
    db.session.commit()

    return jsonify({
        "message": "Candidate added successfully (DB + Blockchain)",
        "candidate_id": candidate.id,
        "on_chain_id": on_chain_id
    }), 201


# ====================================================
# GET CANDIDATES
# ====================================================

@admin_bp.route("/get_candidates", methods=["GET"])
def get_candidates():
    election = e_service.get_active()
    if not election:
        return jsonify({"error": "No active election"}), 400

    candidates = e_service.get_candidates_by_election(election.id)

    data = [{
        "id": c.id,
        "name": c.name,
        "party": c.party or "",
        "age": c.age or "",
        "qualification": c.qualification or "",
        "photo": c.photo or "",
        "logo": c.logo or "",
        "onchain_id": getattr(c, "on_chain_id", None)
    } for c in candidates]

    return jsonify({"candidates": data})


# ====================================================
# DELETE CANDIDATE
# ====================================================

@admin_bp.route("/delete_candidate/<int:candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id):
    candidate = Candidate.query.filter_by(id=candidate_id).first()

    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    db.session.delete(candidate)
    db.session.commit()

    return jsonify({"message": "Candidate deleted successfully!"})


# ====================================================
# GET RESULTS
# ====================================================

@admin_bp.route("/results", methods=["GET"])
def get_results():
    election = e_service.get_active()
    if not election or not election.contract_address:
        return jsonify({"error": "No active election"}), 400

    results = bc_service.get_results(election.contract_address)
    return jsonify({"results": results}), 200


# =======================================================
# REGISTER VOTER FACE
# =======================================================

@admin_bp.route("/register_voter_faces", methods=["POST"])
def register_voter_faces():
    data = request.get_json()

    name = data.get("name")
    enrollment = data.get("enrollment")
    frames = data.get("frames")

    if not name or not enrollment or not frames:
        return jsonify({"error": "Name, enrollment and face frames required"}), 400

    if u_service.get_by_enrollment(enrollment):
        return jsonify({"error": "Enrollment number already exists"}), 400

    from backend.models import Voter
    voters = Voter.query.all()
    existing_encodings = []

    for v in voters:
        try:
            if v.face_encodings:
                for enc in v.face_encodings:
                    existing_encodings.append(np.array(enc, dtype=np.float64))
        except:
            pass

    try:
        encodings = []

        for frame in frames:
            img = base64_to_image(frame)
            enc = f_service.encode_from_image(img)
            if enc is not None:
                encodings.append(enc)

        if len(encodings) == 0:
            return jsonify({"error": "Face not detected"}), 400

        final_encoding = np.mean(encodings, axis=0)

        if f_service.is_face_duplicate(final_encoding, existing_encodings):
            return jsonify({"error": "This face is already registered"}), 400

        voter = u_service.create_voter(
            name=name,
            enrollment=enrollment,
            face_encodings=[final_encoding.tolist()]
        )

        return jsonify({
            "message": "Voter registered successfully (DB + Face)",
            "voter_id": voter.id
        }), 201

    except Exception as e:
        current_app.logger.exception("Register voter faces error")
        return jsonify({"error": str(e)}), 500


# ====================================================
# GET ALL ELECTIONS
# ====================================================

@admin_bp.route("/get_elections", methods=["GET"])
def get_elections():
    elections = e_service.get_all_elections()

    data = [{
        "id": e.id,
        "name": e.name,
        "active": e.is_active,
        "contract_address": e.contract_address
    } for e in elections]

    return jsonify(data)

# ====================================================
# CHECK IF ADMIN EXISTS
# ====================================================

@admin_bp.route("/check_admin", methods=["GET"])
def check_admin():
    admin = u_service.get_any_admin()

    if admin:
        return jsonify({"exists": True})
    return jsonify({"exists": False})


@admin_bp.route("/setup_admin", methods=["POST"])
def setup_admin_route():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    frames = data.get("frames")

    # ===============================
    # 1️⃣ BASIC VALIDATION
    # ===============================
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if not frames or len(frames) == 0:
        return jsonify({"error": "Face frames required"}), 400

    if u_service.get_admin_by_username(username):
        return jsonify({
            "success": False,
            "already_exists": True,
            "message": "Admin already registered"
        }), 200

    # ===============================
    # 2️⃣ EXTRACT FACE ENCODINGS
    # ===============================
    encodings = []

    for f in frames:
        img = base64_to_image(f)
        enc = f_service.encode_from_image(img)
        if enc is not None:
            encodings.append(enc)

    if len(encodings) == 0:
        return jsonify({"error": "Face not detected"}), 400

    final_enc = np.mean(encodings, axis=0)

    # ===============================
    # 3️⃣ CREATE ADMIN IN DATABASE ONLY
    # ===============================
    u_service.create_admin(
        username=username,
        password=password,
        face_encodings=[final_enc.tolist()]
    )

    return jsonify({
        "success": True,
        "message": "Admin registered successfully"
    }), 201



@admin_bp.route("/admin_face_login", methods=["POST"])
def admin_face_login():
    from werkzeug.security import check_password_hash
    from flask import session
    import json
    import numpy as np

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    frames = data.get("frames")

    # 1️⃣ BASIC VALIDATION
    if not username or not password:
        return jsonify({"error": "Username or password missing"}), 400

    if not frames or len(frames) == 0:
        return jsonify({"error": "No frames received"}), 400

    # 2️⃣ USERNAME + PASSWORD CHECK
    admin = Admin.query.filter_by(username=username).first()

    if not admin:
        return jsonify({"error": "Invalid username or password"}), 401

    if not check_password_hash(admin.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    if not admin.face_encodings:
        return jsonify({"error": "Admin face not registered"}), 400

    # 3️⃣ LOAD STORED FACE ENCODINGS SAFELY
    raw_encodings = admin.face_encodings

    if isinstance(raw_encodings, str):
        try:
            raw_encodings = json.loads(raw_encodings)
        except Exception:
            return jsonify({"error": "Stored face data corrupted"}), 500

    stored_encodings = []
    for enc in raw_encodings:
        try:
            stored_encodings.append(np.array(enc, dtype=np.float64))
        except Exception:
            pass

    if not stored_encodings:
        return jsonify({"error": "Stored face data corrupted"}), 500

    # 4️⃣ FACE MATCH
    matched = False

    for frame in frames:
        img = base64_to_image(frame)
        live_enc = f_service.encode_from_image(img)

        if live_enc is None:
            continue

        if f_service.is_face_duplicate(live_enc, stored_encodings, tolerance=0.5):
            matched = True
            break

    if not matched:
        return jsonify({"error": "Face does not match"}), 401

    # 🔥🔥🔥 5️⃣ SET SESSION (THIS WAS MISSING)
    session["admin_id"] = admin.id
    session.permanent = True

    return jsonify({
        "success": True,
        "admin_id": admin.id,
        "username": admin.username
    }), 200

@admin_bp.route("/me", methods=["GET"])
def admin_me():
    from flask import session

    admin_id = session.get("admin_id")

    if not admin_id:
        return jsonify({"logged_in": False}), 401

    admin = Admin.query.get(admin_id)
    if not admin:
        return jsonify({"logged_in": False}), 401

    return jsonify({
        "logged_in": True,
        "username": admin.username
    }), 200

# ===================================
# GET ALL THE REGISTER VOTER
# ====================================
@admin_bp.route("/get_voters", methods=["GET"])
def get_voters():
    from backend.models import Voter

    voters = Voter.query.all()

    data = [{
        "id": v.id,
        "name": v.name,
        "enrollment": v.enrollment,
        "has_voted": v.has_voted
    } for v in voters]

    return jsonify({"voters": data}), 200

# ===================================
# DELETE REGISTERED VOTER
# ====================================
@admin_bp.route("/delete_voter/<int:voter_id>", methods=["DELETE"])
def delete_voter(voter_id):
    from backend.models import Voter

    voter = Voter.query.get(voter_id)
    if not voter:
        return jsonify({"error": "Voter not found"}), 404

    if voter.has_voted:
        return jsonify({
            "error": "Cannot delete voter who has already voted"
        }), 400

    db.session.delete(voter)
    db.session.commit()

    return jsonify({"message": "Voter deleted successfully"}), 200
