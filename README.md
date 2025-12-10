# Connect4-Python
Connect 4 programmed in python using pygame.

## Data structures
- **Board**: `numpy.ndarray` (6x7) storing {0: empty, 1: player, 2: bot}. Core ops: `create_board`, `drop_piece`, `is_valid_location`, `get_next_open_row`, `winning_move`.
- **Move history**: list of `(col, row, piece)` tuples to support undo and replay on restart.

## Algorithms
- **Move validation**: check top cell to see if a column is playable; find next open row by scanning upward.
- **Win detection**: scan horizontal, vertical, and both diagonals for four-in-a-row.
- **Bot move**: simple one-ply heuristic (`pick_best_move`) scores immediate outcomes and picks the best column.
- **Undo/Restart**: pop from history and clear that cell; restart reinitializes board/state.

## Asymptotic analysis (R rows, C cols; constants for 6x7)
- `is_valid_location`: O(1)
- `get_next_open_row`: O(R)
- `drop_piece`: O(1)
- `winning_move`: O(R*C)
- `pick_best_move`: O(C * (R + eval scans)) → linear in board cells for a general board.
- Undo/Restart: O(1) per operation.

## Implementation artifacts
- Game: `Four_in_a_row.py` (run with `python Four_in_a_row.py`).
- Automated checks: `test_connect4.py` exercises move validity, win detection, and undo/history basics (`python test_connect4.py`).
- Dependencies: `pygame`, `numpy`.

## Running
```bash
python Four_in_a_row.py
```

## Tests
```bash
python test_connect4.py
```
