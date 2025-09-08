CREATE DATABASE IF NOT EXISTS patient_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE patient_db;

CREATE TABLE IF NOT EXISTS patients (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    contact_number VARCHAR(50),
    gender ENUM('Male','Female','Other') DEFAULT NULL,
    date_of_birth DATE DEFAULT NULL,
    blood_group VARCHAR(10) DEFAULT NULL,
    marital_status VARCHAR(50) DEFAULT NULL,
    emergency_contact VARCHAR(50) DEFAULT NULL,
    allergies TEXT DEFAULT NULL,
    current_medications TEXT DEFAULT NULL,
    past_medications TEXT DEFAULT NULL,
    chronic_diseases TEXT DEFAULT NULL,
    injuries TEXT DEFAULT NULL,
    surgeries TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
