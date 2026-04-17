import copy


class Sprite:
    def __init__(self, name="novo_sprite", width=16, height=16):
        self.name = name
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

        # Pilhas de histórico independentes para cada sprite
        self.undo_stack = []
        self.redo_stack = []

    def toggle_pixel(self, row, col):
        self.grid[row][col] = 1 if self.grid[row][col] == 0 else 0

    def save_state(self):
        # Salva a matriz atual no histórico de "desfazer"
        self.undo_stack.append(copy.deepcopy(self.grid))

        # Limita o histórico a 50 passos para não estourar a memória RAM
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

        # Sempre que uma NOVA ação é feita, o futuro (refazer) é apagado
        self.redo_stack.clear()