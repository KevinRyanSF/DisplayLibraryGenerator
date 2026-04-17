import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import copy
import math
from src.models import Sprite
from src.file_manager import export_h_file, import_h_file
from .sidebar import Sidebar
from .canvas import DrawingCanvas


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Display Library Generator")
        self.root.configure(bg="#2b2b2b")

        self.sprites = []
        self.current_sprite = None

        # Variáveis para desenho de formas
        self.start_c = 0
        self.start_r = 0
        self.backup_grid = None

        self.sidebar = Sidebar(self.root, controller=self)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas = DrawingCanvas(self.root)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Nova ligação de eventos
        self.canvas.on_mouse_action = self.action_mouse_event

        self.action_new_sprite()

    # --- LÓGICA DE FERRAMENTAS E DESENHO ---

    def action_mouse_event(self, c, r, state, action_type):
        if not self.current_sprite: return
        tool = self.sidebar.tool_var.get()

        if tool == "fill":
            if action_type == "press":
                self.current_sprite.save_state()  # Salva histórico
                self.apply_flood_fill(c, r, state)
                self.canvas.refresh_colors(self.current_sprite)

        elif tool == "move":
            if action_type == "press":
                self.current_sprite.save_state()  # Salva histórico
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
                self.current_sprite.save_state()  # Salva histórico
            self.current_sprite.grid[r][c] = state
            self.canvas.update_single_pixel(r, c, state)

        else:
            if action_type == "press":
                self.current_sprite.save_state()  # Salva histórico
                self.start_c = c
                self.start_r = r
                self.backup_grid = copy.deepcopy(self.current_sprite.grid)

            elif action_type == "drag" or action_type == "release":
                if self.backup_grid:
                    self.current_sprite.grid = copy.deepcopy(self.backup_grid)
                    pixels = self.calculate_shape(tool, self.start_c, self.start_r, c, r)
                    for px, py in pixels:
                        if 0 <= px < self.current_sprite.width and 0 <= py < self.current_sprite.height:
                            self.current_sprite.grid[py][px] = state
                    self.canvas.refresh_colors(self.current_sprite)

                if action_type == "release":
                    self.backup_grid = None

    def action_undo(self):
        if self.current_sprite and self.current_sprite.undo_stack:
            self.current_sprite.redo_stack.append(copy.deepcopy(self.current_sprite.grid))
            self.current_sprite.grid = self.current_sprite.undo_stack.pop()

            # Recalcula a largura e altura, caso o usuário esteja desfazendo uma Rotação
            self.current_sprite.height = len(self.current_sprite.grid)
            self.current_sprite.width = len(self.current_sprite.grid[0])

            # Usa draw_grid no lugar de refresh_colors para reestruturar a tela
            self.canvas.draw_grid(self.current_sprite.width, self.current_sprite.height, self.current_sprite)

    def action_redo(self):
        if self.current_sprite and self.current_sprite.redo_stack:
            self.current_sprite.undo_stack.append(copy.deepcopy(self.current_sprite.grid))
            self.current_sprite.grid = self.current_sprite.redo_stack.pop()

            # Recalcula a largura e altura, caso o usuário esteja refazendo uma Rotação
            self.current_sprite.height = len(self.current_sprite.grid)
            self.current_sprite.width = len(self.current_sprite.grid[0])

            # Usa draw_grid no lugar de refresh_colors para reestruturar a tela
            self.canvas.draw_grid(self.current_sprite.width, self.current_sprite.height, self.current_sprite)

    def apply_flood_fill(self, start_x, start_y, target_state):
        grid = self.current_sprite.grid
        width = self.current_sprite.width
        height = self.current_sprite.height
        initial_state = grid[start_y][start_x]

        if initial_state == target_state: return

        stack = [(start_x, start_y)]
        while stack:
            x, y = stack.pop()
            if grid[y][x] == initial_state:
                grid[y][x] = target_state
                # Verifica vizinhos (Norte, Sul, Leste, Oeste)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        stack.append((nx, ny))

    def apply_move(self, dc, dr):
        width = self.current_sprite.width
        height = self.current_sprite.height
        # Cria uma grade vazia para o resultado
        new_grid = [[0 for _ in range(width)] for _ in range(height)]

        for r in range(height):
            for c in range(width):
                if self.backup_grid[r][c] == 1:
                    new_r = r + dr
                    new_c = c + dc
                    # Só move se o pixel resultante estiver dentro da tela
                    if 0 <= new_r < height and 0 <= new_c < width:
                        new_grid[new_r][new_c] = 1

        self.current_sprite.grid = new_grid

    def calculate_shape(self, tool, x0, y0, x1, y1):
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
        pixels = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            pixels.append((x0, y0))
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return pixels

    def get_rect_pixels(self, x0, y0, x1, y1):
        pixels = []
        pixels.extend(self.get_line_pixels(x0, y0, x1, y0))
        pixels.extend(self.get_line_pixels(x1, y0, x1, y1))
        pixels.extend(self.get_line_pixels(x1, y1, x0, y1))
        pixels.extend(self.get_line_pixels(x0, y1, x0, y0))
        return list(set(pixels))

    def get_circle_pixels(self, x0, y0, x1, y1):
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
        pixels = []
        mid_x = (x0 + x1) // 2
        pixels.extend(self.get_line_pixels(mid_x, y0, x1, y1))
        pixels.extend(self.get_line_pixels(x1, y1, x0, y1))
        pixels.extend(self.get_line_pixels(x0, y1, mid_x, y0))
        return list(set(pixels))

    # --- AÇÕES GERAIS ---

    def action_new_sprite(self):
        w, h = self.sidebar.sprite_w_var.get(), self.sidebar.sprite_h_var.get()
        new_s = Sprite(name=f"sprite_{len(self.sprites)}", width=w, height=h)
        self.sprites.append(new_s)
        self.sidebar.update_list(self.sprites)
        self.sidebar.listbox.selection_set(tk.END)
        self._load_sprite_to_view(new_s)

    def action_clear_sprite(self):
        if not self.current_sprite: return
        if messagebox.askyesno("Limpar", f"Apagar todo o desenho de '{self.current_sprite.name}'?"):
            self.current_sprite.save_state() # Salva histórico antes de apagar
            w, h = self.current_sprite.width, self.current_sprite.height
            self.current_sprite.grid = [[0 for _ in range(w)] for _ in range(h)]
            self.canvas.draw_grid(w, h, self.current_sprite)

    def action_save_name(self):
        if self.current_sprite:
            self.current_sprite.name = self.sidebar.name_entry.get().replace(" ", "_")
            self.sidebar.update_list(self.sprites)

    def action_select_sprite(self, event):
        if not self.sidebar.listbox.curselection(): return
        self._load_sprite_to_view(self.sprites[self.sidebar.listbox.curselection()[0]])

    def action_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".h", filetypes=[("C Header", "*.h")])
        if path:
            export_h_file(self.sprites, path, self.sidebar.display_type_var.get(),
                          self.sidebar.display_w_var.get(), self.sidebar.display_h_var.get())
            messagebox.showinfo("Sucesso", "Biblioteca exportada!")

    def action_import(self):
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
        original = self.sprites[index]
        # Cria uma cópia profunda para que as alterações em um não afetem o outro
        new_sprite = copy.deepcopy(original)
        new_sprite.name = f"{original.name}_copy"

        self.sprites.append(new_sprite)
        self.sidebar.update_list(self.sprites)
        # Seleciona o novo sprite na lista
        self.sidebar.listbox.selection_clear(0, tk.END)
        self.sidebar.listbox.selection_set(tk.END)
        self._load_sprite_to_view(new_sprite)

    def action_rename_sprite(self, index):
        sprite_to_rename = self.sprites[index]

        # Abre uma janela pedindo o novo nome, já preenchida com o nome atual
        novo_nome = simpledialog.askstring(
            "Renomear Sprite",
            "Digite o novo nome para o sprite:",
            initialvalue=sprite_to_rename.name,
            parent=self.root
        )

        if novo_nome:
            # Substitui espaços por underscores para manter o código C válido
            novo_nome = novo_nome.replace(" ", "_")
            sprite_to_rename.name = novo_nome

            # Atualiza a lista lateral
            self.sidebar.update_list(self.sprites)

            # Se o sprite que foi renomeado for o que está aberto na tela,
            # atualiza também a caixa de texto de nome lá no menu lateral.
            if self.current_sprite == sprite_to_rename:
                self.sidebar.name_entry.delete(0, tk.END)
                self.sidebar.name_entry.insert(0, novo_nome)

    def action_rotate_90(self):
        if not self.current_sprite: return
        self.current_sprite.save_state()

        old_w = self.current_sprite.width
        old_h = self.current_sprite.height
        new_w = old_h
        new_h = old_w

        # Cria uma nova matriz vazia com dimensões invertidas
        new_grid = [[0 for _ in range(new_w)] for _ in range(new_h)]

        # Mapeia os pixels girando 90 graus no sentido horário
        for r in range(old_h):
            for c in range(old_w):
                new_grid[c][old_h - 1 - r] = self.current_sprite.grid[r][c]

        self.current_sprite.width = new_w
        self.current_sprite.height = new_h
        self.current_sprite.grid = new_grid

        # Redesenha a tela inteira (pois as proporções podem ter mudado)
        self.canvas.draw_grid(new_w, new_h, self.current_sprite)

    def action_flip_h(self):
        if not self.current_sprite: return
        self.current_sprite.save_state()

        # Inverte os itens de cada linha horizontalmente
        for r in range(self.current_sprite.height):
            self.current_sprite.grid[r].reverse()

        self.canvas.refresh_colors(self.current_sprite)

    def action_flip_v(self):
        if not self.current_sprite: return
        self.current_sprite.save_state()

        # Inverte a ordem das linhas de cima para baixo
        self.current_sprite.grid.reverse()

        self.canvas.refresh_colors(self.current_sprite)

    def action_resize_sprite(self, index):
        sprite_to_resize = self.sprites[index]

        # Abre a caixa de diálogo pedindo o formato WxH
        novo_tamanho = simpledialog.askstring(
            "Redimensionar Sprite",
            f"Tamanho atual: {sprite_to_resize.width}x{sprite_to_resize.height}\nDigite o novo tamanho (Ex: 32x32):",
            initialvalue=f"{sprite_to_resize.width}x{sprite_to_resize.height}",
            parent=self.root
        )

        if novo_tamanho:
            try:
                # Divide a string no 'x' para pegar largura e altura
                partes = novo_tamanho.lower().split('x')
                new_w = int(partes[0].strip())
                new_h = int(partes[1].strip())
            except:
                messagebox.showerror("Erro", "Formato invalido. Use o formato numerico WxH (exemplo: 16x32).")
                return

            if new_w == sprite_to_resize.width and new_h == sprite_to_resize.height:
                return

            # Exibe o aviso exigido
            aviso = messagebox.askyesno(
                "Aviso de Redimensionamento",
                "Alterar as dimensoes pode cortar e apagar permanentemente os pixels que ficarem de fora do novo tamanho.\n\nDeseja continuar?"
            )

            if not aviso:
                return

            is_current = (self.current_sprite == sprite_to_resize)

            # Se o sprite alterado for o que está aberto, salva no histórico de CTRL+Z
            if is_current:
                self.current_sprite.save_state()

            old_w = sprite_to_resize.width
            old_h = sprite_to_resize.height

            # Cria a nova grade preenchida com zeros
            new_grid = [[0 for _ in range(new_w)] for _ in range(new_h)]

            # Copia os pixels antigos para a nova matriz
            # O min() garante que ele pare de copiar se atingir a borda antiga ou a nova
            for r in range(min(old_h, new_h)):
                for c in range(min(old_w, new_w)):
                    new_grid[r][c] = sprite_to_resize.grid[r][c]

            # Atualiza os dados do sprite
            sprite_to_resize.width = new_w
            sprite_to_resize.height = new_h
            sprite_to_resize.grid = new_grid

            # Atualiza a tela se o sprite editado for o que o usuario está olhando
            if is_current:
                self.sidebar.info_label.config(text=f"Tamanho: {new_w} x {new_h}")
                self.canvas.draw_grid(new_w, new_h, self.current_sprite)

    def _load_sprite_to_view(self, sprite):
        self.current_sprite = sprite
        self.sidebar.name_entry.delete(0, tk.END)
        self.sidebar.name_entry.insert(0, sprite.name)

        # Atualiza a label com as dimensões
        self.sidebar.info_label.config(text=f"Tamanho: {sprite.width} x {sprite.height}")

        self.canvas.draw_grid(sprite.width, sprite.height, sprite)