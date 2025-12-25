from src.cli.ui_helpers import get_user_input_int, list_cars
from src.car import SERVICE_INTERVALS


def _get_filters_from_user():
    """Interactively gets filter criteria from the user."""
    print("\n--- Set Filter Criteria (press Enter to skip a filter) ---")
    filters = {}

    make = input("Filter by make: ").strip()
    if make:
        filters["make"] = make

    model = input("Filter by model: ").strip()
    if model:
        filters["model"] = model

    min_year = get_user_input_int("Filter by minimum year: ", allow_empty=True)
    if min_year is not None:
        filters["min_year"] = min_year

    max_year = get_user_input_int("Filter by maximum year: ", allow_empty=True)
    if max_year is not None:
        filters["max_year"] = max_year

    max_mileage = get_user_input_int(
        "Filter by maximum mileage: ", min_val=0, allow_empty=True
    )
    if max_mileage is not None:
        filters["max_mileage"] = max_mileage

    has_open_issues = (
        input("Show only cars with open diagnostic issues? (y/n): ").strip().lower()
    )
    if has_open_issues == "y":
        filters["has_open_issues"] = True

    print(f"Available services to check for: {', '.join(SERVICE_INTERVALS.keys())}")
    needs_service_type = (
        input("Show only cars needing a specific service (enter type): ")
        .strip()
        .lower()
    )
    if needs_service_type:
        if needs_service_type in SERVICE_INTERVALS:
            filters["needs_service_type"] = needs_service_type
        else:
            print(
                f"Warning: '{needs_service_type}' is not a known service type. This filter will be ignored."
            )

    return filters


def _apply_filters(cars_list, filters):
    """Applies a dictionary of filters to a list of cars."""
    filtered = list(cars_list)  # Start with a copy of the list

    if "make" in filters:
        filtered = [
            car for car in filtered if filters["make"].lower() in car.make.lower()
        ]
    if "model" in filters:
        filtered = [
            car for car in filtered if filters["model"].lower() in car.model.lower()
        ]
    if "min_year" in filters:
        filtered = [car for car in filtered if car.year >= filters["min_year"]]
    if "max_year" in filters:
        filtered = [car for car in filtered if car.year <= filters["max_year"]]
    if "max_mileage" in filters:
        filtered = [car for car in filtered if car.milage <= filters["max_mileage"]]
    if filters.get("has_open_issues"):
        filtered = [
            car
            for car in filtered
            if any(log["status"] == "open" for log in car.diagnostic_logs)
        ]
    if "needs_service_type" in filters:
        service_type = filters["needs_service_type"]
        # Call needs_maintenance with verbose=False to prevent printing during filtering
        filtered = [
            car
            for car in filtered
            if car.needs_maintenance(
                service_type, current_mileage=car.milage, verbose=False
            )
        ]

    return filtered


def search_and_filter_cars(cars_list):
    """Guides user through filtering cars and displaying results."""
    if not cars_list:
        print("\nNo cars in the system to search or filter.")
        return

    filters = _get_filters_from_user()
    results = _apply_filters(cars_list, filters)

    print(f"\n--- Found {len(results)} car(s) matching your criteria ---")
    if not results:
        print("No cars match your filter criteria.")
    else:
        list_cars(results)
