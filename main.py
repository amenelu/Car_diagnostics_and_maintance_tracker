from car import Car
import datetime

cars=[]

def add_car():
    make=input("Enter the car make:")
    model=input("Enter the car model:")
    year=int(input("Enter the car year:"))
    milage=int(input("Enter the car milage:"))
    vin=int(input("Enter the car vin:"))
    # create new car 
    new_car=Car(make,model,year,milage,vin)

    # add to the dictionary
    cars.append(new_car)
    print("Car added successfully")

def list_cars():
    if not cars:
        print("No car found. Please add a car first.")
        return
    for index,car in enumerate(cars):
        print(f"{index+1}. {car}")
def add_service_record():
    if not cars:
        print("No car found. Please add a car first.")
        return
    list_cars():
    car_index=int(input("Enter the index of the car:"))-1
    if car_index<0 or car_index>=len(cars):
        print("Invalid car index. Please try again.")
        return

    service=input("Enter the service type:")
    milage=int(input("Enter the service milage:"))
    cost=input("Enter the service coast:")
    date=input("Enter the service date (YYYY-MM-DD):")
    # convert date to datetime
    date=datetime.datetime.strptime(date,"%Y-%m-%d").date()
    cars[car_index].log_maintence(service,cost,date,milage)
    print("Service record added successfully")


while True:
    print("\n Car Tracker Menu\n")
    print("1. Add a new car")
    print("2. Add  service record to a car")
    print("3. View a car's service history")
    print("4. Check if a car is due for service")
    print("5. Exit")

    choice=input("Enter your choice:")
    if choice=="1":
        print("Add a new car")
        add_car()
    elif choice=="2":
        print("Add  service record to a car")
        add_service_record()
    elif choice=="3":
        print("View a car's service history")
        
    elif choice=="4":
        print("Check if a car is due for service")
    elif choice=="5":
        print("Exiting... Goodbye")
        break
    else:
        print("Invalid choice. Please input a number between 1 and 5.")
