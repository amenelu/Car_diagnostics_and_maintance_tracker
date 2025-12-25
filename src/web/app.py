import datetime
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import src.database as db
from src.car import Car, SERVICE_INTERVALS
from src.search_filter import _apply_filters
from werkzeug.utils import secure_filename

# Get the absolute path of the directory containing this file
_basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize the Flask app
app = Flask(
    __name__,
    static_folder=os.path.join(_basedir, "static"),
    template_folder=os.path.join(_basedir, "templates"),
)
app.secret_key = "supersecretkey"  # Needed for flashing messages

# Configure the upload folder
UPLOAD_FOLDER = os.path.join(_basedir, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database
db.init_db()


@app.route("/")
def index():
    """Home page: Lists all cars."""
    # Get filter criteria from query parameters to pass back to the template
    form_values = {
        "make": request.args.get("make", "").strip(),
        "model": request.args.get("model", "").strip(),
        "min_year": request.args.get("min_year", ""),
        "max_year": request.args.get("max_year", ""),
        "max_mileage": request.args.get("max_mileage", ""),
        "has_open_issues": request.args.get("has_open_issues", ""),
        "needs_service_type": request.args.get("needs_service_type", "").strip(),
    }

    # Build a dictionary of only the active filters to pass to the logic
    active_filters = {}
    if form_values["make"]:
        active_filters["make"] = form_values["make"]
    if form_values["model"]:
        active_filters["model"] = form_values["model"]
    if form_values["min_year"]:
        active_filters["min_year"] = int(form_values["min_year"])
    if form_values["max_year"]:
        active_filters["max_year"] = int(form_values["max_year"])
    if form_values["max_mileage"]:
        active_filters["max_mileage"] = int(form_values["max_mileage"])
    if form_values["has_open_issues"] == "y":
        active_filters["has_open_issues"] = True
    if form_values["needs_service_type"]:
        active_filters["needs_service_type"] = form_values["needs_service_type"]

    all_cars = db.load_all_cars()

    if active_filters:
        filtered_cars = _apply_filters(all_cars, active_filters)
    else:
        filtered_cars = all_cars

    # If the request is an AJAX request, return only the list partial
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("_car_list.html", cars=filtered_cars)

    # Otherwise, for a full page load, return the whole page
    return render_template(
        "index.html",
        cars=filtered_cars,
        filters=form_values,
        service_intervals=SERVICE_INTERVALS.keys(),
    )


@app.route("/car/<int:car_id>")
def car_detail(car_id):
    """Shows a detailed view of a single car."""
    car = db.load_car_by_id(car_id)
    if not car:
        return "Car not found", 404

    # Reuse the logic from the CLI to get upcoming services
    upcoming_services = car.get_upcoming_services()
    open_issues = [
        log for log in car.get_diagnostic_history() if log["status"] == "open"
    ]
    today_date = datetime.date.today().isoformat()

    return render_template(
        "car_detail.html",
        car=car,
        upcoming_services=upcoming_services,
        open_issues=open_issues,
        today_date=today_date,
    )


@app.route("/car/add", methods=["GET", "POST"])
def add_car():
    """Handles adding a new car."""
    if request.method == "POST":
        # Basic validation
        if db.check_vin_exists(request.form["vin"].upper()):
            flash(f"Error: VIN {request.form['vin']} already exists.", "error")
            return render_template("car_form.html", car=request.form)
        if db.check_license_plate_exists(request.form["license_plate"].upper()):
            flash(
                f"Error: License plate {request.form['license_plate']} already exists.",
                "error",
            )
            return render_template("car_form.html", car=request.form)

        new_car = Car(
            make=request.form["make"],
            model=request.form["model"],
            year=int(request.form["year"]),
            milage=int(request.form["milage"]),
            vin=request.form["vin"].upper(),
            license_plate=request.form["license_plate"].upper(),
        )
        db.add_car(new_car)
        flash(f"Car '{new_car.make} {new_car.model}' added successfully!", "success")
        return redirect(url_for("index"))

    # For GET request, show the form
    return render_template("car_form.html", car=None)


@app.route("/car/<int:car_id>/edit", methods=["GET", "POST"])
def edit_car(car_id):
    """Handles editing an existing car."""
    car = db.load_car_by_id(car_id)
    if not car:
        return "Car not found", 404

    if request.method == "POST":
        # Update car object from form data
        car.milage = int(request.form["milage"])
        car.license_plate = request.form["license_plate"].upper()

        # Handle 'before' image upload
        if "image_before" in request.files:
            file = request.files["image_before"]
            if file.filename != "":
                # Generate a unique, secure filename
                filename = f"{car.vin}-before-{int(time.time())}-{secure_filename(file.filename)}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                car.image_before = filename

        # Handle 'after' image upload
        if "image_after" in request.files:
            file = request.files["image_after"]
            if file.filename != "":
                filename = f"{car.vin}-after-{int(time.time())}-{secure_filename(file.filename)}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                car.image_after = filename

        db.update_car_details(car)
        flash(f"Car '{car.make} {car.model}' updated successfully!", "success")
        return redirect(url_for("car_detail", car_id=car.id))

    # For GET request, show the form pre-filled with car data
    return render_template("car_form.html", car=car)


@app.route("/car/<int:car_id>/delete", methods=["POST"])
def delete_car(car_id):
    """Handles deleting a car."""
    car = db.load_car_by_id(car_id)
    if car:
        db.delete_car_by_id(car_id)
        flash(f"Car '{car.make} {car.model}' has been deleted.", "success")
    return redirect(url_for("index"))


@app.route("/car/<int:car_id>/add_maintenance", methods=["POST"])
def add_maintenance_log(car_id):
    """Adds a maintenance log to a car."""
    car = db.load_car_by_id(car_id)
    if car:
        new_log = car.log_maintenance(
            service_type=request.form["service"],
            cost=float(request.form["cost"]),
            milage=int(request.form["milage"]),
            date=request.form["date"],
        )
        db.add_maintenance_log(car.id, new_log)
        db.update_car_details(car)  # Update mileage if it changed
        flash("Maintenance record added successfully!", "success")
    return redirect(url_for("car_detail", car_id=car_id))


@app.route("/car/<int:car_id>/add_diagnostic", methods=["POST"])
def add_diagnostic_log(car_id):
    """Adds a diagnostic log to a car."""
    car = db.load_car_by_id(car_id)
    if car:
        new_log = car.log_diagnostic(
            description=request.form["description"],
            code=request.form.get("code") or None,
            date=datetime.date.today().isoformat(),
        )
        db.add_diagnostic_log(car.id, new_log)
        flash("Diagnostic issue logged successfully!", "success")
    return redirect(url_for("car_detail", car_id=car_id))


@app.route("/car/<int:car_id>/resolve_diagnostic/<int:log_id>", methods=["POST"])
def resolve_diagnostic(car_id, log_id):
    """Resolves a diagnostic issue."""
    car = db.load_car_by_id(car_id)
    log_to_resolve = next(
        (log for log in car.diagnostic_logs if log["id"] == log_id), None
    )

    if car and log_to_resolve:
        resolution = request.form["resolution"]
        log_to_resolve["status"] = "resolved"
        log_to_resolve["resolution"] = resolution
        log_to_resolve["resolved_date"] = datetime.date.today().isoformat()

        db.resolve_diagnostic_log(log_to_resolve)
        flash("Diagnostic issue has been resolved.", "success")

    return redirect(url_for("car_detail", car_id=car_id))


if __name__ == "__main__":
    # Run the app in debug mode for development
    app.run(debug=True, port=8000)
