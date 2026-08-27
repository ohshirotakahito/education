import random
import unittest

from tetris import BOARD_HEIGHT, BOARD_WIDTH, TetrisEngine


class TetrisEngineTests(unittest.TestCase):
    def make_engine(self) -> TetrisEngine:
        return TetrisEngine(random.Random(1))

    def test_piece_moves_and_hard_drop_locks(self) -> None:
        engine = self.make_engine()
        start_x = engine.current_x
        engine.move(-1, 0)
        self.assertEqual(engine.current_x, start_x - 1)
        engine.hard_drop()
        self.assertTrue(any(cell is not None for row in engine.board for cell in row))

    def test_full_line_is_cleared_and_score_is_awarded(self) -> None:
        engine = self.make_engine()
        engine.board[-1] = ["I"] * BOARD_WIDTH
        engine.current_y = 0
        engine.lock_piece()
        self.assertEqual(engine.lines, 1)
        self.assertEqual(engine.score, 100)
        self.assertEqual(sum(cell is not None for row in engine.board for cell in row), 4)

    def test_collision_stops_at_left_wall(self) -> None:
        engine = self.make_engine()
        for _ in range(BOARD_WIDTH):
            engine.move(-1, 0)
        self.assertFalse(engine.move(-1, 0))
        self.assertGreaterEqual(engine.current_x, 0)

    def test_filled_spawn_area_causes_game_over(self) -> None:
        engine = self.make_engine()
        for row in range(4):
            for column in range(BOARD_WIDTH):
                engine.board[row][column] = "Z"
        engine.spawn_piece()
        self.assertTrue(engine.game_over)


if __name__ == "__main__":
    unittest.main()