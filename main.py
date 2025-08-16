from car import Car
import datetime

cars=[]

def _get_user_input_int(prompt):
    """Helper function to get a valid integer from the user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def _select_car():
    """Lists cars and prompts user to select one. Returns the car object or None."""
    if not cars:
        print("No car found. Please add a car first.")
        return None
    list_cars()
    while True:
        car_index = _get_user_input_int("Enter the index of the car: ") - 1
        if 0 <= car_index < len(cars):
            return cars[car_index]
        print("Invalid car index. Please try again.")

def add_car():
    make=input("Enter the car make:")
    model=input("Enter the car model:")
    year=_get_user_input_int("Enter the car year:")
    milage=_get_user_input_int("Enter the car milage:")
    vin=input("Enter the car vin:") # VINs can have letters, should be a string
    # create new car 
    new_car=Car(make,model,year,milage,vin)

    # add to the list
    cars.append(new_car)
    print("Car added successfully")

def list_cars():
    if not cars:
        print("No car found. Please add a car first.")
        return False
    for index,car in enumerate(cars):
        print(f"{index+1}. {car}")
    return True

def service_history():
    car = _select_car()
    if car:
        history = car.get_maintenance_history()
        if not history:
            print("No service history found for this car.")
            return
        print(f"\n--- Service History for {car.make} {car.model} ---")
        for record in history:
            print(f"  Date: {record['date']}, Service: {record['service']}, Mileage: {record['milage']}, Cost: ${record['cost']:.2f}")
        print("-------------------------------------------------")

def add_service_record():
    car = _select_car()
    if not car:
        return

    service_type=input("Enter the service type:")
    milage=_get_user_input_int("Enter the service milage:")
    
    while True:
        try:
            cost_str = input("Enter the service cost:")
            cost = float(cost_str)
            break
        except ValueError:
            print("Invalid cost. Please enter a number.")

    while True:
        date_str = input("Enter the service date (YYYY-MM-DD) or press Enter to use today's date:")
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
    print("Service record added successfully")

def needs_service():
    car = _select_car()
    if not car:
        return
    
    service_interval = _get_user_input_int("Enter the service interval:")
    if car.needs_maintenance(service_interval):
        print("The car needs maintenance.")
    else:
        print("The car does not need maintenance.")

def main():
    """Main application loop."""
    while True:
        print("\nCar Tracker Menu\n")
        print("1. Add a new car")
        print("2. Add service record to a car")
        print("3. View a car's service history")
        print("4. Check if a car is due for service")
        print("5. Exit")

        choice=input("Enter your choice:")
        if choice=="1":
            add_car()
        elif choice=="2":
            add_service_record()
        elif choice=="3":
            service_history()
        elif choice=="4":
            needs_service()
        elif choice=="5":
            print("Exiting... Goodbye")
            break
        else:
            print("Invalid choice. Please input a number between 1 and 5.")

if __name__ == "__main__":
    main()
