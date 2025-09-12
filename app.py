
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import secrets
import mysql.connector
from chatbot import ConversationManager
from models import db, Patient

# ---------- AUTO CREATE DATABASE ----------
DB_NAME = "patient_db"
MYSQL_USER = "root"         
MYSQL_PASSWORD = "root"        
MYSQL_HOST = "127.0.0.1"

conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD
)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.close()
conn.close()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32) 
conv_manager = ConversationManager()

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
CORS(app, supports_credentials=True)


# ---------- Models ----------
class Patient(UserMixin, db.Model):
    __tablename__ = "patients"
    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    blood_group = db.Column(db.String(10))
    marital_status = db.Column(db.String(50))
    emergency_contact = db.Column(db.String(50))
    allergies = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    past_medications = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    injuries = db.Column(db.Text)
    surgeries = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "contact_number": self.contact_number,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "blood_group": self.blood_group,
            "marital_status": self.marital_status,
            "emergency_contact": self.emergency_contact,
            "allergies": self.allergies,
            "current_medications": self.current_medications,
            "past_medications": self.past_medications,
            "chronic_diseases": self.chronic_diseases,
            "injuries": self.injuries,
            "surgeries": self.surgeries,
        }


@login_manager.user_loader
def load_user(user_id):
    return Patient.query.get(int(user_id))


# ---------- Routes ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"msg": "Full name, email, and password are required"}), 400

    try:
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({"msg": "Invalid email", "error": str(e)}), 400

    if Patient.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400

    password_hash = generate_password_hash(password)

    dob = None
    if data.get("date_of_birth"):
        try:
            dob = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"msg": "Invalid date format, use YYYY-MM-DD"}), 400

    patient = Patient(
        full_name=full_name,
        email=email,
        password_hash=password_hash,
        contact_number=data.get("contact_number"),
        gender=data.get("gender"),
        date_of_birth=dob,
        blood_group=data.get("blood_group"),
        marital_status=data.get("marital_status"),
        emergency_contact=data.get("emergency_contact"),
        allergies=data.get("allergies"),
        current_medications=data.get("current_medications"),
        past_medications=data.get("past_medications"),
        chronic_diseases=data.get("chronic_diseases"),
        injuries=data.get("injuries"),
        surgeries=data.get("surgeries"),
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({"msg": "Registration successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    patient = Patient.query.filter_by(email=email).first()
    if not patient or not check_password_hash(patient.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    login_user(patient)
    return jsonify({"msg": "Login successful"}), 200


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "Logged out successfully"}), 200
from flask import jsonify

@app.route("/getallpatients", methods=["GET"])
def get_all_patients():
    try:
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/patient/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/profile", methods=["GET"])
@login_required
def profile():
    return jsonify({"patient": current_user.to_dict()}), 200

@app.route("/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json()
    user_text = data.get("message", "").strip()

    if not user_text:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Use only ConversationManager for multi-turn flow
    response = conv_manager.process(user_text)

    return jsonify(response)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
