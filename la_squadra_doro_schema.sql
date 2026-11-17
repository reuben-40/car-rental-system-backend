PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(150) NULL
);

CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year SMALLINT NOT NULL,
    registration_number VARCHAR(15) UNIQUE NOT NULL,
    colour VARCHAR(30) NULL,
    color VARCHAR(30) NULL,
    transmission VARCHAR(20) NOT NULL CHECK(transmission IN ('automatic', 'manual')),
    fuel_type VARCHAR(20) NOT NULL CHECK(fuel_type IN ('petrol', 'diesel', 'hybrid', 'electric')),
    seats TINYINT NOT NULL CHECK(seats > 0),
    daily_rate DECIMAL(10,2) NOT NULL CHECK(daily_rate >= 0),
    mileage INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'maintenance', 'retired')),
    primary_image_url VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS car_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    label VARCHAR(20) NOT NULL DEFAULT 'other' CHECK(label IN ('side', 'front', 'interior', 'other')),
    is_main BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(60) UNIQUE NOT NULL,
    address VARCHAR(150) NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer' CHECK(role IN ('customer', 'admin')),
    licence_number VARCHAR(30) NULL,
    licence_expiry DATE NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference VARCHAR(20) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    pickup_location_id INTEGER NULL,
    return_location_id INTEGER NULL,
    pickup_location VARCHAR(150) NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK(end_date > start_date),
    actual_return_date DATE NULL,
    daily_rate_snapshot DECIMAL(10,2) NOT NULL,
    days SMALLINT NOT NULL CHECK(days > 0),
    subtotal DECIMAL(10,2) NOT NULL,
    extras_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    extras TEXT NULL,
    tax DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    deposit DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'active', 'completed', 'cancelled')),
    pickup_mileage INTEGER NULL,
    return_mileage INTEGER NULL,
    cancelled_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS extras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(80) UNIQUE NOT NULL,
    description VARCHAR(150) NULL,
    price DECIMAL(10,2) NULL,
    price_per_day DECIMAL(10,2) NULL,
    per_day BOOLEAN NOT NULL DEFAULT 1,
    is_flat_rate BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS booking_extras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    extra_id INTEGER NOT NULL,
    quantity TINYINT NOT NULL DEFAULT 1,
    price_snapshot DECIMAL(10,2) NOT NULL,
    UNIQUE(booking_id, extra_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (extra_id) REFERENCES extras(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK(amount > 0),
    method VARCHAR(20) NOT NULL CHECK(method IN ('mpesa', 'card', 'cash', 'bank_transfer')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'paid', 'failed', 'refunded')),
    transaction_ref VARCHAR(40) NULL,
    paid_at DATETIME NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    description VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK(end_date >= start_date),
    cost DECIMAL(10,2) NULL DEFAULT 0.00,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value INTEGER
);