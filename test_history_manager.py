import unittest
from car import Car
from history_manager import HistoryManager

class TestHistoryManager(unittest.TestCase):

    def setUp(self):
        self.history = HistoryManager()
        self.car1 = Car("Make1", "Model1", 2020, 10000, "VIN1", "PLATE1")
        self.car2 = Car("Make2", "Model2", 2021, 20000, "VIN2", "PLATE2")
        self.initial_state = [self.car1, self.car2]

    def test_record_state(self):
        """Test that recording a state adds to undo stack and clears redo stack."""
        self.history.record_state(self.initial_state)
        self.assertEqual(len(self.history.undo_stack), 1)
        self.assertEqual(len(self.history.redo_stack), 0)

    def test_undo_and_redo(self):
        """Test the full undo and redo cycle."""
        # 1. Record initial state
        self.history.record_state(self.initial_state)

        # 2. Make a change (create a new list representing the modified state)
        modified_state = self.initial_state + [Car("Make3", "Model3", 2022, 300, "VIN3", "PLATE3")]
        
        # 3. Undo the change
        undone_state = self.history.undo(modified_state)
        self.assertEqual(len(undone_state), 2)
        self.assertEqual(undone_state[0].vin, "VIN1")
        self.assertEqual(len(self.history.redo_stack), 1) # The modified state should be in redo stack

        # 4. Redo the change
        redone_state = self.history.redo(undone_state)
        self.assertEqual(len(redone_state), 3)
        self.assertEqual(redone_state[2].vin, "VIN3")
        self.assertEqual(len(self.history.undo_stack), 1) # The initial state is back on the undo stack

    def test_new_action_clears_redo_stack(self):
        """Test that a new action after an undo clears the redo history."""
        self.history.record_state(self.initial_state)
        modified_state = self.initial_state + [Car("Make3", "Model3", 2022, 300, "VIN3", "PLATE3")]
        
        # Undo, which populates the redo stack
        undone_state = self.history.undo(modified_state)
        self.assertEqual(len(self.history.redo_stack), 1)

        # Record a new, different action
        self.history.record_state(undone_state)
        self.assertEqual(len(self.history.redo_stack), 0) # Redo stack should now be empty

    def test_discard_last_record(self):
        """Test discarding a recorded state (e.g., for a cancelled action)."""
        self.history.record_state(self.initial_state)
        self.assertEqual(len(self.history.undo_stack), 1)
        self.history.discard_last_record()
        self.assertEqual(len(self.history.undo_stack), 0)

if __name__ == '__main__':
    unittest.main()