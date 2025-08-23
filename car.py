import datetime

# Define standard service intervals (miles, days). A value of None means no limit.
SERVICE_INTERVALS = {
    "oil change": (5000, 180),
    "tire rotation": (7500, 365),
    "brake inspection": (12000, 365),
    "timing belt": (100000, 2555) # ~7 years
}
class Car:
    def __init__(self, make, model, year, milage, vin):
        self.make = make
        self.model = model
        self.year = year
        self.milage = milage
        self.vin = vin
        self.maintenance_logs = []
        self.diagnostic_logs = []

    def log_maintenance(self, service_type, cost,milage=None, date=None):
        if date is None:
            date = datetime.date.today().isoformat()

        # Determine the mileage for this specific log entry
        log_milage = milage if milage is not None else self.milage

        log = {
            "service": service_type,
            "cost": cost,
            "milage": log_milage,
            "date": date
        }

        self.maintenance_logs.append(log)

        # Also update the car's primary mileage if this service record's mileage is higher
        if log_milage > self.milage:
            self.milage = log_milage

    def log_diagnostic(self, description, code=None, date=None):
        """Logs a new diagnostic issue."""
        if date is None:
            date = datetime.date.today().isoformat()

        log = {
            "description": description,
            "code": code, # e.g., P0420
            "date_logged": date,
            "status": "open", # Can be 'open' or 'resolved'
            "resolution": None,
            "resolved_date": None
        }
        self.diagnostic_logs.append(log)

    def resolve_diagnostic(self, issue_index, resolution_notes):
        """Marks a diagnostic issue as resolved."""
        open_issues = [log for log in self.diagnostic_logs if log['status'] == 'open']
        if 0 <= issue_index < len(open_issues):
            issue_to_resolve = open_issues[issue_index]
            issue_to_resolve['status'] = 'resolved'
            issue_to_resolve['resolution'] = resolution_notes
            issue_to_resolve['resolved_date'] = datetime.date.today().isoformat()
            return True
        return False

    def get_maintenance_history(self):
        return sorted(self.maintenance_logs, key=lambda x: x['date'])

    def get_diagnostic_history(self):
        return sorted(self.diagnostic_logs, key=lambda x: x['date_logged'])

    def needs_maintenance(self, service_type, current_mileage=None):
        if service_type not in SERVICE_INTERVALS:
            print(f"Warning: Unknown service type '{service_type}'. Cannot determine interval.")
            return False

        mile_interval, day_interval = SERVICE_INTERVALS[service_type]

        # Find the last time this specific service was performed
        relevant_logs = [log for log in self.maintenance_logs if log['service'].lower() == service_type.lower()]

        if not relevant_logs:
            print(f"No record of a '{service_type}' found.")
            return True

        # Use the provided current_mileage for the check, otherwise default to the car's last known mileage.
        effective_mileage = current_mileage if current_mileage is not None else self.milage

        last_service = max(relevant_logs, key=lambda x: x['date'])

        # Check mileage gap if an interval is set
        if mile_interval is not None:
            milage_gap = effective_mileage - last_service['milage']
            if milage_gap >= mile_interval:
                print(f"Reason: Mileage since last '{service_type}' is {milage_gap} miles (Interval: {mile_interval}).")
                return True

        # Check time gap if an interval is set
        if day_interval is not None:
            last_service_date = datetime.datetime.strptime(last_service['date'], "%Y-%m-%d").date()
            days_since_service = (datetime.date.today() - last_service_date).days
            if days_since_service > day_interval:
                print(f"Reason: It has been {days_since_service} days since last '{service_type}' (Interval: {day_interval}).")
                return True

        return False

    def __str__(self):
        open_issues = sum(1 for log in self.diagnostic_logs if log['status'] == 'open')
        issue_str = f", {open_issues} open issues" if open_issues > 0 else ""
        return f"{self.year} {self.make} {self.model} (VIN: {self.vin}, Mileage: {self.milage}{issue_str})"

    def to_dict(self):  
        """Converts the Car object to a dictionary for JSON serialization."""
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "milage": self.milage,
            "vin": self.vin,
            "maintenance_logs": self.maintenance_logs,
            "diagnostic_logs": self.diagnostic_logs,
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Car object from a dictionary."""
        car = cls(
            make=data["make"], model=data["model"], year=data["year"], milage=data["milage"], vin=data["vin"]
        )
        car.maintenance_logs = data.get("maintenance_logs", [])
        car.diagnostic_logs = data.get("diagnostic_logs", [])
        return car
