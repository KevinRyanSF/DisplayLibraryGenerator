import copy


class Sprite:
    """
    Represents a 2D sprite graphic, managing its dimensions, pixel grid state,
    and independent undo/redo history.
    """

    def __init__(self, name="novo_sprite", width=16, height=16):
        self.name = name
        self.width = width
        self.height = height

        # Initializes a 2D matrix filled with zeros (representing unlit pixels)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

        # Independent history stacks to manage undo and redo operations for this specific sprite
        self.undo_stack = []
        self.redo_stack = []

    def toggle_pixel(self, row, col):
        """
        Inverts the binary state of a specific pixel at the given row and column coordinates.
        """
        self.grid[row][col] = 1 if self.grid[row][col] == 0 else 0

    def save_state(self):
        """
        Records the current state of the pixel grid into the undo history
        and manages the stack boundaries.
        """
        # Appends a deep copy of the current grid to the undo stack
        self.undo_stack.append(copy.deepcopy(self.grid))

        # Caps the undo history at 50 steps to optimize memory consumption
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

        # Clears the redo stack whenever a new action is performed to prevent invalid forward states
        self.redo_stack.clear()