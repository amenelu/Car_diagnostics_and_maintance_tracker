from car import Car
import datetime

# Import the new modules
import maintenance
import diagnostics
import ui_helpers
import search_filter
import data_manager

# Load existing cars from file at startup
cars = data_manager.load_cars()

def add_car():
    make=input("Enter the car make:")
    model=input("Enter the car model:")
    current_year = datetime.date.today().year
    year=ui_helpers.get_user_input_int(f"Enter the car year (1900-{current_year+1}): ", min_val=1900, max_val=current_year + 1)
    milage=ui_helpers.get_user_input_int("Enter the car mileage: ", min_val=0)
    
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

def search_for_car():
    """Finds a car by VIN or license plate and shows a sub-menu."""
    if not cars:
        print("\nNo cars in the system to search.")
        return

    search_term = input("\nEnter VIN or License Plate to search: ").upper()
    found_car = None
    for car in cars:
        if car.vin == search_term or car.license_plate == search_term:
            found_car = car
            break

    if not found_car:
        print(f"\nNo car found with VIN or License Plate '{search_term}'.")
        return

    print("\n--- Car Found ---")
    print(found_car)
    print("-----------------")

    while True:
        print("\nCar-Specific Menu:")
        print("1. View service history")
        print("2. View and resolve diagnostic issues")
        print("3. Return to main menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            maintenance.display_service_history(found_car)
        elif choice == '2':
            diagnostics.manage_car_diagnostics(found_car)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def edit_car():
    """Selects a car and allows editing its details."""
    print("\n--- Edit Car Details ---")
    car_to_edit = ui_helpers.select_car(cars)
    if not car_to_edit:
        return

    while True:
        print(f"\nCurrently editing: {car_to_edit}")
        print("\nWhat would you like to edit?")
        print("1. Mileage")
        print("2. License Plate")
        print("3. Return to main menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            new_mileage = ui_helpers.get_user_input_int(
                f"Enter new mileage (current: {car_to_edit.milage}): ",
                min_val=car_to_edit.milage
            )
            car_to_edit.milage = new_mileage
            print("Mileage updated successfully.")
            data_manager.save_cars(cars)
        elif choice == '2':
            while True:
                new_plate = input("Enter new license plate: ").upper()
                if any(c.license_plate == new_plate and c.vin != car_to_edit.vin for c in cars):
                    print(f"Error: License plate '{new_plate}' is already in use by another car.")
                else:
                    car_to_edit.license_plate = new_plate
                    print("License plate updated successfully.")
                    data_manager.save_cars(cars)
                    break
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def delete_car():
    """Selects a car and permanently deletes it from the system."""
    print("\n--- Delete a Car ---")
    car_to_delete = ui_helpers.select_car(cars)
    if not car_to_delete:
        return

    # Confirmation step to prevent accidental deletion
    print(f"\nYou have selected: {car_to_delete}")
    confirm = input("Are you sure you want to PERMANENTLY delete this car? This cannot be undone. (yes/no): ").lower()

    if confirm == 'yes':
        cars.remove(car_to_delete)
        data_manager.save_cars(cars)
        print("Car has been successfully deleted.")
    else:
        print("Deletion cancelled.")

def main():
    """Main application loop."""
    print(f"Welcome! {len(cars)} car(s) loaded from file.")
    while True:
        print("\nCar Tracker Menu\n")
        print("--- Maintenance ---")
        print("1. Add a new car")
        print("2. Edit a car's details")
        print("3. Delete a car")
        print("4. Add service record to a car")
        print("5. View a car's service history")
        print("6. Check if a car is due for service")
        print("\n--- Diagnostics ---")
        print("7. Log a diagnostic issue")
        print("8. View and resolve diagnostic issues")
        print("\n--- Search & View ---")
        print("9. Find a specific car (VIN/Plate)")
        print("10. Filter car list by criteria")
        print("\n-------------------")
        print("11. Exit")

        choice=input("Enter your choice: ")
        if choice=="1":
            add_car() # Saving is handled inside the add_car function
        elif choice=="2":
            edit_car()
        elif choice=="3":
            delete_car()
        elif choice=="4":
            maintenance.add_service_record(cars)
            data_manager.save_cars(cars)
        elif choice=="5":
            maintenance.service_history(cars) # View-only, no save needed
        elif choice=="6":
            maintenance.needs_service(cars) # View-only, no save needed
        elif choice=="7":
            diagnostics.log_diagnostic_issue(cars)
            data_manager.save_cars(cars)
        elif choice=="8":
            diagnostics.view_and_resolve_diagnostics(cars)
            data_manager.save_cars(cars)
        elif choice=="9":
            search_for_car()
        elif choice == "10":
            search_filter.search_and_filter_cars(cars)
        elif choice=="11":
            print("Exiting... Goodbye")
            break
        else:
            print("Invalid choice. Please input a number between 1 and 11.")

if __name__ == "__main__":
    main()
