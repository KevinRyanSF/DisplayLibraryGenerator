import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import copy
import math
from src.models import Sprite
from src.file_manager import export_h_file, import_h_file
from .sidebar import Sidebar
from .canvas import DrawingCanvas


class MainWindow:
    """
    Acts as the main controller for the application, handling the state,
    tool logic, and communication between the sidebar and the canvas.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Display Library Generator")
        self.root.configure(bg="#2b2b2b")

        # Stores the list of all created sprites and tracks the active one
        self.sprites = []
        self.current_sprite = None

        # Variables for shape drawing and movement tracking
        self.start_c = 0
        self.start_r = 0
        self.backup_grid = None

        # Initializes and places the UI components
        self.sidebar = Sidebar(self.root, controller=self)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas = DrawingCanvas(self.root)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Binds the canvas mouse events to the main controller logic
        self.canvas.on_mouse_action = self.action_mouse_event

        # Creates the first default sprite on startup
        self.action_new_sprite()

    # --- TOOL AND DRAWING LOGIC ---

    def action_mouse_event(self, c, r, state, action_type):
        """
        Routes the mouse events to the appropriate tool logic based on the user's selection.
        """
        if not self.current_sprite:
            return

        tool = self.sidebar.tool_var.get()

        if tool == "fill":
            if action_type == "press":
                self.current_sprite.save_state()
                self.apply_flood_fill(c, r, state)
                self.canvas.refresh_colors(self.current_sprite)

        elif tool == "move":
            if action_type == "press":
                self.current_sprite.save_state()
                self.start_c, self.start_r = c, r
                self.backup_grid = copy.deepcopy(self.current_sprite.grid)
            elif action_type == "drag" or action_type == "release":
                if self.backup_grid:
                    dc = c - self.start_c
                    dr = r - self.start_r
                    self.apply_move(dc, dr)
                    self.canvas.refresh_colors(self.current_sprite)
                if action_type == "release":
                    self.backup_grid = None

        elif tool == "pen":
            if action_type == "press":
                self.current_sprite.save_state()
            self.current_sprite.grid[r][c] = state
            self.canvas.update_single_pixel(r, c, state)

        else:
            # Handles geometric shape tools (line, rectangle, circle, triangle)
            if action_type == "press":
                self.current_sprite.save_state()
                self.start_c = c
                self.start_r = r
                self.backup_grid = copy.deepcopy(self.current_sprite.grid)

            elif action_type == "drag" or action_type == "release":
                if self.backup_grid:
                    # Restores the clean background before overlaying the updated shape
                    self.current_sprite.grid = copy.deepcopy(self.backup_grid)
                    pixels = self.calculate_shape(tool, self.start_c, self.start_r, c, r)
                    for px, py in pixels:
                        if 0 <= px < self.current_sprite.width and 0 <= py < self.current_sprite.height:
                            self.current_sprite.grid[py][px] = state
                    self.canvas.refresh_colors(self.current_sprite)

                if action_type == "release":
                    self.backup_grid = None

    def action_undo(self):
        """
        Reverts the sprite to its previous state using the undo stack.
        """
        if self.current_sprite and self.current_sprite.undo_stack:
            self.current_sprite.redo_stack.append(copy.deepcopy(self.current_sprite.grid))
            self.current_sprite.grid = self.current_sprite.undo_stack.pop()

            # Recalculates dimensions in case the undone action was a rotation
            self.current_sprite.height = len(self.current_sprite.grid)
            self.current_sprite.width = len(self.current_sprite.grid[0])

            self.canvas.draw_grid(self.current_sprite.width, self.current_sprite.height, self.current_sprite)

    def action_redo(self):
        """
        Restores the next state from the redo stack after an undo action.
        """
        if self.current_sprite and self.current_sprite.redo_stack:
            self.current_sprite.undo_stack.append(copy.deepcopy(self.current_sprite.grid))
            self.current_sprite.grid = self.current_sprite.redo_stack.pop()

            # Recalculates dimensions in case the redone action was a rotation
            self.current_sprite.height = len(self.current_sprite.grid)
            self.current_sprite.width = len(self.current_sprite.grid[0])

            self.canvas.draw_grid(self.current_sprite.width, self.current_sprite.height, self.current_sprite)

    def apply_flood_fill(self, start_x, start_y, target_state):
        """
        Implements an iterative flood fill algorithm to color enclosed areas.
        """
        grid = self.current_sprite.grid
        width = self.current_sprite.width
        height = self.current_sprite.height
        initial_state = grid[start_y][start_x]

        if initial_state == target_state:
            return

        stack = [(start_x, start_y)]
        while stack:
            x, y = stack.pop()
            if grid[y][x] == initial_state:
                grid[y][x] = target_state
                # Checks neighboring pixels (North, South, East, West)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        stack.append((nx, ny))

    def apply_move(self, dc, dr):
        """
        Translates the entire sprite matrix by the specified delta coordinates.
        """
        width = self.current_sprite.width
        height = self.current_sprite.height
        new_grid = [[0 for _ in range(width)] for _ in range(height)]

        for r in range(height):
            for c in range(width):
                if self.backup_grid[r][c] == 1:
                    new_r = r + dr
                    new_c = c + dc
                    # Only moves the pixel if it remains within the canvas boundaries
                    if 0 <= new_r < height and 0 <= new_c < width:
                        new_grid[new_r][new_c] = 1

        self.current_sprite.grid = new_grid

    def calculate_shape(self, tool, x0, y0, x1, y1):
        """
        Directs the shape calculation to the appropriate geometric algorithm.
        """
        if tool == "line":
            return self.get_line_pixels(x0, y0, x1, y1)
        elif tool == "rect":
            return self.get_rect_pixels(x0, y0, x1, y1)
        elif tool == "circle":
            return self.get_circle_pixels(x0, y0, x1, y1)
        elif tool == "triangle":
            return self.get_triangle_pixels(x0, y0, x1, y1)
        return []

    def get_line_pixels(self, x0, y0, x1, y1):
        """
        Calculates the pixels forming a line using Bresenham's algorithm.
        """
        pixels = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            pixels.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return pixels

    def get_rect_pixels(self, x0, y0, x1, y1):
        """
        Calculates the perimeter pixels of a rectangle.
        """
        pixels = []
        pixels.extend(self.get_line_pixels(x0, y0, x1, y0))
        pixels.extend(self.get_line_pixels(x1, y0, x1, y1))
        pixels.extend(self.get_line_pixels(x1, y1, x0, y1))
        pixels.extend(self.get_line_pixels(x0, y1, x0, y0))
        return list(set(pixels))

    def get_circle_pixels(self, x0, y0, x1, y1):
        """
        Calculates the perimeter pixels of a circle using the midpoint circle algorithm.
        """
        r = int(math.hypot(x1 - x0, y1 - y0))
        pixels = []
        x = r
        y = 0
        err = 0
        while x >= y:
            pixels.extend([
                (x0 + x, y0 + y), (x0 + y, y0 + x), (x0 - y, y0 + x), (x0 - x, y0 + y),
                (x0 - x, y0 - y), (x0 - y, y0 - x), (x0 + y, y0 - x), (x0 + x, y0 - y)
            ])
            if err <= 0:
                y += 1
                err += 2 * y + 1
            if err > 0:
                x -= 1
                err -= 2 * x + 1
        return list(set(pixels))

    def get_triangle_pixels(self, x0, y0, x1, y1):
        """
        Calculates the perimeter pixels of an isosceles triangle.
        """
        pixels = []
        mid_x = (x0 + x1) // 2
        pixels.extend(self.get_line_pixels(mid_x, y0, x1, y1))
        pixels.extend(self.get_line_pixels(x1, y1, x0, y1))
        pixels.extend(self.get_line_pixels(x0, y1, mid_x, y0))
        return list(set(pixels))

    # --- GENERAL ACTIONS ---

    def action_new_sprite(self):
        """
        Instantiates a new sprite based on the dimensions provided in the sidebar.
        """
        w, h = self.sidebar.sprite_w_var.get(), self.sidebar.sprite_h_var.get()
        new_s = Sprite(name=f"sprite_{len(self.sprites)}", width=w, height=h)
        self.sprites.append(new_s)
        self.sidebar.update_list(self.sprites)
        self.sidebar.listbox.selection_set(tk.END)
        self._load_sprite_to_view(new_s)

    def action_clear_sprite(self):
        """
        Prompts the user for confirmation and resets the current sprite's grid to zeroes.
        """
        if not self.current_sprite:
            return
        if messagebox.askyesno("Limpar", f"Apagar todo o desenho de '{self.current_sprite.name}'?"):
            self.current_sprite.save_state()
            w, h = self.current_sprite.width, self.current_sprite.height
            self.current_sprite.grid = [[0 for _ in range(w)] for _ in range(h)]
            self.canvas.draw_grid(w, h, self.current_sprite)

    def action_save_name(self):
        """
        Updates the current sprite's name from the input field, replacing spaces with underscores.
        """
        if self.current_sprite:
            self.current_sprite.name = self.sidebar.name_entry.get().replace(" ", "_")
            self.sidebar.update_list(self.sprites)

    def action_select_sprite(self, event):
        """
        Loads the sprite selected from the sidebar's listbox into the canvas.
        """
        if not self.sidebar.listbox.curselection():
            return
        self._load_sprite_to_view(self.sprites[self.sidebar.listbox.curselection()[0]])

    def action_export(self):
        """
        Opens a save dialog and exports the sprites to a C header file.
        """
        path = filedialog.asksaveasfilename(defaultextension=".h", filetypes=[("C Header", "*.h")])
        if path:
            export_h_file(self.sprites, path, self.sidebar.display_type_var.get(),
                          self.sidebar.display_w_var.get(), self.sidebar.display_h_var.get())
            messagebox.showinfo("Sucesso", "Biblioteca exportada!")

    def action_import(self):
        """
        Opens a file dialog, reads an existing C header file, and imports its sprites.
        """
        path = filedialog.askopenfilename(filetypes=[("C Header", "*.h")])
        if path:
            sprites, d_type, d_w, d_h = import_h_file(path)
            if sprites:
                self.sidebar.display_type_var.set(d_type)
                self.sidebar.display_w_var.set(d_w)
                self.sidebar.display_h_var.set(d_h)
                self.sprites.extend(sprites)
                self.sidebar.update_list(self.sprites)

    def action_delete_sprite(self, index):
        """
        Prompts the user for confirmation and removes the specified sprite from the list.
        """
        if messagebox.askyesno("Excluir", f"Excluir '{self.sprites[index].name}'?"):
            del self.sprites[index]
            self.sidebar.update_list(self.sprites)
            if not self.sprites:
                self.current_sprite = None
                self.sidebar.name_entry.delete(0, tk.END)
                self.canvas.draw_grid(16, 16, None)
            else:
                idx = max(0, index - 1)
                self.sidebar.listbox.selection_set(idx)
                self._load_sprite_to_view(self.sprites[idx])

    def action_duplicate_sprite(self, index):
        """
        Creates a deep copy of the selected sprite and appends it to the list.
        """
        original = self.sprites[index]
        new_sprite = copy.deepcopy(original)
        new_sprite.name = f"{original.name}_copy"

        self.sprites.append(new_sprite)
        self.sidebar.update_list(self.sprites)
        self.sidebar.listbox.selection_clear(0, tk.END)
        self.sidebar.listbox.selection_set(tk.END)
        self._load_sprite_to_view(new_sprite)

    def action_rename_sprite(self, index):
        """
        Opens a dialog to rename the selected sprite directly from the context menu.
        """
        sprite_to_rename = self.sprites[index]

        new_name = simpledialog.askstring(
            "Renomear Sprite",
            "Digite o novo nome para o sprite:",
            initialvalue=sprite_to_rename.name,
            parent=self.root
        )

        if new_name:
            new_name = new_name.replace(" ", "_")
            sprite_to_rename.name = new_name
            self.sidebar.update_list(self.sprites)

            if self.current_sprite == sprite_to_rename:
                self.sidebar.name_entry.delete(0, tk.END)
                self.sidebar.name_entry.insert(0, new_name)

    def action_rotate_90(self):
        """
        Rotates the current sprite 90 degrees clockwise and adjusts its dimensions.
        """
        if not self.current_sprite:
            return
        self.current_sprite.save_state()

        old_w = self.current_sprite.width
        old_h = self.current_sprite.height
        new_w = old_h
        new_h = old_w

        new_grid = [[0 for _ in range(new_w)] for _ in range(new_h)]

        for r in range(old_h):
            for c in range(old_w):
                new_grid[c][old_h - 1 - r] = self.current_sprite.grid[r][c]

        self.current_sprite.width = new_w
        self.current_sprite.height = new_h
        self.current_sprite.grid = new_grid

        self.canvas.draw_grid(new_w, new_h, self.current_sprite)

    def action_flip_h(self):
        """
        Flips the current sprite horizontally.
        """
        if not self.current_sprite:
            return
        self.current_sprite.save_state()

        for r in range(self.current_sprite.height):
            self.current_sprite.grid[r].reverse()

        self.canvas.refresh_colors(self.current_sprite)

    def action_flip_v(self):
        """
        Flips the current sprite vertically.
        """
        if not self.current_sprite:
            return
        self.current_sprite.save_state()

        self.current_sprite.grid.reverse()

        self.canvas.refresh_colors(self.current_sprite)

    def action_resize_sprite(self, index):
        """
        Prompts the user for new dimensions, warns about pixel loss, and resizes the grid.
        """
        sprite_to_resize = self.sprites[index]

        new_lengh = simpledialog.askstring(
            "Redimensionar Sprite",
            f"Tamanho atual: {sprite_to_resize.width}x{sprite_to_resize.height}\nDigite o novo tamanho (Ex: 32x32):",
            initialvalue=f"{sprite_to_resize.width}x{sprite_to_resize.height}",
            parent=self.root
        )

        if new_lengh:
            try:
                partes = new_lengh.lower().split('x')
                new_w = int(partes[0].strip())
                new_h = int(partes[1].strip())
            except:
                messagebox.showerror("Erro", "Formato invalido. Use o formato numerico WxH (exemplo: 16x32).")
                return

            if new_w == sprite_to_resize.width and new_h == sprite_to_resize.height:
                return

            warning = messagebox.askyesno(
                "Aviso de Redimensionamento",
                "Alterar as dimensoes pode cortar e apagar permanentemente os pixels que ficarem de fora do novo tamanho.\n\nDeseja continuar?"
            )

            if not warning:
                return

            is_current = (self.current_sprite == sprite_to_resize)

            if is_current:
                self.current_sprite.save_state()

            old_w = sprite_to_resize.width
            old_h = sprite_to_resize.height

            new_grid = [[0 for _ in range(new_w)] for _ in range(new_h)]

            for r in range(min(old_h, new_h)):
                for c in range(min(old_w, new_w)):
                    new_grid[r][c] = sprite_to_resize.grid[r][c]

            sprite_to_resize.width = new_w
            sprite_to_resize.height = new_h
            sprite_to_resize.grid = new_grid

            if is_current:
                self.sidebar.info_label.config(text=f"Tamanho: {new_w} x {new_h}")
                self.canvas.draw_grid(new_w, new_h, self.current_sprite)

    def _load_sprite_to_view(self, sprite):
        """
        Updates the UI components and canvas to display the selected sprite.
        """
        self.current_sprite = sprite
        self.sidebar.name_entry.delete(0, tk.END)
        self.sidebar.name_entry.insert(0, sprite.name)

        self.sidebar.info_label.config(text=f"Tamanho: {sprite.width} x {sprite.height}")

        self.canvas.draw_grid(sprite.width, sprite.height, sprite)