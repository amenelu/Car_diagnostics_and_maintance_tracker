from car import Car

class HistoryManager:
    """Manages undo and redo functionality by tracking states."""
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def record_state(self, cars_list):
        """
        Records the current state of the cars list before a change.
        A new action clears the redo stack.
        """
        snapshot = [car.to_dict() for car in cars_list]
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()

    def discard_last_record(self):
        """Removes the most recent snapshot from the undo stack if an action was cancelled."""
        if self.undo_stack:
            self.undo_stack.pop()

    def undo(self, current_cars_list):
        """
        Reverts to the previous state.
        Returns the previous state as a list of Car objects, or None.
        """
        if not self.undo_stack:
            print("\nNothing to undo.")
            return None

        current_snapshot = [car.to_dict() for car in current_cars_list]
        self.redo_stack.append(current_snapshot)

        previous_snapshot = self.undo_stack.pop()
        return [Car.from_dict(data) for data in previous_snapshot]

    def redo(self, current_cars_list):
        """
        Re-applies a previously undone action.
        Returns the redone state as a list of Car objects, or None.
        """
        if not self.redo_stack:
            print("\nNothing to redo.")
            return None

        current_snapshot = [car.to_dict() for car in current_cars_list]
        self.undo_stack.append(current_snapshot)

        next_snapshot = self.redo_stack.pop()
        return [Car.from_dict(data) for data in next_snapshot]