import math
import sys
from typing import Optional, Tuple

import numpy as np
import pygame

# --- Colors ---
# Basic RGB tuples for drawing the UI.
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
TEXT_LIGHT = (230, 230, 230)
WARNING_COLOR = (255, 80, 80)

# --- Board setup ---
ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

SQUARESIZE = 100
PANEL_WIDTH = 320
BOARD_WIDTH = COLUMN_COUNT * SQUARESIZE
BOARD_HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
WINDOW_WIDTH = PANEL_WIDTH + BOARD_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT
RADIUS = int(SQUARESIZE / 2 - 5)


def create_board() -> np.ndarray:
    # Start with an empty 6x7 grid.
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)


def drop_piece(board: np.ndarray, row: int, col: int, piece: int) -> None:
    # Place a piece on the board at the given slot.
    board[row][col] = piece


def is_valid_location(board: np.ndarray, col: int) -> bool:
    # A column is valid if its topmost cell is empty.
    return board[ROW_COUNT - 1][col] == EMPTY


def get_next_open_row(board: np.ndarray, col: int) -> Optional[int]:
    # Find the lowest empty row in a column.
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r
    return None


def winning_move(board: np.ndarray, piece: int) -> bool:
    # Check horizontal, vertical, and diagonal wins.
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True

    return False


def evaluate_window(window, piece):
    # Score a 4-slot window for the heuristic.
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    # Sum up scores for all possible windows.
    score = 0

    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c : c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r : r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def get_valid_locations(board: np.ndarray):
    # Columns where a piece can still be dropped.
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]


def is_terminal_node(board: np.ndarray) -> bool:
    # Game is over if someone wins or board is full.
    return (
        winning_move(board, PLAYER_PIECE)
        or winning_move(board, AI_PIECE)
        or len(get_valid_locations(board)) == 0
    )

def pick_best_move(board: np.ndarray, piece: int) -> Tuple[Optional[int], int]:
    valid_locations = get_valid_locations(board)
    if not valid_locations:
        return None, 0

    best_score = -math.inf
    best_col = valid_locations[0]
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col, best_score


# --- Pygame setup ---
# Build the window and fonts once at startup.
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Connect 4 with AI")

TITLE_FONT = pygame.font.SysFont("monospace", 72, bold=True)
TURN_FONT = pygame.font.SysFont("monospace", 45, bold=True)
BUTTON_FONT = pygame.font.SysFont("monospace", 38, bold=True)
BUTTON_FONT_SMALL = pygame.font.SysFont("monospace", 23, bold=True)
INSTRUCTIONS_FONT = pygame.font.SysFont("monospace", 25, bold=True)
TEXT_FONT = pygame.font.SysFont("monospace", 24, bold=True)
GAME_OVER_FONT = pygame.font.SysFont("monospace", 64, bold=True)


def draw_button(rect, text, color, hover_color, font: Optional[pygame.font.Font] = None):
    # Simple reusable button for the menu.
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, hover_color if is_hover else color, rect)
    use_font = font or BUTTON_FONT
    label = use_font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
    return is_hover


