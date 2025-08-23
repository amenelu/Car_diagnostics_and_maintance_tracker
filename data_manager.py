import json
from car import Car

DATA_FILE = "car_data.json"

def save_cars(cars_list):
    """Saves the list of car objects to a JSON file."""
    # Convert the list of Car objects into a list of dictionaries
    data_to_save = [car.to_dict() for car in cars_list]
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except IOError as e:
        print(f"Error: Could not save data to {DATA_FILE}. {e}")

def load_cars():
    """Loads the list of cars from a JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            data_from_file = json.load(f)
            # Convert the list of dictionaries back into a list of Car objects
            return [Car.from_dict(car_data) for car_data in data_from_file]
    except FileNotFoundError:
        return []  # If the file doesn't exist yet, start with an empty list
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not load or parse data from {DATA_FILE}. Starting fresh. {e}")
        return []
