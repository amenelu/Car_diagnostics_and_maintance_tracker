from src.car import Car
import datetime

# Import the new modules
import src.maintenance as maintenance
import src.cli.diagnostics as diagnostics
import src.cli.ui_helpers as ui_helpers
import src.search_filter as search_filter
import src.database as db
from src.history_manager import HistoryManager

# Load existing cars from file at startup
db.init_db()  # Ensure DB and tables exist
cars = db.load_all_cars()
history = HistoryManager()


def add_car(cars_list):
    make = input("Enter the car make:")
    model = input("Enter the car model:")
    current_year = datetime.date.today().year
    year = ui_helpers.get_user_input_int(
        f"Enter the car year (1900-{current_year+1}): ",
        min_val=1900,
        max_val=current_year + 1,
    )
    milage = ui_helpers.get_user_input_int("Enter the car mileage: ", min_val=0)

    while True:
        vin = input("Enter the car VIN:").upper()  # Standardize to uppercase
        if db.check_vin_exists(vin):
            print(f"A car with VIN {vin} already exists. Please enter a unique VIN.")
        else:
            break

    while True:
        license_plate = input("Enter the license plate: ").upper()
        if db.check_license_plate_exists(license_plate):
            print(
                f"A car with license plate {license_plate} already exists. Please enter a unique license plate."
            )
        else:
            break

    new_car = Car(make, model, year, milage, vin, license_plate)

    # add to the list
    cars_list.append(new_car)
    db.add_car(new_car)  # Save to DB and get ID assigned to the object
    print(f"\nCar '{new_car.make} {new_car.model}' added successfully.")
    return True


def search_for_car(cars_list):
    """Finds a car by VIN or license plate and shows a sub-menu."""
    if not cars_list:
        print("\nNo cars in the system to search.")
        return

    search_term = input("\nEnter VIN or License Plate to search: ").upper()
    found_car = None
    for car in cars_list:
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
        print("3. Generate Summary Report")
        print("4. Return to main menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            maintenance.display_service_history(found_car)
        elif choice == "2":
            diagnostics.manage_car_diagnostics(found_car)
        elif choice == "3":
            maintenance.generate_car_summary_report(found_car)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


def edit_car(cars_list):
    """Selects a car and allows editing its details."""
    print("\n--- Edit Car Details ---")
    car_to_edit = ui_helpers.select_car(cars_list)
    if not car_to_edit:
        return False

    made_change = False
    while True:
        print(f"\nCurrently editing: {car_to_edit}")
        print("\nWhat would you like to edit?")
        print("1. Mileage")
        print("2. License Plate")
        print("3. Return to main menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            new_mileage = ui_helpers.get_user_input_int(
                f"Enter new mileage (current: {car_to_edit.milage}): ",
                min_val=car_to_edit.milage,
            )
            car_to_edit.milage = new_mileage
            db.update_car_details(car_to_edit)
            made_change = True
            print("Mileage updated successfully.")
        elif choice == "2":
            while True:
                new_plate = input("Enter new license plate: ").upper()
                if db.check_license_plate_exists(new_plate, exclude_id=car_to_edit.id):
                    print(
                        f"Error: License plate '{new_plate}' is already in use by another car."
                    )
                else:
                    car_to_edit.license_plate = new_plate
                    db.update_car_details(car_to_edit)
                    made_change = True
                    print("License plate updated successfully.")
                    break
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
    return made_change


def delete_car(cars_list):
    """Selects a car and permanently deletes it from the system."""
    print("\n--- Delete a Car ---")
    car_to_delete = ui_helpers.select_car(cars_list)
    if not car_to_delete:
        return False

    # Confirmation step to prevent accidental deletion
    print(f"\nYou have selected: {car_to_delete}")
    confirm = input(
        "Are you sure you want to PERMANENTLY delete this car? (yes/no): "
    ).lower()

    if confirm == "yes":
        cars_list.remove(car_to_delete)
        db.delete_car_by_id(car_to_delete.id)
        print("Car has been successfully deleted.")
        return True
    else:
        print("Deletion cancelled.")
        return False


def display_main_menu():
    """Prints the main menu options."""
    print("\nCar Tracker Menu\n")
    print("--- Maintenance ---")
    print("1. Add a new car")
    print("2. Edit a car's details")
    print("3. Delete a car")
    print("4. Add service record to a car")
    print("5. View a car's service history")
    print("6. Check if a car is due for service")
    print("7. View All Service Reminders")
    print("\n--- Diagnostics ---")
    print("8. Log a diagnostic issue")
    print("9. View and resolve diagnostic issues")
    print("\n--- Search & View ---")
    print("10. Find a specific car (VIN/Plate)")
    print("11. Filter car list by criteria")
    print("\n--- History ---")
    print("12. Undo last action")
    print("13. Redo last action")
    print("\n-------------------")
    print("14. Exit")


def main():
    """Main application loop."""
    global cars

    # Define actions that modify the state of the application
    state_modifying_actions = {
        "1": add_car,
        "2": edit_car,
        "3": delete_car,
        "4": maintenance.add_service_record,
        "8": diagnostics.log_diagnostic_issue,
        "9": diagnostics.view_and_resolve_diagnostics,
    }

    # Define actions that only view data
    view_only_actions = {
        "5": maintenance.service_history,
        "6": maintenance.needs_service,
        "7": maintenance.view_service_reminders,
        "10": search_for_car,
        "11": search_filter.search_and_filter_cars,
    }

    while True:
        ui_helpers.clear_screen()
        print(f"--- Car Maintenance Tracker --- ({len(cars)} car(s) loaded)")
        display_main_menu()
        choice = input("Enter your choice: ")

        if choice in view_only_actions:
            view_only_actions[choice](cars)
            ui_helpers.press_enter_to_continue()
        elif choice in state_modifying_actions:
            history.record_state(cars)
            changed = state_modifying_actions[choice](cars)

            if changed:
                # Reload the car list from the DB to reflect any changes
                cars = db.load_all_cars()
            else:
                history.discard_last_record()
            ui_helpers.press_enter_to_continue()
        elif choice == "12":  # Undo
            new_cars_state = history.undo(cars)
            if new_cars_state is not None:
                db.reset_database([c.to_dict() for c in new_cars_state])
                cars = db.load_all_cars()  # Reload from DB to ensure consistency
                print("Undo successful.")
            ui_helpers.press_enter_to_continue()
        elif choice == "13":  # Redo
            new_cars_state = history.redo(cars)
            if new_cars_state is not None:
                db.reset_database([c.to_dict() for c in new_cars_state])
                cars = db.load_all_cars()  # Reload from DB to ensure consistency
                print("Redo successful.")
            ui_helpers.press_enter_to_continue()
        elif choice == "14":  # Exit
            print("Exiting... Goodbye")
            break
        else:
            print("Invalid choice. Please input a number between 1 and 14.")
            ui_helpers.press_enter_to_continue()


if __name__ == "__main__":
    main()
