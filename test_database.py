import unittest
import os
import sqlite3
from src.car import Car
import src.database as db


class TestDatabase(unittest.TestCase):

    def setUp(self):
        """
        Set up a temporary database for each test.
        This method is called before each test function is executed.
        """
        self.test_db_file = "test_db.sqlite"
        # Monkey-patch the DB_FILE constant in the database module
        # to ensure all db functions use our temporary test database.
        db.DB_FILE = self.test_db_file

        # Initialize the schema in the new temporary database
        db.init_db()

    def tearDown(self):
        """
        Clean up by removing the temporary database file after each test.
        This method is called after each test function is executed.
        """
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def test_add_and_load_car(self):
        """Test adding a car and loading it back from the database."""
        car = Car("Toyota", "Corolla", 2021, 30000, "VIN1", "PLATE1")
        db.add_car(car)

        # The car object should now have an ID assigned by the database.
        self.assertIsNotNone(car.id)
        self.assertEqual(car.id, 1)

        loaded_cars = db.load_all_cars()
        self.assertEqual(len(loaded_cars), 1)
        self.assertEqual(loaded_cars[0].vin, "VIN1")

    def test_update_car_details(self):
        """Test updating a car's details in the database."""
        car = Car("Honda", "Civic", 2019, 50000, "VIN2", "PLATE2")
        db.add_car(car)

        # Update the object in memory
        car.milage = 55000
        car.license_plate = "NEWPLATE"
        db.update_car_details(car)

        loaded_cars = db.load_all_cars()
        updated_car = loaded_cars[0]

        self.assertEqual(updated_car.milage, 55000)
        self.assertEqual(updated_car.license_plate, "NEWPLATE")

    def test_delete_car_and_cascade(self):
        """Test that deleting a car also deletes its associated logs."""
        car = Car("Ford", "Focus", 2018, 70000, "VIN3", "PLATE3")
        db.add_car(car)

        # Add logs associated with the car
        maint_log = car.log_maintenance("oil change", 50)
        diag_log = car.log_diagnostic("Rattling noise")
        db.add_maintenance_log(car.id, maint_log)
        db.add_diagnostic_log(car.id, diag_log)

        # Delete the car
        db.delete_car_by_id(car.id)

        # Verify the car is gone
        loaded_cars = db.load_all_cars()
        self.assertEqual(len(loaded_cars), 0)

        # Verify logs are also gone by checking the tables directly
        conn = sqlite3.connect(self.test_db_file)
        maint_count = conn.execute("SELECT COUNT(*) FROM maintenance_logs").fetchone()[
            0
        ]
        diag_count = conn.execute("SELECT COUNT(*) FROM diagnostic_logs").fetchone()[0]
        conn.close()

        self.assertEqual(maint_count, 0)
        self.assertEqual(diag_count, 0)

    def test_add_and_resolve_logs(self):
        """Test adding and resolving diagnostic and maintenance logs."""
        car = Car("Nissan", "Titan", 2022, 15000, "VIN4", "PLATE4")
        db.add_car(car)

        # Add logs
        maint_log = car.log_maintenance("tire rotation", 40)
        diag_log = car.log_diagnostic("Check engine light")
        db.add_maintenance_log(car.id, maint_log)
        db.add_diagnostic_log(car.id, diag_log)

        # Resolve the diagnostic log
        resolved_log = car.resolve_diagnostic(0, "Replaced O2 sensor.")
        db.resolve_diagnostic_log(resolved_log)

        loaded_car = db.load_all_cars()[0]
        self.assertEqual(len(loaded_car.maintenance_logs), 1)
        self.assertEqual(loaded_car.maintenance_logs[0]["service"], "tire rotation")
        self.assertEqual(len(loaded_car.diagnostic_logs), 1)
        self.assertEqual(loaded_car.diagnostic_logs[0]["status"], "resolved")
        self.assertEqual(
            loaded_car.diagnostic_logs[0]["resolution"], "Replaced O2 sensor."
        )

    def test_reset_database(self):
        """Test that reset_database correctly wipes and repopulates the database."""
        # Initial state with one car
        car1 = Car("Subaru", "Outback", 2023, 5000, "VIN5", "PLATE5")
        db.add_car(car1)

        # New state (snapshot) with a different car
        car2 = Car(
            "Mazda", "CX-5", 2022, 12000, "VIN6", "PLATE6", id=10
        )  # Use a distinct ID
        snapshot = [car2.to_dict()]

        db.reset_database(snapshot)
        loaded_cars = db.load_all_cars()

        self.assertEqual(len(loaded_cars), 1)
        self.assertEqual(loaded_cars[0].vin, "VIN6")


if __name__ == "__main__":
    unittest.main()
