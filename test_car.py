import unittest
import datetime
from src.car import Car


class TestCar(unittest.TestCase):

    def setUp(self):
        """Set up a new Car object for each test."""
        self.car = Car("TestMake", "TestModel", 2020, 50000, "TESTVIN", "TESTPLATE")

    def test_needs_maintenance_due_by_miles(self):
        """Test that service is due when mileage interval is exceeded."""
        # Log an oil change that was done a long time ago (mileage-wise)
        self.car.log_maintenance("oil change", 50, milage=44000, date="2024-01-01")
        # Current mileage is 50000, interval is 5000. 50000 - 44000 = 6000.
        self.assertTrue(self.car.needs_maintenance("oil change", verbose=False))

    def test_needs_maintenance_due_by_time(self):
        """Test that service is due when time interval is exceeded."""
        # Log an oil change done recently (mileage-wise) but long ago (time-wise)
        # Oil change interval is 180 days.
        old_date = (datetime.date.today() - datetime.timedelta(days=200)).isoformat()
        self.car.log_maintenance("oil change", 50, milage=49900, date=old_date)
        self.assertTrue(self.car.needs_maintenance("oil change", verbose=False))

    def test_needs_maintenance_not_due(self):
        """Test that service is not due when within intervals."""
        # Log a recent oil change
        recent_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        self.car.log_maintenance("oil change", 50, milage=49000, date=recent_date)
        self.assertFalse(self.car.needs_maintenance("oil change", verbose=False))

    def test_needs_maintenance_no_history(self):
        """Test that service is due if it has never been performed."""
        self.assertTrue(self.car.needs_maintenance("oil change", verbose=False))

    def test_get_upcoming_services(self):
        """Test the aggregation of all due services."""
        # This car has no history, so it should need everything.
        due = self.car.get_upcoming_services()
        self.assertIn("oil change", due)
        self.assertIn("tire rotation", due)

        # After an oil change, it should no longer be in the list.
        self.car.log_maintenance("oil change", 50, milage=50000)
        due_after_service = self.car.get_upcoming_services()
        self.assertNotIn("oil change", due_after_service)
        self.assertIn("tire rotation", due_after_service)

    def test_resolve_diagnostic(self):
        """Test resolving an open diagnostic issue."""
        self.car.log_diagnostic("Test issue")
        open_issues_before = [
            log for log in self.car.diagnostic_logs if log["status"] == "open"
        ]
        self.assertEqual(len(open_issues_before), 1)

        self.car.resolve_diagnostic(0, "Resolved it.")
        open_issues_after = [
            log for log in self.car.diagnostic_logs if log["status"] == "open"
        ]
        self.assertEqual(len(open_issues_after), 0)

    def test_log_maintenance_updates_mileage(self):
        """Test that logging a service with higher mileage updates the car's main mileage."""
        self.assertEqual(self.car.milage, 50000)
        self.car.log_maintenance("oil change", 50, milage=51000)
        self.assertEqual(self.car.milage, 51000)

    def test_log_maintenance_does_not_lower_mileage(self):
        """Test that logging a service with lower mileage does not decrease the car's main mileage."""
        self.assertEqual(self.car.milage, 50000)
        self.car.log_maintenance(
            "oil change", 50, milage=49000
        )  # e.g., correcting a past entry
        self.assertEqual(self.car.milage, 50000)

    def test_serialization_deserialization(self):
        """Test that a car can be converted to a dict and back to an identical object."""
        self.car.log_diagnostic("Test issue")
        self.car.log_maintenance("oil change", 50, milage=45000)

        car_dict = self.car.to_dict()
        rehydrated_car = Car.from_dict(car_dict)

        self.assertEqual(self.car.to_dict(), rehydrated_car.to_dict())


if __name__ == "__main__":
    unittest.main()
