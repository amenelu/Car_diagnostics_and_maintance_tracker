from ui_helpers import select_car
import database as db

def log_diagnostic_issue(cars_list):
    """Logs a new diagnostic issue for a selected car."""
    car = select_car(cars_list)
    if not car:
give        return False

    print(f"\n--- Logging Diagnostic Issue for {car.make} {car.model} ---")
    description = input("Enter a description of the issue (e.g., 'Check engine light on'): ")
    code = input("Enter any diagnostic code, if available (e.g., 'P0420') or press Enter to skip: ")
    
    new_log = car.log_diagnostic(description, code=code if code else None)
    db.add_diagnostic_log(car.id, new_log)
    print("\nDiagnostic issue logged successfully.")
    return True

def manage_car_diagnostics(car):
    """Displays diagnostic issues for a given car and allows resolving them."""
    made_change = False
    while True:
        history = car.get_diagnostic_history()
        open_issues = [log for log in history if log['status'] == 'open']
        resolved_issues = [log for log in history if log['status'] == 'resolved']

        print(f"\n--- Diagnostic History for {car.make} {car.model} ---")
        if not history:
            print("No diagnostic issues found for this car.")
            return made_change

        if open_issues:
            print("\n-- Open Issues --")
            for i, log in enumerate(open_issues):
                code_str = f" (Code: {log['code']})" if log['code'] else ""
                print(f"  {i + 1}. [{log['date_logged']}] {log['description']}{code_str}")
        else:
            print("\n-- No Open Issues --")

        if resolved_issues:
            print("\n-- Resolved Issues --")
            for log in resolved_issues:
                code_str = f" (Code: {log['code']})" if log['code'] else ""
                print(f"  - [{log['date_logged']}] {log['description']}{code_str}")
                print(f"    Resolved on {log['resolved_date']}: {log['resolution']}")
        print("\n-------------------------------------------------")

        if not open_issues:
            break

        resolve_choice = input("Enter the number of an issue to resolve, or press Enter to return to the main menu: ")
        if not resolve_choice:
            break
        try:
            choice_index = int(resolve_choice) - 1
            resolution = input(f"How was issue '{open_issues[choice_index]['description']}' resolved? ")
            resolved_log = car.resolve_diagnostic(choice_index, resolution)
            if resolved_log:
                print("Issue marked as resolved.")
                db.resolve_diagnostic_log(car.id, resolved_log)
                made_change = True
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid issue number.")
    return made_change

def view_and_resolve_diagnostics(cars_list):
    """Prompts user to select a car and manage its diagnostics."""
    car = select_car(cars_list)
    if car:
        return manage_car_diagnostics(car)
    return False
