import Car from car

cars=[]

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
    elif choice=="2":
        print("Add  service record to a car")
    elif choice=="3":
        print("View a car's service history")
    elif choice=="4":
        print("Check if a car is due for service")
    elif choice=="5":
        print("Exiting... Goodbye")
        break
    else:
        print("Invalid choice. Please input a number between 1 and 5.")

while True:
    car_make=input("Enter the car make:")
    car_model=input("Enter the car model:")
    car_year=input("Enter the car year:")
    car_milage=input("Enter the car milage:")
    car_vin=input("Enter the car vin:")
    car=Car(car_make,car_model,car_year,car_milage,car_vin)
    cars.append(car)
