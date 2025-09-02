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
        license_plate TEXT NOT NULL UNIQUE
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
            
    return car_objectsef check_vin_exists(vin, exclude_id=None):
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
        "INSERT INTO cars (make, model, year, milage, vin, license_plate) VALUES (?, ?, ?, ?, ?, ?)",
        (car.make, car.model, car.year, car.milage, car.vin, car.license_plate)
    )
    car.id = cursor.lastrowid
    conn.commit()
    conn.close()

def update_car_details(car):
    """Updates a car's editable details (mileage, license plate) in the database."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE cars SET milage = ?, license_plate = ? WHERE id = ?",
        (car.milage, car.license_plate, car.id)
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
    conn.execute(
        "INSERT INTO maintenance_logs (car_id, service, cost, milage, date) VALUES (?, ?, ?, ?, ?)",
        (car_id, log['service'], log['cost'], log['milage'], log['date'])
    )
    conn.commit()
    conn.close()

def add_diagnostic_log(car_id, log):
    """Adds a diagnostic log to the database."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO diagnostic_logs (car_id, description, code, date_logged, status) VALUES (?, ?, ?, ?, ?)",
        (car_id, log['description'], log['code'], log['date_logged'], log['status'])
    )
    conn.commit()
    conn.close()

def resolve_diagnostic_log(car_id, log):
    """Updates a diagnostic log to 'resolved' in the database."""
    conn = get_db_connection()
    # Find the specific log by attributes that are effectively unique for an open issue
    conn.execute(
        """UPDATE diagnostic_logs 
           SET status = ?, resolution = ?, resolved_date = ?
           WHERE car_id = ? AND description = ? AND date_logged = ? AND status = 'open'""",
        (log['status'], log['resolution'], log['resolved_date'], car_id, log['description'], log['date_logged'])
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
            "INSERT INTO cars (id, make, model, year, milage, vin, license_plate) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (car_data['id'], car_data['make'], car_data['model'], car_data['year'], car_data['milage'], car_data['vin'], car_data['license_plate'])
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