import datetime

class Car:
    def __init__(self, make, model, year, milage, vin):
        self.make = make
        self.model = model
        self.year = year
        self.milage = milage
        self.vin = vin
        self.maintence_logs = []

    def add_milage(self, miles):
        if miles > 0:
            self.milage += miles
        else:
            raise ValueError("Miles must be positive")

    def log_maintence(self, service_type, cost,milage=None, date=None):
        if date is None:
            date = datetime.date.today().isoformat()

        log = {
            "service": service_type,
            "cost": cost,
            "milage": milage if milage is not None else self.milage,
            "date": date
        }

        self.maintence_logs.append(log)

    def get_maintence_history(self):
        return sorted(self.maintence_logs, key=lambda x: x['date'])

    def needs_maintence(self, service_interval):
        if not self.maintence_logs:
            return True

        last_service = max(self.maintence_logs, key=lambda x: x['date'])

        # Check milage gap
        milage_gap = self.milage - last_service['milage']
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
