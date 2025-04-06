import os
import datetime
import bcrypt
import jwt
import base64
import subprocess
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_from_directory
from werkzeug.utils import secure_filename
from functools import wraps

from config import config
from models.user_model import UserModel
from models.profile_model import ProfileModel
from services.audio_service import AudioService
from result import extract_information

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES_PATH = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_PATH = os.path.join(BASE_DIR, "frontend", "static")
RECORDINGS_PATH = os.path.join(STATIC_PATH, "recordings")

print("BASE_DIR:", BASE_DIR)
print("Templates path:", TEMPLATES_PATH)
print("Static path:", STATIC_PATH)
print("Recordings path:", RECORDINGS_PATH)

app = Flask(__name__, template_folder=TEMPLATES_PATH, static_folder=STATIC_PATH)
app.config['SECRET_KEY'] = config.SECRET_KEY

@app.template_filter('basename')
def basename_filter(value):
    return os.path.basename(value) if value else ""

audio_service = AudioService()


def encode_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            else:
                return jsonify({"error": "Invalid auth header"}), 401
        else:
            token = request.cookies.get("jwt")
            if not token:
                return jsonify({"error": "Missing auth header"}), 401

        user_id = decode_jwt(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(user_id, *args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return "Missing email or password", 400

        existing_user = UserModel.find_by_email(email)
        if existing_user:
            return "User already exists", 400

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        user_id = UserModel.create_user(email, hashed)
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        user = UserModel.find_by_email(email)
        if not user:
            return "Invalid credentials", 401

        if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
            token = encode_jwt(str(user["_id"]))
            response = make_response(jsonify({"token": token}))
            response.set_cookie("jwt", token, httponly=True)
            return response
        else:
            return "Invalid credentials", 401

@app.route("/dashboard")
@jwt_required
def dashboard(user_id):
    profiles = ProfileModel.get_profiles()
    return render_template("dashboard.html", profiles=profiles)

@app.route("/create-profile", methods=["GET", "POST"])
@jwt_required
def create_profile(user_id):
    if request.method == "GET":
        return render_template("profile.html")
    else:
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        location = request.form.get("location")
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        description = request.form.get("description")

        image_file = request.files.get("image_file")
        image_path = None
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(STATIC_PATH, "uploads", filename)
            image_file.save(image_path)

        audio_path = None
        recorded_audio = request.form.get("recordedAudio")
        if recorded_audio:
            try:
                if recorded_audio.startswith("data:"):
                    header, encoded = recorded_audio.split(",", 1)
                else:
                    encoded = recorded_audio
                audio_data = base64.b64decode(encoded)
                unique_audio_filename = f"{user_id}-{int(datetime.datetime.utcnow().timestamp())}.webm"
                audio_filename = secure_filename(unique_audio_filename)
                os.makedirs(RECORDINGS_PATH, exist_ok=True)
                audio_path = os.path.join(RECORDINGS_PATH, audio_filename)
                with open(audio_path, "wb") as f:
                    f.write(audio_data)
                print("Saved recorded audio to:", audio_path)
            except Exception as e:
                print("Error processing recorded audio:", e)
        else:
            audio_file = request.files.get("audio_file")
            if audio_file:
                unique_audio_filename = f"{user_id}-{int(datetime.datetime.utcnow().timestamp())}.webm"
                audio_filename = secure_filename(unique_audio_filename)
                os.makedirs(RECORDINGS_PATH, exist_ok=True)
                audio_path = os.path.join(RECORDINGS_PATH, audio_filename)
                audio_file.save(audio_path)

        profile_id = ProfileModel.create_profile(
            user_id, name, age, gender, location, lat, lon, description, image_path, audio_path
        )
        return redirect(url_for("dashboard"))

@app.route("/transcribe/<profile_id>", methods=["POST"])
@jwt_required
def transcribe(user_id, profile_id):
    profile = ProfileModel.get_profile_by_id(profile_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    if not profile.get("audio_path"):
        return jsonify({"error": "No audio recording found"}), 400

    full_audio_path = os.path.join(RECORDINGS_PATH, os.path.basename(profile["audio_path"]))
    transcription_result = audio_service.transcribe_audio(full_audio_path)
    if not transcription_result.get("transcription"):
        return jsonify({"error": "Transcription failed"}), 500
    return jsonify(transcription_result)

@app.route("/<profile_id>/extract/")
@jwt_required
def extract(user_id, profile_id):
    profile = ProfileModel.get_profile_by_id(profile_id)
    if not profile:
        return "Profile not found", 404

    full_audio_path = os.path.join(RECORDINGS_PATH, os.path.basename(profile["audio_path"]))
    transcription_result = audio_service.transcribe_audio(full_audio_path)
    transcription_text = transcription_result.get("transcription", "")
    if not transcription_text:
        return "Transcription failed", 500

    extracted_info = extract_information(transcription_text)
    if "extra_info" not in extracted_info:
        extracted_info["extra_info"] = {
            "medical_conditions": "Not specified",
            "possible_relatives": "Not specified",
            "problems_concerns": "Not specified"
        }
    return render_template("extract.html", profile=profile, extracted_info=extracted_info)

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return redirect(url_for("dashboard"))
    field = request.args.get("field", "name")
    order = request.args.get("order", "desc")
    filter_query = { field: {"$regex": query, "$options": "i"} }
    from models.profile_model import db
    results = list(db.profiles.find(filter_query))
    if order == "asc":
        results.sort(key=lambda p: p.get("created_at", datetime.datetime.min))
    else:
        results.sort(key=lambda p: p.get("created_at", datetime.datetime.min), reverse=True)
    return render_template("dashboard.html", profiles=results)

@app.route("/profile/<profile_id>")
@jwt_required
def view_profile(user_id, profile_id):
    profile = ProfileModel.get_profile_by_id(profile_id)
    if not profile:
        return "Profile not found", 404
    return render_template("profile_detail.html", profile=profile)

if __name__ == "__main__":
    app.run(debug=True)
