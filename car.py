import datetime

class Car:
    def __init__(self, make, model, year, mileage, vin):
        self.make = make
        self.model = model
        self.year = year
        self.mileage = mileage
        self.vin = vin
        self.maintenance_logs = []

    def add_mileage(self, miles):
        if miles > 0:
            self.mileage += miles
        else:
            raise ValueError("Miles must be positive")

    def log_maintenance(self, service_type, cost, date=None):
        if date is None:
            date = datetime.date.today().isoformat()

        log = {
            "service": service_type,
            "cost": cost,
            "mileage": self.mileage,
            "date": date
        }

        self.maintenance_logs.append(log)

    def get_maintenance_history(self):
        return sorted(self.maintenance_logs, key=lambda x: x['date'])

    def needs_maintenance(self, service_interval):
        if not self.maintenance_logs:
            return True

        last_service = max(self.maintenance_logs, key=lambda x: x['date'])

        # Check mileage gap
        mileage_gap = self.mileage - last_service['mileage']
        if mileage_gap >= service_interval:
            return True

        # Check time gap
        last_service_date = datetime.datetime.strptime(last_service['date'], "%Y-%m-%d").date()
        days_since_service = (datetime.date.today() - last_service_date).days
        if days_since_service > 180:
            return True

        return False

    def __str__(self):
        return f"{self.year} {self.make} {self.model} (VIN: {self.vin}, Mileage: {self.mileage})"
