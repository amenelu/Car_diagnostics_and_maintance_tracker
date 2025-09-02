import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import database as db
from car import Car

# Get the absolute path of the directory containing this file
_basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize the Flask app
app = Flask(__name__,
            static_folder=os.path.join(_basedir, 'static'),
            template_folder=os.path.join(_basedir, 'templates'))
app.secret_key = 'supersecretkey' # Needed for flashing messages

# Initialize the database
db.init_db()

@app.route('/')
def index():
    """Home page: Lists all cars."""
    cars = db.load_all_cars()
    return render_template('index.html', cars=cars)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    """Shows a detailed view of a single car."""
    car = db.load_car_by_id(car_id)
    if not car:
        return "Car not found", 404
    
    # Reuse the logic from the CLI to get upcoming services
    upcoming_services = car.get_upcoming_services()
    open_issues = [log for log in car.get_diagnostic_history() if log['status'] == 'open']

    return render_template('car_detail.html', car=car, upcoming_services=upcoming_services, open_issues=open_issues)

@app.route('/car/add', methods=['GET', 'POST'])
def add_car():
    """Handles adding a new car."""
    if request.method == 'POST':
        # Basic validation
        if db.check_vin_exists(request.form['vin'].upper()):
            flash(f"Error: VIN {request.form['vin']} already exists.", 'error')
            return render_template('car_form.html', car=request.form)
        if db.check_license_plate_exists(request.form['license_plate'].upper()):
            flash(f"Error: License plate {request.form['license_plate']} already exists.", 'error')
            return render_template('car_form.html', car=request.form)

        new_car = Car(
            make=request.form['make'],
            model=request.form['model'],
            year=int(request.form['year']),
            milage=int(request.form['milage']),
            vin=request.form['vin'].upper(),
            license_plate=request.form['license_plate'].upper()
        )
        db.add_car(new_car)
        flash(f"Car '{new_car.make} {new_car.model}' added successfully!", 'success')
        return redirect(url_for('index'))
    
    # For GET request, show the form
    return render_template('car_form.html', car=None)

@app.route('/car/<int:car_id>/edit', methods=['GET', 'POST'])
def edit_car(car_id):
    """Handles editing an existing car."""
    car = db.load_car_by_id(car_id)
    if not car:
        return "Car not found", 404

    if request.method == 'POST':
        # Update car object from form data
        car.milage = int(request.form['milage'])
        car.license_plate = request.form['license_plate'].upper()
        
        db.update_car_details(car)
        flash(f"Car '{car.make} {car.model}' updated successfully!", 'success')
        return redirect(url_for('car_detail', car_id=car.id))

    # For GET request, show the form pre-filled with car data
    return render_template('car_form.html', car=car)

@app.route('/car/<int:car_id>/delete', methods=['POST'])
def delete_car(car_id):
    """Handles deleting a car."""
    car = db.load_car_by_id(car_id)
    if car:
        db.delete_car_by_id(car_id)
        flash(f"Car '{car.make} {car.model}' has been deleted.", 'success')
    return redirect(url_for('index'))

@app.route('/car/<int:car_id>/add_maintenance', methods=['POST'])
def add_maintenance_log(car_id):
    """Adds a maintenance log to a car."""
    car = db.load_car_by_id(car_id)
    if car:
        new_log = car.log_maintenance(
            service_type=request.form['service'],
            cost=float(request.form['cost']),
            milage=int(request.form['milage']),
            date=request.form['date']
        )
        db.add_maintenance_log(car.id, new_log)
        db.update_car_details(car) # Update mileage if it changed
        flash("Maintenance record added successfully!", 'success')
    return redirect(url_for('car_detail', car_id=car_id))

@app.route('/car/<int:car_id>/add_diagnostic', methods=['POST'])
def add_diagnostic_log(car_id):
    """Adds a diagnostic log to a car."""
    car = db.load_car_by_id(car_id)
    if car:
        new_log = car.log_diagnostic(
            description=request.form['description'],
            code=request.form.get('code') or None,
            date=datetime.date.today().isoformat()
        )
        db.add_diagnostic_log(car.id, new_log)
        flash("Diagnostic issue logged successfully!", 'success')
    return redirect(url_for('car_detail', car_id=car_id))

@app.route('/car/<int:car_id>/resolve_diagnostic/<int:log_id>', methods=['POST'])
def resolve_diagnostic(car_id, log_id):
    """Resolves a diagnostic issue."""
    car = db.load_car_by_id(car_id)
    log_to_resolve = next((log for log in car.diagnostic_logs if log['id'] == log_id), None)

    if car and log_to_resolve:
        resolution = request.form['resolution']
        log_to_resolve['status'] = 'resolved'
        log_to_resolve['resolution'] = resolution
        log_to_resolve['resolved_date'] = datetime.date.today().isoformat()
        
        db.resolve_diagnostic_log(log_to_resolve)
        flash("Diagnostic issue has been resolved.", 'success')

    return redirect(url_for('car_detail', car_id=car_id))

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=True)