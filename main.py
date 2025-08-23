from car import Car
import datetime

# Import the new modules
import maintenance
import diagnostics
from ui_helpers import get_user_input_int
import data_manager

# Load existing cars from file at startup
cars = data_manager.load_cars()

def add_car():
    make=input("Enter the car make:")
    model=input("Enter the car model:")
    current_year = datetime.date.today().year
    year=get_user_input_int(f"Enter the car year (1900-{current_year+1}): ", min_val=1900, max_val=current_year + 1)
    milage=get_user_input_int("Enter the car mileage: ", min_val=0)
    
    while True:
        vin=input("Enter the car VIN:").upper() # Standardize to uppercase
        # Check if a car with this VIN already exists
        if any(car.vin == vin for car in cars):
            print(f"A car with VIN {vin} already exists. Please enter a unique VIN.")
        else:
            break

    while True:
        license_plate = input("Enter the license plate: ").upper()
        # Check if a car with this license plate already exists
        if any(car.license_plate == license_plate for car in cars):
            print(f"A car with license plate {license_plate} already exists. Please enter a unique license plate.")
        else:
            break

    new_car=Car(make,model,year,milage,vin, license_plate)

    # add to the list
    cars.append(new_car)
    # Save the updated list to the file
    data_manager.save_cars(cars)
    print("\nCar added successfully.")

def main():
    """Main application loop."""
    print(f"Welcome! {len(cars)} car(s) loaded from file.")
    while True:
        print("\nCar Tracker Menu\n")
        print("--- Maintenance ---")
        print("1. Add a new car")
        print("2. Add service record to a car")
        print("3. View a car's service history")
        print("4. Check if a car is due for service")
        print("\n--- Diagnostics ---")
        print("5. Log a diagnostic issue")
        print("6. View and resolve diagnostic issues")
        print("\n-------------------")
        print("7. Exit")

        choice=input("Enter your choice:")
        if choice=="1":
            add_car() # Saving is handled inside the add_car function
        elif choice=="2":
            maintenance.add_service_record(cars)
            data_manager.save_cars(cars)
        elif choice=="3":
            maintenance.service_history(cars) # View-only, no save needed
        elif choice=="4":
            maintenance.needs_service(cars) # View-only, no save needed
        elif choice=="5":
            diagnostics.log_diagnostic_issue(cars)
            data_manager.save_cars(cars)
        elif choice=="6":
            diagnostics.view_and_resolve_diagnostics(cars)
            data_manager.save_cars(cars)
        elif choice=="7":
            print("Exiting... Goodbye")
            break
        else:
            print("Invalid choice. Please input a number between 1 and 7.")

if __name__ == "__main__":
    main()
