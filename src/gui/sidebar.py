import tkinter as tk
from tkinter import ttk


class Sidebar(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg="#2b2b2b", padx=10, pady=10, **kwargs)
        self.controller = controller

        self.display_type_var = tk.StringVar(value="SSD1306")
        self.display_w_var = tk.IntVar(value=128)
        self.display_h_var = tk.IntVar(value=64)

        self.sprite_w_var = tk.IntVar(value=16)
        self.sprite_h_var = tk.IntVar(value=16)

        # Variável que guarda a ferramenta atual
        self.tool_var = tk.StringVar(value="pen")

        self._build_display_config()
        self._build_tools()
        self._build_transformations()
        self._build_sprite_manager()

    def _build_display_config(self):
        f = tk.LabelFrame(self, text="Config. do Display", bg="#2b2b2b", fg="white", padx=5, pady=5)
        f.pack(fill=tk.X, pady=(0, 10))
        tk.Label(f, text="Tipo:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w")
        ttk.Combobox(f, textvariable=self.display_type_var, values=["SSD1306", "SH1106"], state="readonly",
                     width=12).grid(row=0, column=1)
        tk.Label(f, text="Largura:", bg="#2b2b2b", fg="white").grid(row=1, column=0, sticky="w")
        tk.Entry(f, textvariable=self.display_w_var, width=15).grid(row=1, column=1)
        tk.Label(f, text="Altura:", bg="#2b2b2b", fg="white").grid(row=2, column=0, sticky="w")
        tk.Entry(f, textvariable=self.display_h_var, width=15).grid(row=2, column=1)

    def _build_tools(self):
        f = tk.LabelFrame(self, text="Ferramentas", bg="#2b2b2b", fg="white", padx=5, pady=5)
        f.pack(fill=tk.X, pady=(0, 10))

        tools = [
            ("Lapis Livre", "pen"),
            ("Linha Reta", "line"),
            ("Retangulo", "rect"),
            ("Circulo", "circle"),
            ("Triangulo", "triangle"),
            ("Balde de Tinta", "fill"),  # Nova ferramenta
            ("Mover Sprite", "move")  # Nova ferramenta
        ]

        for text, val in tools:
            rb = tk.Radiobutton(f, text=text, variable=self.tool_var, value=val,
                                bg="#2b2b2b", fg="white", selectcolor="#4b6eaf",
                                activebackground="#2b2b2b", activeforeground="white")
            rb.pack(anchor="w")

        # Botões de Desfazer e Refazer
        action_frame = tk.Frame(f, bg="#2b2b2b")
        action_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(action_frame, text="Desfazer", command=self.controller.action_undo).pack(side=tk.LEFT, fill=tk.X,
                                                                                           expand=True, padx=(0, 2))
        tk.Button(action_frame, text="Refazer", command=self.controller.action_redo).pack(side=tk.RIGHT, fill=tk.X,
                                                                                          expand=True, padx=(2, 0))

    def _build_transformations(self):
        f = tk.LabelFrame(self, text="Transformacoes", bg="#2b2b2b", fg="white", padx=5, pady=5)
        f.pack(fill=tk.X, pady=(0, 10))

        tk.Button(f, text="Girar 90", command=self.controller.action_rotate_90).pack(side=tk.LEFT, fill=tk.X,
                                                                                     expand=True, padx=(0, 2))
        tk.Button(f, text="Espelhar H", command=self.controller.action_flip_h).pack(side=tk.LEFT, fill=tk.X,
                                                                                    expand=True, padx=(2, 2))
        tk.Button(f, text="Espelhar V", command=self.controller.action_flip_v).pack(side=tk.LEFT, fill=tk.X,
                                                                                    expand=True, padx=(2, 0))

    def _build_sprite_manager(self):
        sf = tk.Frame(self, bg="#2b2b2b")
        sf.pack(fill=tk.X, pady=5)
        tk.Label(sf, text="Novo Sprite (W x H):", bg="#2b2b2b", fg="#aaa").pack(anchor="w")

        tk.Entry(sf, textvariable=self.sprite_w_var, width=5).pack(side=tk.LEFT)
        tk.Label(sf, text="x", bg="#2b2b2b", fg="white").pack(side=tk.LEFT)
        tk.Entry(sf, textvariable=self.sprite_h_var, width=5).pack(side=tk.LEFT)

        tk.Button(self, text="Novo Sprite", command=self.controller.action_new_sprite).pack(fill=tk.X, pady=5)
        tk.Button(self, text="Limpar Desenho", command=self.controller.action_clear_sprite).pack(fill=tk.X, pady=(0, 5))

        self.listbox = tk.Listbox(self, bg="#3c3f41", fg="white", selectbackground="#4b6eaf")
        self.listbox.pack(fill=tk.Y, expand=True, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.controller.action_select_sprite)
        self.listbox.bind('<Button-3>', self._show_context_menu)

        self.info_label = tk.Label(self, text="Tamanho: -- x --", bg="#2b2b2b", fg="#aaa")
        self.info_label.pack(fill=tk.X, pady=(0, 5))

        self.name_entry = tk.Entry(self)
        self.name_entry.pack(fill=tk.X, pady=5)

        tk.Button(self, text="Salvar Nome", command=self.controller.action_save_name).pack(fill=tk.X, pady=2)
        tk.Button(self, text="Exportar .h", command=self.controller.action_export, bg="#4b6eaf", fg="white").pack(
            fill=tk.X, pady=10)
        tk.Button(self, text="Importar .h", command=self.controller.action_import).pack(fill=tk.X, pady=2)

        self.context_menu = tk.Menu(self, tearoff=0, bg="#3c3f41", fg="white", activebackground="#cf3e3e")
        self.context_menu.add_command(label="Renomear Sprite", command=self._on_rename_clicked)
        self.context_menu.add_command(label="Redimensionar Sprite", command=self._on_resize_clicked)  # Nova linha
        self.context_menu.add_command(label="Duplicar Sprite", command=self._on_duplicate_clicked)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Excluir Sprite", command=self._on_delete_clicked)

    def _show_context_menu(self, event):
        index = self.listbox.nearest(event.y)
        if 0 <= index < self.listbox.size():
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.controller.action_select_sprite(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _on_delete_clicked(self):
        selection = self.listbox.curselection()
        if selection: self.controller.action_delete_sprite(selection[0])

    def _on_duplicate_clicked(self):
        selection = self.listbox.curselection()
        if selection:
            self.controller.action_duplicate_sprite(selection[0])

    def _on_rename_clicked(self):
        selection = self.listbox.curselection()
        if selection:
            self.controller.action_rename_sprite(selection[0])

    def _on_resize_clicked(self):
        selection = self.listbox.curselection()
        if selection:
            self.controller.action_resize_sprite(selection[0])

    def update_list(self, sprites):
        self.listbox.delete(0, tk.END)
        for s in sprites: self.listbox.insert(tk.END, s.name)