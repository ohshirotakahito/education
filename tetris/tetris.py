"""Tkinterで動くシンプルなテトリス。"""

import random
import tkinter as tk
from typing import Optional


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30

COLORS = {
    "I": "#28c7d9",
    "J": "#3972e6",
    "L": "#ed9224",
    "O": "#f3d34a",
    "S": "#54c46b",
    "T": "#a85ee8",
    "Z": "#e85454",
}

SHAPES = {
    "I": (
        ((0, 1), (1, 1), (2, 1), (3, 1)),
        ((2, 0), (2, 1), (2, 2), (2, 3)),
    ),
    "J": (
        ((0, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (2, 2)),
        ((1, 0), (1, 1), (0, 2), (1, 2)),
    ),
    "L": (
        ((2, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (1, 2), (2, 2)),
        ((0, 1), (1, 1), (2, 1), (0, 2)),
        ((0, 0), (1, 0), (1, 1), (1, 2)),
    ),
    "O": (((1, 0), (2, 0), (1, 1), (2, 1)),),
    "S": (
        ((1, 0), (2, 0), (0, 1), (1, 1)),
        ((1, 0), (1, 1), (2, 1), (2, 2)),
    ),
    "T": (
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (1, 2)),
        ((1, 0), (0, 1), (1, 1), (1, 2)),
    ),
    "Z": (
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((2, 0), (1, 1), (2, 1), (1, 2)),
    ),
}


class TetrisEngine:
    """GUIから独立したテトリスの盤面とルール。"""

    def __init__(self, randomizer: Optional[random.Random] = None) -> None:
        self.randomizer = randomizer or random.Random()
        self.reset()

    def reset(self) -> None:
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.current_kind = ""
        self.current_rotation = 0
        self.current_x = 0
        self.current_y = 0
        self._bag: list[str] = []
        self.spawn_piece()

    @property
    def level(self) -> int:
        return self.lines // 10 + 1

    @property
    def current_cells(self) -> tuple[tuple[int, int], ...]:
        return SHAPES[self.current_kind][self.current_rotation]

    def _next_kind(self) -> str:
        if not self._bag:
            self._bag = list(SHAPES)
            self.randomizer.shuffle(self._bag)
        return self._bag.pop()

    def spawn_piece(self) -> None:
        self.current_kind = self._next_kind()
        self.current_rotation = 0
        self.current_x = (BOARD_WIDTH - 4) // 2
        self.current_y = 0
        if self.collides(self.current_x, self.current_y, self.current_rotation):
            self.game_over = True

    def collides(self, piece_x: int, piece_y: int, rotation: int) -> bool:
        cells = SHAPES[self.current_kind][rotation]
        for cell_x, cell_y in cells:
            board_x = piece_x + cell_x
            board_y = piece_y + cell_y
            if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                return True
            if board_y >= 0 and self.board[board_y][board_x] is not None:
                return True
        return False

    def move(self, delta_x: int, delta_y: int) -> bool:
        if self.game_over:
            return False
        next_x = self.current_x + delta_x
        next_y = self.current_y + delta_y
        if self.collides(next_x, next_y, self.current_rotation):
            return False
        self.current_x = next_x
        self.current_y = next_y
        return True

    def rotate(self) -> bool:
        if self.game_over:
            return False
        next_rotation = (self.current_rotation + 1) % len(SHAPES[self.current_kind])
        for offset_x in (0, -1, 1, -2, 2):
            if not self.collides(self.current_x + offset_x, self.current_y, next_rotation):
                self.current_x += offset_x
                self.current_rotation = next_rotation
                return True
        return False

    def tick(self) -> bool:
        if self.game_over:
            return False
        if self.move(0, 1):
            return True
        self.lock_piece()
        return False

    def hard_drop(self) -> int:
        if self.game_over:
            return 0
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.lock_piece()
        return distance

    def lock_piece(self) -> None:
        for cell_x, cell_y in self.current_cells:
            board_x = self.current_x + cell_x
            board_y = self.current_y + cell_y
            if 0 <= board_y < BOARD_HEIGHT:
                self.board[board_y][board_x] = self.current_kind
        cleared = self.clear_lines()
        self.lines += cleared
        self.score += (0, 100, 300, 500, 800)[cleared] * self.level
        self.spawn_piece()

    def clear_lines(self) -> int:
        remaining = [row for row in self.board if any(cell is None for cell in row)]
        cleared = BOARD_HEIGHT - len(remaining)
        self.board = [[None] * BOARD_WIDTH for _ in range(cleared)] + remaining
        return cleared


class TetrisApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Python Tetris")
        self.resizable(False, False)
        self.configure(bg="#17202a")
        self.engine = TetrisEngine()

        container = tk.Frame(self, bg="#17202a", padx=16, pady=16)
        container.pack()
        self.canvas = tk.Canvas(
            container,
            width=BOARD_WIDTH * CELL_SIZE,
            height=BOARD_HEIGHT * CELL_SIZE,
            bg="#0c1117",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=2)
        self.info = tk.Label(
            container,
            text="",
            justify="left",
            anchor="nw",
            width=17,
            height=12,
            bg="#17202a",
            fg="#f3f6f8",
            font=("Segoe UI", 11),
            padx=16,
        )
        self.info.grid(row=0, column=1, sticky="n")
        self.help = tk.Label(
            container,
            text="← → 移動\n↓ 落下\n↑ / X 回転\nSpace 一気に落とす\nR 再スタート",
            justify="left",
            anchor="nw",
            bg="#17202a",
            fg="#9fb0bf",
            font=("Segoe UI", 10),
            padx=16,
        )
        self.help.grid(row=1, column=1, sticky="n")

        self.bind("<Left>", lambda _event: self.handle_action(lambda: self.engine.move(-1, 0)))
        self.bind("<Right>", lambda _event: self.handle_action(lambda: self.engine.move(1, 0)))
        self.bind("<Down>", lambda _event: self.handle_action(lambda: self.engine.move(0, 1)))
        self.bind("<Up>", lambda _event: self.handle_action(self.engine.rotate))
        self.bind("x", lambda _event: self.handle_action(self.engine.rotate))
        self.bind("<space>", lambda _event: self.handle_action(self.engine.hard_drop))
        self.bind("r", lambda _event: self.restart())
        self.bind("R", lambda _event: self.restart())
        self.focus_force()
        self.render()
        self.after(500, self.game_loop)

    def handle_action(self, action) -> None:
        if not self.engine.game_over:
            action()
            self.render()

    def restart(self) -> None:
        if self.engine.game_over:
            self.engine.reset()
            self.render()

    def game_loop(self) -> None:
        if not self.engine.game_over:
            self.engine.tick()
            self.render()
        self.after(max(90, 500 - (self.engine.level - 1) * 35), self.game_loop)

    def render(self) -> None:
        self.canvas.delete("all")
        for row_index, row in enumerate(self.engine.board):
            for column_index, kind in enumerate(row):
                self.draw_cell(column_index, row_index, COLORS.get(kind, "#18232d"))
        if not self.engine.game_over:
            for cell_x, cell_y in self.engine.current_cells:
                self.draw_cell(
                    self.engine.current_x + cell_x,
                    self.engine.current_y + cell_y,
                    COLORS[self.engine.current_kind],
                )
        status = "\n\nGAME OVER\nRキーで再スタート" if self.engine.game_over else ""
        self.info.config(
            text=(
                f"SCORE\n{self.engine.score:06d}\n\n"
                f"LINES\n{self.engine.lines}\n\n"
                f"LEVEL\n{self.engine.level}{status}"
            ),
            fg="#ffcf5c" if self.engine.game_over else "#f3f6f8",
        )

    def draw_cell(self, column: int, row: int, color: str) -> None:
        left = column * CELL_SIZE + 1
        top = row * CELL_SIZE + 1
        self.canvas.create_rectangle(
            left,
            top,
            left + CELL_SIZE - 2,
            top + CELL_SIZE - 2,
            fill=color,
            outline="#0c1117",
            width=2,
        )


if __name__ == "__main__":
    TetrisApp().mainloop()