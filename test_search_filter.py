import unittest
from car import Car
from search_filter import _apply_filters # We test the internal logic function directly

class TestSearchFilter(unittest.TestCase):

    def setUp(self):
        self.car1 = Car("Toyota", "Camry", 2018, 78500, "VIN001", "ABC-123")
        self.car2 = Car("Ford", "Mustang", 2022, 15200, "VIN002", "XYZ-789")
        self.car3 = Car("Honda", "CR-V", 2020, 45000, "VIN003", "DEF-456")
        
        # Add an open issue to car2
        self.car2.log_diagnostic("Check engine light")
        
        # Add service history to car1 so it doesn't need an oil change
        self.car1.log_maintenance("oil change", 75, milage=78000)

        self.cars = [self.car1, self.car2, self.car3]

    def test_filter_by_make(self):
        filters = {"make": "Ford"}
        results = _apply_filters(self.cars, filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].vin, "VIN002")

    def test_filter_by_year_range(self):
        filters = {"min_year": 2019, "max_year": 2021}
        results = _apply_filters(self.cars, filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].vin, "VIN003")

    def test_filter_by_max_mileage(self):
        filters = {"max_mileage": 50000}
        results = _apply_filters(self.cars, filters)
        self.assertEqual(len(results), 2)
        vins = {car.vin for car in results}
        self.assertIn("VIN002", vins)
        self.assertIn("VIN003", vins)

    def test_filter_by_open_issues(self):
        filters = {"has_open_issues": True}
        results = _apply_filters(self.cars, filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].vin, "VIN002")

    def test_filter_by_needs_service(self):
        # car2 and car3 need an oil change, car1 does not
        filters = {"needs_service_type": "oil change"}
        results = _apply_filters(self.cars, filters)
        self.assertEqual(len(results), 2)
        vins = {car.vin for car in results}
        self.assertIn("VIN002", vins)
        self.assertIn("VIN003", vins)

    def test_combined_filter(self):
        # Find cars made after 2019 with less than 50000 miles
        filters = {"min_year": 2019, "max_mileage": 50000}
        results = _apply_filters(self.cars, filters)
        self.assertEqual(len(results), 2) # Ford Mustang and Honda CR-V

if __name__ == '__main__':
    unittest.main()