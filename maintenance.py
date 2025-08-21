import datetime
from car import SERVICE_INTERVALS
from ui_helpers import get_user_input_int, select_car

def service_history(cars_list):
    """Displays the maintenance history for a selected car."""
    car = select_car(cars_list)
    if car:
        history = car.get_maintenance_history()
        if not history:
            print("No service history found for this car.")
            return
        print(f"\n--- Service History for {car.make} {car.model} ---")
        for record in history:
            print(f"  Date: {record['date']}, Service: {record['service']}, Mileage: {record['milage']}, Cost: ${record['cost']:.2f}")
        print("-------------------------------------------------")

def add_service_record(cars_list):
    """Adds a new maintenance log to a selected car."""
    car = select_car(cars_list)
    if not car:
        return

    service_type = input("Enter the service type: ")
    milage = get_user_input_int("Enter the service mileage: ", min_val=0)

    if milage < car.milage:
        print(f"Warning: The entered mileage ({milage}) is lower than the car's last recorded mileage ({car.milage}).")
    
    while True:
        try:
            cost_str = input("Enter the service cost: ")
            cost = float(cost_str)
            break
        except ValueError:
            print("Invalid cost. Please enter a number.")

    while True:
        date_str = input("Enter the service date (YYYY-MM-DD) or press Enter to use today's date: ")
        if not date_str:
            date = datetime.date.today()
            break
        else:
            try:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

    car.log_maintenance(service_type, cost, milage=milage, date=date.isoformat())
    print("\nService record added successfully.")

def needs_service(cars_list):
    """Checks if a selected car is due for a specific maintenance service."""
    car = select_car(cars_list)
    if not car:
        return
    
    print("\nWhich service would you like to check?")
    print(f"Known services: {', '.join(SERVICE_INTERVALS.keys())}")
    service_type = input("Enter the service type: ").lower()
    current_mileage = get_user_input_int(f"Enter the car's current mileage (last known: {car.milage}): ", min_val=0)
    if car.needs_maintenance(service_type, current_mileage=current_mileage):
        print(f"\nYES, the car is due for a '{service_type}'.")
    else:
        print(f"\nNO, the car is not yet due for a '{service_type}'.")
