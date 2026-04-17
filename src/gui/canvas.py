import tkinter as tk


class DrawingCanvas(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#1e1e1e", padx=10, pady=10, **kwargs)
        self.on_mouse_action = None
        self.cell_size = 20
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(expand=True)

        self.canvas.bind("<ButtonPress-1>", lambda e: self._handle(e, 1, "press"))
        self.canvas.bind("<B1-Motion>", lambda e: self._handle(e, 1, "drag"))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self._handle(e, 1, "release"))

        self.canvas.bind("<ButtonPress-3>", lambda e: self._handle(e, 0, "press"))
        self.canvas.bind("<B3-Motion>", lambda e: self._handle(e, 0, "drag"))
        self.canvas.bind("<ButtonRelease-3>", lambda e: self._handle(e, 0, "release"))

        self.rects = []
        self.current_w = 0
        self.current_h = 0

    def draw_grid(self, width, height, current_sprite):
        self.canvas.delete("all")
        self.rects = []
        self.current_w = width
        self.current_h = height

        if current_sprite is None: return
        self.canvas.config(width=width * self.cell_size, height=height * self.cell_size)

        for r in range(height):
            row_rects = []
            for c in range(width):
                x0, y0 = c * self.cell_size, r * self.cell_size
                color = "#00FFFF" if current_sprite.grid[r][c] == 1 else "#000000"
                rid = self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size, fill=color,
                                                   outline="#333333")
                row_rects.append(rid)
            self.rects.append(row_rects)

    def _handle(self, event, state, action_type):
        if not self.on_mouse_action or not self.rects: return

        c = event.x // self.cell_size
        r = event.y // self.cell_size

        # Limita a coordenada ao tamanho da tela para não quebrar a matriz
        c = max(0, min(c, self.current_w - 1))
        r = max(0, min(r, self.current_h - 1))

        self.on_mouse_action(c, r, state, action_type)

    def update_single_pixel(self, r, c, state):
        self.canvas.itemconfig(self.rects[r][c], fill="#00FFFF" if state else "#000000")

    def refresh_colors(self, current_sprite):
        for r in range(self.current_h):
            for c in range(self.current_w):
                color = "#00FFFF" if current_sprite.grid[r][c] == 1 else "#000000"
                self.canvas.itemconfig(self.rects[r][c], fill=color)