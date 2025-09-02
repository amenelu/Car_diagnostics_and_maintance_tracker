import sqlite3
from car import Car

DB_FILE = "car_tracker.db"

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Enable foreign key support, which is crucial for data integrity
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Car Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        milage INTEGER NOT NULL,
        vin TEXT NOT NULL UNIQUE,
        license_plate TEXT NOT NULL UNIQUE,
        image_before TEXT,
        image_after TEXT
    )
    """)

    # Maintenance Logs Table with a foreign key to the cars table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER NOT NULL,
        service TEXT NOT NULL,
        cost REAL NOT NULL,
        milage INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (car_id) REFERENCES cars (id) ON DELETE CASCADE
    )
    """)

    # Diagnostic Logs Table with a foreign key to the cars table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnostic_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        code TEXT,
        date_logged TEXT NOT NULL,
        status TEXT NOT NULL,
        resolution TEXT,
        resolved_date TEXT,
        FOREIGN KEY (car_id) REFERENCES cars (id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

def load_all_cars():
    """Loads all cars and their associated logs from the database."""
    conn = get_db_connection()
    
    # Fetch all data in fewer queries to avoid the N+1 query problem
    cars_rows = conn.execute("SELECT * FROM cars ORDER BY make, model").fetchall()
    maint_logs_rows = conn.execute("SELECT * FROM maintenance_logs").fetchall()
    diag_logs_rows = conn.execute("SELECT * FROM diagnostic_logs").fetchall()
    
    conn.close()

    cars_map = {}
    car_objects = []

    # Create Car objects and map them by their ID
    for row in cars_rows:
        car = Car.from_dict(dict(row))
        cars_map[car.id] = car
        car_objects.append(car)

    # Attach maintenance logs to the correct car object
    for row in maint_logs_rows:
        if row['car_id'] in cars_map:
            cars_map[row['car_id']].maintenance_logs.append(dict(row))

    # Attach diagnostic logs to the correct car object
    for row in diag_logs_rows:
        if row['car_id'] in cars_map:
            cars_map[row['car_id']].diagnostic_logs.append(dict(row))
            
    return car_objects

def load_car_by_id(car_id):
    """Loads a single car and its logs from the database by its ID."""
    conn = get_db_connection()
    car_row = conn.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
    
    if not car_row:
        conn.close()
        return None

    car = Car.from_dict(dict(car_row))

    maint_logs_rows = conn.execute("SELECT * FROM maintenance_logs WHERE car_id = ?", (car_id,)).fetchall()
    for row in maint_logs_rows:
        car.maintenance_logs.append(dict(row))

    diag_logs_rows = conn.execute("SELECT * FROM diagnostic_logs WHERE car_id = ?", (car_id,)).fetchall()
    for row in diag_logs_rows:
        car.diagnostic_logs.append(dict(row))
        
    conn.close()
    return car

def check_vin_exists(vin, exclude_id=None):
    """Checks if a VIN exists in the database, optionally excluding a car ID."""
    conn = get_db_connection()
    query = "SELECT id FROM cars WHERE vin = ?"
    params = [vin]
    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)
    result = conn.execute(query, params).fetchone()
    conn.close()
    return result is not None

def check_license_plate_exists(plate, exclude_id=None):
    """Checks if a license plate exists, optionally excluding a car ID."""
    conn = get_db_connection()
    query = "SELECT id FROM cars WHERE license_plate = ?"
    params = [plate]
    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)
    result = conn.execute(query, params).fetchone()
    conn.close()
    return result is not None

def add_car(car):
    """Adds a car to the database and updates the car object with its new ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cars (make, model, year, milage, vin, license_plate, image_before, image_after) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (car.make, car.model, car.year, car.milage, car.vin, car.license_plate, car.image_before, car.image_after)
    )
    car.id = cursor.lastrowid
    conn.commit()
    conn.close()

def update_car_details(car):
    """Updates a car's editable details (mileage, license plate) in the database."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE cars SET milage = ?, license_plate = ?, image_before = ?, image_after = ? WHERE id = ?",
        (car.milage, car.license_plate, car.image_before, car.image_after, car.id)
    )
    conn.commit()
    conn.close()

def delete_car_by_id(car_id):
    """Deletes a car and its associated logs from the database by its ID."""
    conn = get_db_connection()
    conn.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()

def add_maintenance_log(car_id, log):
    """Adds a maintenance log to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO maintenance_logs (car_id, service, cost, milage, date) VALUES (?, ?, ?, ?, ?)",
        (car_id, log['service'], log['cost'], log['milage'], log['date'])
    )
    log['id'] = cursor.lastrowid # Add the ID to the dictionary
    conn.commit()
    conn.close()

def add_diagnostic_log(car_id, log):
    """Adds a diagnostic log to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diagnostic_logs (car_id, description, code, date_logged, status) VALUES (?, ?, ?, ?, ?)",
        (car_id, log['description'], log['code'], log['date_logged'], log['status'])
    )
    log['id'] = cursor.lastrowid # Add the ID to the dictionary
    conn.commit()
    conn.close()

def resolve_diagnostic_log(log):
    """Updates a diagnostic log to 'resolved' in the database."""
    conn = get_db_connection()
    conn.execute(
        """UPDATE diagnostic_logs 
           SET status = ?, resolution = ?, resolved_date = ?
           WHERE id = ?""",
        (log['status'], log['resolution'], log['resolved_date'], log['id'])
    )
    conn.commit()
    conn.close()

def reset_database(snapshot):
    """Wipes the database and repopulates it from a snapshot. Used for Undo/Redo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing data in the correct order to respect foreign keys
    cursor.execute("DELETE FROM maintenance_logs")
    cursor.execute("DELETE FROM diagnostic_logs")
    cursor.execute("DELETE FROM cars")
    
    # Re-populate all tables from the snapshot
    for car_data in snapshot:
        cursor.execute(
            "INSERT INTO cars (id, make, model, year, milage, vin, license_plate, image_before, image_after) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (car_data['id'], car_data['make'], car_data['model'], car_data['year'], car_data['milage'], car_data['vin'], car_data['license_plate'], car_data.get('image_before'), car_data.get('image_after'))
        )
        car_id = car_data['id']
        
        for log in car_data.get('maintenance_logs', []):
            cursor.execute(
                "INSERT INTO maintenance_logs (car_id, service, cost, milage, date) VALUES (?, ?, ?, ?, ?)",
                (car_id, log['service'], log['cost'], log['milage'], log['date'])
            )
            
        for log in car_data.get('diagnostic_logs', []):
            cursor.execute(
                "INSERT INTO diagnostic_logs (car_id, description, code, date_logged, status, resolution, resolved_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (car_id, log['description'], log['code'], log['date_logged'], log['status'], log.get('resolution'), log.get('resolved_date'))
            )
            
    conn.commit()
    conn.close()