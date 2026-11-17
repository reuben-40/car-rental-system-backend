INSERT OR IGNORE INTO categories (id, name, description) VALUES
(1, 'Economy', 'Fuel-sipping city cars'),
(2, 'SUV', 'Safari-ready 4x4s'),
(3, 'Luxury', 'Executive arrivals'),
(4, 'Van', 'Groups and cargo');

INSERT OR IGNORE INTO locations (id, name, address, is_active) VALUES
(1, 'JKIA', 'Jomo Kenyatta International Airport, Terminal 1A & 1E', 1),
(2, 'Wilson Airport', 'Langata Road, Nairobi', 1),
(3, 'Westlands', 'Sarit Centre & Westgate Mall Hub', 1),
(4, 'Kilimani', 'Yaya Centre Hub, Argwings Kodhek Rd', 1),
(5, 'Karen', 'The Hub Karen, Dagoretti Rd', 1),
(6, 'CBD', 'Kenyatta Avenue & City Hall Way', 1);

INSERT OR IGNORE INTO extras (id, name, description, price, price_per_day, per_day, is_flat_rate) VALUES
(1, 'Child seat', 'ISOFIX, ages 1-4', 500.00, 500.00, 1, 0),
(2, 'GPS navigation', 'offline Kenya maps', 400.00, 400.00, 1, 0),
(3, 'Extra driver', 'Add a second licensed driver', 2500.00, 2500.00, 0, 1),
(4, 'Airport meet-and-greet', 'VIP arrival pickup', 1500.00, 1500.00, 0, 1);

INSERT OR IGNORE INTO cars (id, category_id, make, model, year, registration_number, colour, color, transmission, fuel_type, seats, daily_rate, mileage, status, primary_image_url) VALUES
(1, 1, 'Toyota', 'Axio', 2019, 'KDK 214A', 'White', 'White', 'automatic', 'petrol', 5, 4500.00, 61200, 'available', '/static/cars/axio.jpg'),
(2, 1, 'Mazda', 'Demio', 2020, 'KDM 882C', 'Silver', 'Silver', 'automatic', 'petrol', 5, 3800.00, 48300, 'available', '/static/cars/demio.jpg'),
(3, 1, 'Toyota', 'Aqua', 2021, 'KDP 117F', 'Blue', 'Blue', 'automatic', 'hybrid', 5, 4200.00, 33900, 'available', '/static/cars/aqua.jpg'),
(4, 2, 'Toyota', 'Land Cruiser Prado', 2022, 'KDS 450G', 'Forest green', 'Forest green', 'automatic', 'diesel', 7, 14500.00, 41000, 'available', '/static/cars/prado.jpg'),
(5, 2, 'Subaru', 'Forester', 2020, 'KDN 309B', 'Grey', 'Grey', 'automatic', 'petrol', 5, 8500.00, 57800, 'available', '/static/cars/forester.jpg'),
(6, 2, 'Nissan', 'X-Trail', 2019, 'KDJ 776D', 'Black', 'Black', 'manual', 'petrol', 7, 7800.00, 72100, 'maintenance', '/static/cars/xtrail.jpg'),
(7, 3, 'Mercedes-Benz', 'E-Class', 2022, 'KDT 001L', 'Obsidian black', 'Obsidian black', 'automatic', 'petrol', 5, 22000.00, 18500, 'available', '/static/cars/e-class.jpg'),
(8, 3, 'BMW', '5 Series', 2021, 'KDR 555X', 'Carbon black', 'Carbon black', 'automatic', 'hybrid', 5, 20000.00, 26400, 'available', '/static/cars/bmw-5-series.jpg'),
(9, 3, 'Range Rover', 'Velar', 2023, 'KDV 777X', 'Santorini black', 'Santorini black', 'automatic', 'diesel', 5, 28000.00, 9800, 'available', '/static/cars/velar.jpg'),
(10, 4, 'Toyota', 'HiAce', 2020, 'KDL 640K', 'White', 'White', 'manual', 'diesel', 14, 12000.00, 88200, 'available', '/static/cars/hiace.jpg'),
(12, 2, 'Toyota', 'TX', 2022, 'KDW 342Q', 'White', 'White', 'automatic', 'diesel', 7, 10000.00, 34240, 'available', '/static/cars/prado.jpg');

INSERT OR IGNORE INTO car_images (id, car_id, image_url, label, is_main) VALUES
(1, 1, '/static/cars/axio.jpg', 'front', 1),
(2, 2, '/static/cars/demio.jpg', 'front', 1),
(3, 3, '/static/cars/aqua.jpg', 'front', 1),
(4, 4, '/static/cars/prado.jpg', 'front', 1),
(5, 5, '/static/cars/forester.jpg', 'front', 1),
(6, 6, '/static/cars/xtrail.jpg', 'front', 1),
(7, 7, '/static/cars/e-class.jpg', 'front', 1),
(8, 8, '/static/cars/bmw-5-series.jpg', 'front', 1),
(9, 9, '/static/cars/velar.jpg', 'front', 1),
(10, 10, '/static/cars/hiace.jpg', 'front', 1),
(12, 12, '/static/cars/prado.jpg', 'front', 1);

