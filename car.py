import datetime

class Car:
    def __init__(self, make, model, year, milage, vin):
        self.make = make
        self.model = model
        self.year = year
        self.milage = milage
        self.vin = vin
        self.maintenance_logs = []

    def add_milage(self, miles):
        if miles > 0:
            self.milage += miles
        else:
            raise ValueError("Miles must be positive")

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

    def get_maintenance_history(self):
        return sorted(self.maintenance_logs, key=lambda x: x['date'])

    def needs_maintenance(self, service_interval, current_mileage=None):
        if not self.maintenance_logs:
            return True

        # Use the provided current_mileage for the check, otherwise default to the car's last known mileage.
        effective_mileage = current_mileage if current_mileage is not None else self.milage

        last_service = max(self.maintenance_logs, key=lambda x: x['date'])

        # Check milage gap
        milage_gap = effective_mileage - last_service['milage']
        if milage_gap >= service_interval:
            return True

        # Check time gap
        last_service_date = datetime.datetime.strptime(last_service['date'], "%Y-%m-%d").date()
        days_since_service = (datetime.date.today() - last_service_date).days
        if days_since_service > 180:
            return True

        return False

    def __str__(self):
        return f"{self.year} {self.make} {self.model} (VIN: {self.vin}, milage: {self.milage})"