def draw_panel_button(rect: pygame.Rect, text: str, font: Optional[pygame.font.Font] = None) -> bool:
    # White rectangular buttons for the sidebar/panel.
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    fill = (230, 230, 230) if is_hover else (255, 255, 255)
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, BLACK, rect, 3)

    use_font = font or BUTTON_FONT
    lines = text.split("\n")
    total_height = sum(use_font.size(line)[1] for line in lines) + (len(lines) - 1) * 6
    start_y = rect.centery - total_height // 2
    for line in lines:
        label = use_font.render(line, True, BLACK)
        screen.blit(label, (rect.centerx - label.get_width() // 2, start_y))
        start_y += label.get_height() + 6
    return is_hover


def draw_board(board: np.ndarray) -> None:
    # Draw the board background and all placed discs.
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                screen,
                BLUE,
                (PANEL_WIDTH + c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(PANEL_WIDTH + c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(PANEL_WIDTH + c * SQUARESIZE + SQUARESIZE / 2),
                        WINDOW_HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(PANEL_WIDTH + c * SQUARESIZE + SQUARESIZE / 2),
                        WINDOW_HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )


def draw_game_over(message: str, color, play_again_rect: pygame.Rect, exit_rect: pygame.Rect) -> None:
    # Overlay when the game ends.
    pygame.draw.rect(screen, BLACK, (PANEL_WIDTH, 0, BOARD_WIDTH, SQUARESIZE))
    label = GAME_OVER_FONT.render(message, True, color)
    screen.blit(label, (PANEL_WIDTH + (BOARD_WIDTH - label.get_width()) // 2, 8))

    draw_panel_button(play_again_rect, "Play again")
    draw_panel_button(exit_rect, "Exit")


def draw_side_panel(
    turn: int,
    last_move_msg: str,
    status_msg: str,
    warning_msg: str,
    recommendation_msg: str,
    undo_rect: pygame.Rect,
    restart_rect: pygame.Rect,
    solution_rect: pygame.Rect,
) -> None:
    # Render the sidebar with status and controls.
    screen.fill(BLACK, (0, 0, PANEL_WIDTH, WINDOW_HEIGHT))

    y = 20
    label_turn = TURN_FONT.render("Turn:", True, TEXT_LIGHT)
    screen.blit(label_turn, (20, y))
    y += label_turn.get_height() - 10

    turn_text = "Your turn" if turn == PLAYER else "Bot's turn"
    turn_color = RED if turn == PLAYER else YELLOW
    turn_lbl = TURN_FONT.render(turn_text, True, turn_color)
    screen.blit(turn_lbl, (20, y))
    y += turn_lbl.get_height() + 16

    last_move_lbl = INSTRUCTIONS_FONT.render("Last move:", True, TEXT_LIGHT)
    screen.blit(last_move_lbl, (20, y))
    y += last_move_lbl.get_height() + 4
    
    for line in str(last_move_msg).replace("\\n", "\n").split("\n"):
        last_move_val = INSTRUCTIONS_FONT.render(line, True, YELLOW)
        screen.blit(last_move_val, (20, y))
        y += last_move_val.get_height() + 2
    y += 12

    # Accept either real newlines or literal "\\n" sequences
    for line in str(status_msg).replace("\\n", "\n").split("\n"):
        status_lbl = INSTRUCTIONS_FONT.render(line, True, TEXT_LIGHT)
        screen.blit(status_lbl, (20, y))
        y += status_lbl.get_height() + 2
    y += 8

    if warning_msg:
        warning_lbl = INSTRUCTIONS_FONT.render(warning_msg, True, WARNING_COLOR)
        screen.blit(warning_lbl, (20, y))
        y += warning_lbl.get_height() + 10

    if recommendation_msg:
        for line in str(recommendation_msg).replace("\\n", "\n").split("\n"):
            hint_val = TEXT_FONT.render(line, True, TEXT_LIGHT)
            screen.blit(hint_val, (20, y))
            y += hint_val.get_height() + 2
        y += 6

    draw_panel_button(undo_rect, "Undo move")
    draw_panel_button(restart_rect, "Restart")
    draw_panel_button(solution_rect, "Request Solution", BUTTON_FONT_SMALL)
def show_menu():
    # Simple main menu loop.
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        title = TITLE_FONT.render("Four in a row!", True, (200, 200, 200))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        btn_w, btn_h = 320, 70
        start_rect = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, 220, btn_w, btn_h)
        inst_rect = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, 310, btn_w, btn_h)
        exit_rect = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, 400, btn_w, btn_h)

        draw_button(start_rect, "Play", RED, (255, 80, 80))
        draw_button(inst_rect, "Instructions", BLUE, (80, 80, 255))
        draw_button(exit_rect, "Exit", BLUE, (80, 80, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    return "start"
                if inst_rect.collidepoint(event.pos):
                    return "instructions"
                if exit_rect.collidepoint(event.pos):
                    return "exit"

        pygame.display.flip()
        clock.tick(60)


def show_instructions():
    # Full-screen instructions page.
    clock = pygame.time.Clock()
    lines = [
        "Drop discs to make 4 in a row.",
        "Red: Player, Yellow: Bot.",
        "Click a column to place your piece.",
		"Player can win by connecting 4 discs",
		"horizontally, vertically, or diagonally.",
		" ",
        "Use Undo to revert the last move.",
        "Request Solution for a suggested move.",
        "Press any key or click to return.",
    ]
    while True:
        screen.fill(BLACK)
        y = 140
        for line in lines:
            lbl = INSTRUCTIONS_FONT.render(line, True, (200, 200, 200))
            screen.blit(lbl, (WINDOW_WIDTH // 2 - lbl.get_width() // 2, y))
            y += 50

        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return

        pygame.display.flip()
        clock.tick(60)


def get_recommended_move(board: np.ndarray) -> Tuple[Optional[int], str]:
    # Return a single suggested move for the player.
    if is_terminal_node(board):
        return None, "Board is already in a finished state."
    col, score = pick_best_move(board, PLAYER_PIECE)
    if col is None:
        return None, "No valid moves."
    return col, f"Drop in column {col + 1}."


def run_game():
    # Main game loop: handles turns, UI, and undo stack.
    board = create_board()
    game_over = False
    turn = PLAYER
    history = []  # Acts as a stack of moves for undo.
    last_move_msg = "No moves yet."
    status_msg = "Waiting for \nplayer's turn..."
    warning_msg = ""
    recommendation_msg = ""
    game_over_msg = ""
    game_over_color = TEXT_LIGHT
    ai_think_start = None

    undo_rect = pygame.Rect(30, WINDOW_HEIGHT - 240, PANEL_WIDTH - 60, 55)
    restart_rect = pygame.Rect(30, WINDOW_HEIGHT - 170, PANEL_WIDTH - 60, 55)
    solution_rect = pygame.Rect(30, WINDOW_HEIGHT - 100, PANEL_WIDTH - 60, 55)
    play_again_rect = pygame.Rect(40, WINDOW_HEIGHT // 2 - 40, PANEL_WIDTH - 80, 50)
    exit_rect = pygame.Rect(40, WINDOW_HEIGHT // 2 + 30, PANEL_WIDTH - 80, 50)

    def update_display():
        draw_board(board)
        if not game_over:
            draw_side_panel(
                turn,
                last_move_msg,
                status_msg,
                warning_msg,
                recommendation_msg,
                undo_rect,
                restart_rect,
                solution_rect,
            )
        else:
            screen.fill(BLACK, (0, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        if game_over:
            draw_game_over(game_over_msg, game_over_color, play_again_rect, exit_rect)
        pygame.display.update()

    update_display()
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                # Redraw to refresh hover states on buttons and preview disc.
                update_display()
                if not game_over:
                    pygame.draw.rect(screen, BLACK, (PANEL_WIDTH, 0, BOARD_WIDTH, SQUARESIZE))
                    if turn == PLAYER:
                        mouse_x = event.pos[0]
                        if PANEL_WIDTH <= mouse_x <= PANEL_WIDTH + BOARD_WIDTH:
                            pygame.draw.circle(screen, RED, (mouse_x, int(SQUARESIZE / 2)), RADIUS)
                    pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                warning_msg = ""
                recommendation_msg = ""

                if game_over:
                    if play_again_rect.collidepoint(event.pos):
                        board = create_board()
                        history.clear()
                        turn = PLAYER
                        game_over = False
                        last_move_msg = "No moves yet."
                        status_msg = "Waiting for \nplayer's turn..."
                        warning_msg = ""
                        recommendation_msg = ""
                        game_over_msg = ""
                        game_over_color = TEXT_LIGHT
                        update_display()
                        continue
                    if exit_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    continue

                if undo_rect.collidepoint(event.pos):
                    if history:
                        col, row, piece = history.pop()
                        board[row][col] = EMPTY
                        last_move_msg = f"Undid move at \ncolumn {col + 1}"
                        status_msg = "Previous move has \nbeen undone."
                        turn = PLAYER if piece == PLAYER_PIECE else AI
                        ai_think_start = None if turn == PLAYER else pygame.time.get_ticks()
                        game_over = False
                    else:
                        warning_msg = "Nothing to undo."
                    update_display()
                    continue

                if restart_rect.collidepoint(event.pos):
                    board = create_board()
                    history.clear()
                    turn = PLAYER
                    game_over = False
                    last_move_msg = "No moves yet."
                    status_msg = "Game restarted. Your turn."
                    warning_msg = ""
                    recommendation_msg = ""
                    game_over_msg = ""
                    game_over_color = TEXT_LIGHT
                    ai_think_start = None
                    update_display()
                    continue

                if solution_rect.collidepoint(event.pos):
                    if game_over:
                        warning_msg = "Game over. Restart to request a move."
                    else:
                        col, message = get_recommended_move(board)
                        if col is not None:
                            recommendation_msg = f"Recommended move:\n{message}"
                            status_msg = ""
                        else:
                            warning_msg = message
                    update_display()
                    continue

                if game_over:
                    warning_msg = "Game finished. Restart or undo."
                    update_display()
                    continue

                if turn == PLAYER:
                    mouse_x = event.pos[0]
                    if mouse_x < PANEL_WIDTH or mouse_x > PANEL_WIDTH + BOARD_WIDTH:
                        continue
                    col = int(math.floor((mouse_x - PANEL_WIDTH) / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)
                        history.append((col, row, PLAYER_PIECE))
                        last_move_msg = f"Player dropped at\ncolumn {col + 1}"

                        if winning_move(board, PLAYER_PIECE):
                            status_msg = "Player wins!"
                            game_over_msg = "Player wins!"
                            game_over_color = RED
                            game_over = True
                        elif len(get_valid_locations(board)) == 0:
                            status_msg = "It's a draw."
                            game_over_msg = "Draw Game!"
                            game_over_color = TEXT_LIGHT
                            game_over = True
                        else:
                            status_msg = "Bot is thinking..."
                            turn = AI
                            ai_think_start = pygame.time.get_ticks()
                        update_display()
                    else:
                        warning_msg = f"Column {col + 1} is full."
                        status_msg = "Waiting for\nplayer's turn..."
                        update_display()

        if turn == AI and not game_over:
            if ai_think_start is None:
                ai_think_start = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - ai_think_start
            if elapsed < 2000:
                # Keep showing "Bot is thinking..." while allowing undo/restart.
                continue

            status_msg = "Bot is thinking..."
            update_display()
            col, _ = pick_best_move(board.copy(), AI_PIECE)

            if col is None:
                status_msg = "No valid moves left."
                game_over_msg = "Draw Game!"
                game_over_color = TEXT_LIGHT
                game_over = True
                ai_think_start = None
                update_display()
                continue

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                history.append((col, row, AI_PIECE))
                last_move_msg = f"Bot dropped at\ncolumn {col + 1}"

                if winning_move(board, AI_PIECE):
                    status_msg = "Bot wins!"
                    game_over_msg = "Bot wins!"
                    game_over_color = YELLOW
                    game_over = True
                elif len(get_valid_locations(board)) == 0:
                    status_msg = "It's a draw."
                    game_over_msg = "Draw Game!"
                    game_over_color = TEXT_LIGHT
                    game_over = True
                else:
                    status_msg = "Waiting for \nplayer's turn..."
                    turn = PLAYER
                    ai_think_start = None
                update_display()
            else:
                warning_msg = "Bot attempted an invalid move."
                status_msg = "Restart to continue."
                game_over_msg = "Invalid move"
                game_over_color = WARNING_COLOR
                game_over = True
                ai_think_start = None
                update_display()


def main():
    # Loop back to menu after each finished run.
    while True:
        choice = show_menu()
        if choice == "start":
            run_game()
        elif choice == "instructions":
            show_instructions()
        elif choice == "exit":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