INSERT OR IGNORE INTO users (id, full_name, email, phone, hashed_password, password_hash, role, licence_number, licence_expiry, is_active) VALUES
(1, 'Wanjiru Kamau', 'wanjiru@example.co.ke', '+254 712 345 678', '$2b$12$K1.q3W8k.HlqH0L5m7V3AedpWpYkH76PqJqN8R9H7M0S5k4l1G6m', '$2b$12$K1.q3W8k.HlqH0L5m7V3AedpWpYkH76PqJqN8R9H7M0S5k4l1G6m', 'customer', 'DL-0048213', '2028-12-31', 1),
(2, 'Admin User', 'admin@lasquadradoro.co.ke', '+254 700 000 001', '$2b$12$K1.q3W8k.HlqH0L5m7V3AedpWpYkH76PqJqN8R9H7M0S5k4l1G6m', '$2b$12$K1.q3W8k.HlqH0L5m7V3AedpWpYkH76PqJqN8R9H7M0S5k4l1G6m', 'admin', NULL, NULL, 1),
(3, 'Otieno Ouma', 'otieno@example.co.ke', '+254 722 111 222', '$2b$12$K1.q3W8k.HlqH0L5m7V3AedpWpYkH76PqJqN8R9H7M0S5k4l1G6m', '$2b$12$K1.q3W8k.HlqH0L5m7V3AedpWpYkH76PqJqN8R9H7M0S5k4l1G6m', 'customer', 'DL-0099120', '2028-06-30', 1);

INSERT OR IGNORE INTO bookings (id, reference, user_id, car_id, pickup_location, start_date, end_date, actual_return_date, daily_rate_snapshot, days, subtotal, extras_total, tax, total_amount, deposit, status, pickup_mileage, return_mileage) VALUES
(1, 'LSD-1041', 1, 4, 'JKIA - Jomo Kenyatta Intl. Airport', '2026-10-15', '2026-10-20', '2026-10-20', 14500.00, 5, 72500.00, 2000.00, 11920.00, 86420.00, 17284.00, 'completed', 40200, 41000),
(2, 'LSD-1042', 3, 7, 'Westlands - Sarit Centre Hub', '2026-11-14', '2026-11-19', NULL, 22000.00, 5, 110000.00, 0.00, 17600.00, 127600.00, 25520.00, 'active', 18100, NULL),
(3, 'LSD-1043', 3, 5, 'Karen - The Hub Karen', '2026-11-12', '2026-11-17', NULL, 8500.00, 5, 42500.00, 2500.00, 7200.00, 52200.00, 10440.00, 'active', 57200, NULL),
(4, 'LSD-1044', 1, 1, 'JKIA - Jomo Kenyatta Intl. Airport', '2026-11-19', '2026-11-23', NULL, 4500.00, 4, 18000.00, 3600.00, 3456.00, 25056.00, 5011.20, 'confirmed', NULL, NULL),
(5, 'LSD-1045', 3, 9, 'Westlands - Sarit Centre Hub', '2026-11-21', '2026-11-25', NULL, 28000.00, 4, 112000.00, 2500.00, 18320.00, 132820.00, 26564.00, 'pending', NULL, NULL),
(6, 'LSD-1046', 1, 8, 'JKIA - Jomo Kenyatta Intl. Airport', '2026-11-28', '2026-12-01', NULL, 20000.00, 3, 60000.00, 0.00, 9600.00, 69600.00, 13920.00, 'pending', NULL, NULL);

INSERT OR IGNORE INTO booking_extras (id, booking_id, extra_id, quantity, price_snapshot) VALUES
(1, 1, 2, 1, 400.00),
(2, 3, 1, 1, 500.00),
(3, 4, 1, 1, 500.00),
(4, 4, 2, 1, 400.00),
(5, 5, 3, 1, 2500.00);

INSERT OR IGNORE INTO payments (id, booking_id, amount, method, status, transaction_ref, paid_at) VALUES
(1, 1, 17284.00, 'mpesa', 'paid', 'QWE123RTY0', '2026-10-15 08:30:00'),
(2, 1, 69136.00, 'card', 'paid', 'CRD-88421', '2026-10-20 16:45:00'),
(3, 2, 25520.00, 'mpesa', 'paid', 'QWE456UIOP', '2026-11-14 09:15:00'),
(4, 3, 10440.00, 'bank_transfer', 'paid', 'BNK-20931', '2026-11-12 11:00:00'),
(5, 4, 5011.20, 'mpesa', 'paid', 'QWE789LKJH', '2026-11-15 14:20:00');

INSERT OR IGNORE INTO maintenance_records (id, car_id, description, start_date, end_date, cost) VALUES
(1, 6, 'Brake pad replacement and rotor skimming', '2026-11-10', '2026-11-18', 24500.00),
(2, 4, 'Full 40,000 km oil service and filter check', '2026-10-22', '2026-10-23', 18000.00);

INSERT OR REPLACE INTO meta (key, value) VALUES ('seq', 1046);
