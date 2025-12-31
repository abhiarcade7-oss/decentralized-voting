import os
import time

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.database import db


def create_app():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # =====================================================
    # FRONTEND + UPLOAD PATHS (FINAL FIXED)
    # =====================================================
    FRONTEND_PATH = os.path.join(BASE_DIR, "..", "frontend", "public")

    # UPLOADS folder ALWAYS inside frontend/public/uploads
    UPLOAD_PATH = os.path.join(FRONTEND_PATH, "uploads")

    # Ensure upload folder exists
    os.makedirs(UPLOAD_PATH, exist_ok=True)

    # =====================================================
    # FLASK APP INITIALIZATION
    # =====================================================
    app = Flask(
        __name__,
        static_folder=FRONTEND_PATH,
        static_url_path="",      # Serve static files directly
        template_folder=FRONTEND_PATH
    )

    # Store upload folder in config (admin_routes will use this)
    app.config["UPLOAD_FOLDER"] = UPLOAD_PATH
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "a_very_secret_key")

    # DATABASE CONFIG
    default_sqlite = "sqlite:///" + os.path.join(BASE_DIR, "instance", "voting_local.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_sqlite)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    # =====================================================
    # BLUEPRINTS
    # =====================================================
    from backend.routes.admin_routes import admin_bp
    from backend.routes.voter_routes import voter_bp

    print("REGISTERING BLUEPRINTS...")

    app.register_blueprint(admin_bp)
    print("Registered admin_bp")

    app.register_blueprint(voter_bp)
    print("Registered voter_bp")


    # =====================================================
    # DATABASE WAIT + CREATE TABLES
    # =====================================================
    from sqlalchemy import text

    def wait_for_db(max_attempts=10, delay=2):
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"⏳ Checking Database (Attempt {attempt})")
                with app.app_context():
                    db.session.execute(text("SELECT 1"))
                print("✅ Database Ready!")
                return
            except Exception as exc:
                print(f"❌ DB not ready: {exc}")
                time.sleep(delay)
        print("⚠ Continuing even though DB not confirmed.")

    with app.app_context():
        wait_for_db()
        db.create_all()

    # =====================================================
    # FRONTEND STATIC ROUTES
    # =====================================================
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_PATH, "index.html")

    @app.route("/admin-login")
    def admin_login():
        return send_from_directory(FRONTEND_PATH, "admin_login.html")

    @app.route("/admin-panel")
    def admin_panel():
        return send_from_directory(FRONTEND_PATH, "admin.html")

    @app.route("/register-voter-page")
    def register_page():
        return send_from_directory(FRONTEND_PATH, "register_voter.html")

    @app.route("/candidate-registration")
    def candidate_page():
        return send_from_directory(FRONTEND_PATH, "candidate_registration.html")

    @app.route("/create-election")
    def create_election_page():
        return send_from_directory(FRONTEND_PATH, "create_election.html")

    @app.route("/delete-election")
    def delete_election_page():
        return send_from_directory(FRONTEND_PATH, "delete_election.html")

    @app.route("/results-page")
    def results_page():
        return send_from_directory(FRONTEND_PATH, "results.html")

    # =====================================================
    # ⭐ NEW: EXACT STATIC ROUTES YOU REQUESTED (MANDATORY)
    # =====================================================
    @app.route("/admin_register.html")
    def admin_register_page():
        return send_from_directory(FRONTEND_PATH, "admin_register.html")

    @app.route("/admin_login.html")
    def admin_login_page():
        return send_from_directory(FRONTEND_PATH, "admin_login.html")

    # =====================================================
    # ⭐ SERVE UPLOADED FILES (FINAL FIXED)
    # =====================================================
    @app.route("/uploads/<path:filename>")
    def uploaded_files(filename):
        """
        This serves uploaded candidate images.
        Path = frontend/public/uploads/<filename>
        """
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app


# =====================================================
# RUN SERVER
# =====================================================
if __name__ == "__main__":
    print("\n============================")
    print("🚀 SERVER RUNNING")
    print("📍 http://127.0.0.1:5000")
    print("============================\n")

    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)

