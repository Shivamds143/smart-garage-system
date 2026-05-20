-- ============================================================
--  Smart Garage Locator System — MySQL Schema
--  Run this in MySQL Workbench or CLI:
--  mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_garage_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smart_garage_db;

-- ─── 1. USERS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(120)    NOT NULL,
    email              VARCHAR(120)    NOT NULL UNIQUE,
    phone              VARCHAR(20),
    password_hash      VARCHAR(256)    NOT NULL,
    role               ENUM('user','admin') DEFAULT 'user' NOT NULL,
    latitude           DOUBLE,
    longitude          DOUBLE,
    emergency_contact  VARCHAR(120),
    created_at         DATETIME        DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email    (email),
    INDEX idx_role     (role)
) ENGINE=InnoDB;

-- ─── 2. GARAGES ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    admin_id        INT          NOT NULL,
    name            VARCHAR(150) NOT NULL,
    address         VARCHAR(300) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    email           VARCHAR(120),
    latitude        DOUBLE       NOT NULL DEFAULT 19.0760,
    longitude       DOUBLE       NOT NULL DEFAULT 72.8777,
    rating          FLOAT        DEFAULT 0.0,
    total_ratings   INT          DEFAULT 0,
    is_active       BOOLEAN      DEFAULT TRUE,
    open_time       VARCHAR(10)  DEFAULT '09:00',
    close_time      VARCHAR(10)  DEFAULT '20:00',
    description     TEXT,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_city  (city),
    INDEX idx_active(is_active)
) ENGINE=InnoDB;

-- ─── 3. SERVICES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS services (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    garage_id        INT          NOT NULL,
    name             VARCHAR(150) NOT NULL,
    description      TEXT,
    price            FLOAT        NOT NULL,
    duration_minutes INT          DEFAULT 60,
    is_available     BOOLEAN      DEFAULT TRUE,
    created_at       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (garage_id) REFERENCES garages(id) ON DELETE CASCADE,
    INDEX idx_garage (garage_id)
) ENGINE=InnoDB;

-- ─── 4. VEHICLES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehicles (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT         NOT NULL,
    reg_number        VARCHAR(20) NOT NULL,
    make              VARCHAR(80) NOT NULL,
    model             VARCHAR(80) NOT NULL,
    year              INT,
    color             VARCHAR(40),
    insurance_number  VARCHAR(80),
    insurance_expiry  DATE,
    created_at        DATETIME    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user    (user_id)
) ENGINE=InnoDB;

-- ─── 5. BOOKINGS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT  NOT NULL,
    garage_id       INT  NOT NULL,
    service_id      INT  NOT NULL,
    vehicle_id      INT,
    booking_date    DATE NOT NULL,
    booking_time    TIME NOT NULL,
    status          ENUM('pending','confirmed','rejected','completed','cancelled')
                         DEFAULT 'pending' NOT NULL,
    notes           TEXT,
    total_amount    FLOAT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (garage_id)  REFERENCES garages(id)  ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL,
    INDEX idx_user_id   (user_id),
    INDEX idx_garage_id (garage_id),
    INDEX idx_status    (status),
    INDEX idx_date      (booking_date)
) ENGINE=InnoDB;

-- ─── 6. DOCUMENTS ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT         NOT NULL,
    doc_type      ENUM('RC','Insurance','License','Other') NOT NULL,
    filename      VARCHAR(256) NOT NULL,
    original_name VARCHAR(256) NOT NULL,
    file_size     INT,
    expiry_date   DATE,
    notes         VARCHAR(300),
    uploaded_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) ENGINE=InnoDB;

-- ─── 7. SOS ALERTS ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sos_alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT  NOT NULL,
    garage_id   INT,
    latitude    DOUBLE NOT NULL,
    longitude   DOUBLE NOT NULL,
    address     VARCHAR(300),
    message     TEXT,
    status      ENUM('active','acknowledged','resolved') DEFAULT 'active',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    FOREIGN KEY (garage_id) REFERENCES garages(id) ON DELETE SET NULL,
    INDEX idx_user      (user_id),
    INDEX idx_status    (status),
    INDEX idx_created   (created_at)
) ENGINE=InnoDB;

-- ─── Verify ──────────────────────────────────────────────────
SHOW TABLES;
SELECT 'Schema created successfully!' AS result;
