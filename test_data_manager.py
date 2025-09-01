import unittest
import os
import json
from car import Car
import data_manager

class TestDataManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test file and some car data."""
        self.test_file = "test_car_data.json"
        # Monkey-patch the DATA_FILE constant in the data_manager module for this test
        data_manager.DATA_FILE = self.test_file
        self.car1 = Car("TestMake", "TestModel", 2020, 10000, "TESTVIN1", "TEST1")
        self.cars_list = [self.car1]

    def tearDown(self):
        """Clean up by removing the temporary test file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_load(self):
        """Test that saving and loading cars preserves the data."""
        data_manager.save_cars(self.cars_list)
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.test_file))

        loaded_cars = data_manager.load_cars()
        self.assertEqual(len(loaded_cars), 1)
        self.assertEqual(loaded_cars[0].vin, self.car1.vin)
        self.assertEqual(loaded_cars[0].to_dict(), self.car1.to_dict())

    def test_load_nonexistent_file(self):
        """Test that loading from a non-existent file returns an empty list."""
        loaded_cars = data_manager.load_cars()
        self.assertEqual(loaded_cars, [])

    def test_load_corrupted_file(self):
        """Test that loading from a corrupted JSON file returns an empty list."""
        with open(self.test_file, 'w') as f:
            f.write("this is not valid json")
        loaded_cars = data_manager.load_cars()
        self.assertEqual(loaded_cars, [])