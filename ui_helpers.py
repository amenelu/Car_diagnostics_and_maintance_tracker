import datetime
import os
import platform

def get_user_input_int(prompt, min_val=None, max_val=None, allow_empty=False):
    """Helper function to get a valid integer from the user within an optional range."""
    while True:
        try:
            value_str = input(prompt)
            if allow_empty and not value_str:
                return None
            value = int(value_str)
            if min_val is not None and value < min_val:
                print(f"Input must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Input must be no more than {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def list_cars(cars_list):
    """Displays a numbered list of cars."""
    print("\n--- Your Cars ---")
    for index, car in enumerate(cars_list):
        print(f"{index + 1}. {car}")
    print("-----------------")

def select_car(cars_list):
    """Lists cars and prompts user to select one. Returns the car object or None."""
    if not cars_list:
        print("\nNo cars found in the system. Please add a car first.")
        return None
    list_cars(cars_list)
    car_index = get_user_input_int("Select a car by number: ", min_val=1, max_val=len(cars_list)) - 1
    return cars_list[car_index]

def clear_screen():
    """Clears the terminal screen."""
    command = 'cls' if platform.system() == 'Windows' else 'clear'
    os.system(command)

def press_enter_to_continue():
    """Pauses execution and waits for the user to press Enter."""
    input("\nPress Enter to continue...")
