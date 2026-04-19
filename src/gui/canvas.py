import tkinter as tk


class DrawingCanvas(tk.Frame):
    """
    Represents the interactive drawing area where the sprite grid is displayed and edited.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#1e1e1e", padx=10, pady=10, **kwargs)

        # Callback function triggered during mouse interactions
        self.on_mouse_action = None

        # Size of each individual grid cell in pixels
        self.cell_size = 20

        # Initializes the Tkinter canvas widget
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(expand=True)

        # Binds left mouse button events for drawing (state 1)
        self.canvas.bind("<ButtonPress-1>", lambda e: self._handle(e, 1, "press"))
        self.canvas.bind("<B1-Motion>", lambda e: self._handle(e, 1, "drag"))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self._handle(e, 1, "release"))

        # Binds right mouse button events for erasing (state 0)
        self.canvas.bind("<ButtonPress-3>", lambda e: self._handle(e, 0, "press"))
        self.canvas.bind("<B3-Motion>", lambda e: self._handle(e, 0, "drag"))
        self.canvas.bind("<ButtonRelease-3>", lambda e: self._handle(e, 0, "release"))

        # Stores the IDs of the rectangle items drawn on the canvas
        self.rects = []

        # Tracks the current dimensions of the active sprite
        self.current_w = 0
        self.current_h = 0

    def draw_grid(self, width, height, current_sprite):
        """
        Clears the canvas and reconstructs the grid of rectangles based on the specified dimensions.
        """
        self.canvas.delete("all")
        self.rects = []
        self.current_w = width
        self.current_h = height

        if current_sprite is None:
            return

        # Adjusts the canvas dimensions to fit the new grid
        self.canvas.config(width=width * self.cell_size, height=height * self.cell_size)

        # Generates the grid cells row by row
        for r in range(height):
            row_rects = []
            for c in range(width):
                # Calculates the pixel coordinates for the current cell
                x0, y0 = c * self.cell_size, r * self.cell_size

                # Determines the cell color based on the sprite's matrix state
                color = "#00FFFF" if current_sprite.grid[r][c] == 1 else "#000000"

                # Draws the cell and stores its ID
                rid = self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size, fill=color,
                                                   outline="#333333")
                row_rects.append(rid)

            self.rects.append(row_rects)

    def _handle(self, event, state, action_type):
        """
        Processes mouse events, calculates grid coordinates, and triggers the assigned callback.
        """
        if not self.on_mouse_action or not self.rects:
            return

        # Converts raw mouse pixel coordinates to grid indices
        c = event.x // self.cell_size
        r = event.y // self.cell_size

        # Clamps the coordinates to ensure they remain within the grid boundaries
        c = max(0, min(c, self.current_w - 1))
        r = max(0, min(r, self.current_h - 1))

        # Dispatches the action details to the main controller
        self.on_mouse_action(c, r, state, action_type)

    def update_single_pixel(self, r, c, state):
        """
        Updates the fill color of a specific canvas rectangle without redrawing the entire grid.
        """
        self.canvas.itemconfig(self.rects[r][c], fill="#00FFFF" if state else "#000000")

    def refresh_colors(self, current_sprite):
        """
        Iterates through the entire grid and synchronizes the color of all canvas rectangles
        with the current state of the sprite's matrix.
        """
        for r in range(self.current_h):
            for c in range(self.current_w):
                color = "#00FFFF" if current_sprite.grid[r][c] == 1 else "#000000"
                self.canvas.itemconfig(self.rects[r][c], fill=color)