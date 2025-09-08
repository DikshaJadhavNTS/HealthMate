from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Patient(UserMixin, db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
