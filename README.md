# Four in a Row 🟡🔴

**Four in a Row** is a Python implementation of **Connect 4** using `pygame`.  
Drop pieces, strategize, and challenge the bot in this classic two-player grid game!

---

## 🧩 Features
- Fully playable **Connect 4** game in Python  
- **Undo** moves and **restart** the game  
- **Bot opponent** with simple heuristic strategy  
- Visual interface powered by `pygame`  

---

## 🗂 Data Structures
- **Board**: `numpy.ndarray` (6x7) storing:
  - `0`: empty  
  - `1`: player  
  - `2`: bot  
  - Core operations: `create_board`, `drop_piece`, `is_valid_location`, `get_next_open_row`, `winning_move`
- **Move History**: list of `(col, row, piece)` tuples to support **undo** and **replay** on restart  

---

## ⚙️ Algorithms
- **Move Validation**: check top cell to see if a column is playable; find the next open row by scanning upward  
- **Win Detection**: scan horizontal, vertical, and both diagonals for four-in-a-row  
- **Bot Move**: simple one-ply heuristic (`pick_best_move`) scores immediate outcomes and picks the best column  
- **Undo / Restart**: remove the last move from history; restart clears the board  

---

## 📊 Asymptotic Analysis  
*(R = rows, C = columns; constants for 6x7 board)*

| Operation             | Time Complexity |
|----------------------|----------------|
| `is_valid_location`    | O(1)           |
| `get_next_open_row`    | O(R)           |
| `drop_piece`           | O(1)           |
| `winning_move`         | O(R * C)       |
| `pick_best_move`       | O(C * (R + eval scans)) |
| Undo / Restart         | O(1) per operation |

---

## 🛠 Implementation
- **Game File**: `Four_in_a_row.py` — run the game with:

```bash
python Four_in_a_row.py
