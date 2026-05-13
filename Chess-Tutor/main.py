import pygame  # Imports pygame for graphics, input handling, and creating the game window
import chess  # Imports python-chess for chess rules, legal moves, and game state management

# Imports window sizes, difficulty names, and layout settings from settings.py
from settings import WIDTH, HEIGHT, EASY, MEDIUM, HARD, TOP_BAR_HEIGHT, SIDE_PANEL_WIDTH, BOARD_SIZE

from board_ui import BoardUI  # Imports the class that draws the board, pieces, and highlights
from ai import ChessAI  # Imports the AI class used to control the computer opponent


def draw_menu(screen, font):
    # Fills the screen with a dark background color for the start menu
    screen.fill((30, 30, 30))

    # Creates and draws the title text at the top center of the menu
    title = font.render("Chess Tutor", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Creates three rectangular buttons for the difficulty choices
    buttons = {
        EASY: pygame.Rect(WIDTH // 2 - 100, 250, 200, 60),
        MEDIUM: pygame.Rect(WIDTH // 2 - 100, 350, 200, 60),
        HARD: pygame.Rect(WIDTH // 2 - 100, 450, 200, 60),
    }

    # Draws each button and places its label in the center
    for text, rect in buttons.items():
        pygame.draw.rect(screen, (70, 70, 70), rect)
        label = font.render(text.capitalize(), True, (255, 255, 255))
        screen.blit(
            label,
            (
                rect.x + rect.width // 2 - label.get_width() // 2,
                rect.y + rect.height // 2 - label.get_height() // 2
            )
        )

    # Returns the button dictionary so clicks can be checked later
    return buttons


def get_game_status(board):
    # Checks the board state and returns a message describing the current game condition
    if board.is_checkmate():
        # If it is checkmate, the side whose turn it is has lost
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate - {winner} Wins!"
    elif board.is_stalemate():
        return "Stalemate"
    elif board.is_insufficient_material():
        return "Draw - Insufficient Material"
    elif board.is_check():
        return "Check"

    # If none of the special conditions apply, return nothing
    return None


def get_move_history_rows(board):
    # Creates a temporary board so moves can be replayed one at a time and converted into SAN notation
    temp_board = chess.Board()
    moves = list(board.move_stack)

    rows = []
    move_number = 1

    # Processes the move stack in pairs: one white move and one black move per row
    for i in range(0, len(moves), 2):
        white_move = temp_board.san(moves[i])
        temp_board.push(moves[i])

        black_move = ""
        if i + 1 < len(moves):
            black_move = temp_board.san(moves[i + 1])
            temp_board.push(moves[i + 1])

        # Stores each turn as a tuple: move number, white move, black move
        rows.append((str(move_number), white_move, black_move))
        move_number += 1

    return rows


def draw_move_history(screen, board, font_small):
    # Starts drawing the move history in the right-side panel
    panel_x = BOARD_SIZE

    # Draws the title for the move history section
    title = font_small.render("Move History", True, (255, 255, 255))
    screen.blit(title, (panel_x + 20, 20))

    # Draws column headers for move number, white moves, and black moves
    header_y = 60
    move_header = font_small.render("#", True, (180, 180, 180))
    white_header = font_small.render("White", True, (180, 180, 180))
    black_header = font_small.render("Black", True, (180, 180, 180))

    screen.blit(move_header, (panel_x + 20, header_y))
    screen.blit(white_header, (panel_x + 55, header_y))
    screen.blit(black_header, (panel_x + 135, header_y))

    rows = get_move_history_rows(board)

    # Controls spacing and limits how many move rows appear on screen
    start_y = 95
    row_height = 30
    max_rows = 10
    visible_rows = rows[-max_rows:]

    # Tracks the newest visible row so it can be highlighted
    last_visible_index = len(visible_rows) - 1

    for i, (move_num, white_move, black_move) in enumerate(visible_rows):
        y = start_y + i * row_height

        # Highlights the most recent visible move row so it stands out
        if i == last_visible_index and visible_rows:
            highlight_rect = pygame.Rect(panel_x + 10, y - 2, SIDE_PANEL_WIDTH - 20, row_height)
            pygame.draw.rect(screen, (55, 55, 55), highlight_rect, border_radius=6)

        # Renders each part of the move history row
        move_text = font_small.render(move_num, True, (200, 200, 200))
        white_text = font_small.render(white_move, True, (255, 255, 255))
        black_text = font_small.render(black_move, True, (255, 255, 255))

        screen.blit(move_text, (panel_x + 20, y))
        screen.blit(white_text, (panel_x + 55, y))
        screen.blit(black_text, (panel_x + 135, y))


def get_captured_pieces(board):
    # Stores how many of each piece each side starts with
    initial_counts = {
        chess.WHITE: {
            chess.PAWN: 8,
            chess.ROOK: 2,
            chess.KNIGHT: 2,
            chess.BISHOP: 2,
            chess.QUEEN: 1,
        },
        chess.BLACK: {
            chess.PAWN: 8,
            chess.ROOK: 2,
            chess.KNIGHT: 2,
            chess.BISHOP: 2,
            chess.QUEEN: 1,
        },
    }

    # Starts current piece counts at zero so we can count what is still on the board
    current_counts = {
        chess.WHITE: {
            chess.PAWN: 0,
            chess.ROOK: 0,
            chess.KNIGHT: 0,
            chess.BISHOP: 0,
            chess.QUEEN: 0,
        },
        chess.BLACK: {
            chess.PAWN: 0,
            chess.ROOK: 0,
            chess.KNIGHT: 0,
            chess.BISHOP: 0,
            chess.QUEEN: 0,
        },
    }

    # Counts all non-king pieces currently remaining on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.KING:
            current_counts[piece.color][piece.piece_type] += 1

    captured_by_white = []
    captured_by_black = []

    # Controls the order captured pieces appear in the display
    piece_order = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]

    # Compares starting counts to current counts to determine what has been captured
    for piece_type in piece_order:
        missing_black = initial_counts[chess.BLACK][piece_type] - current_counts[chess.BLACK][piece_type]
        missing_white = initial_counts[chess.WHITE][piece_type] - current_counts[chess.WHITE][piece_type]

        captured_by_white.extend([("b", piece_type)] * missing_black)
        captured_by_black.extend([("w", piece_type)] * missing_white)

    return captured_by_white, captured_by_black


def draw_captured_pieces(screen, board_ui, board, font_small):
    # Chooses where the captured piece display begins in the side panel
    panel_x = BOARD_SIZE
    start_y = 430

    captured_by_white, captured_by_black = get_captured_pieces(board)

    # Draws section titles for each side's captured pieces
    white_title = font_small.render("Captured by White", True, (255, 255, 255))
    screen.blit(white_title, (panel_x + 20, start_y))

    black_title = font_small.render("Captured by Black", True, (255, 255, 255))
    screen.blit(black_title, (panel_x + 20, start_y + 90))

    # Maps chess piece types to the asset file letters used in the images folder
    piece_letters = {
        chess.QUEEN: "q",
        chess.ROOK: "r",
        chess.BISHOP: "b",
        chess.KNIGHT: "n",
        chess.PAWN: "p",
    }

    icon_size = 28
    spacing = 34

    # Draws the icons for pieces captured by White
    for i, (color_prefix, piece_type) in enumerate(captured_by_white):
        piece_key = color_prefix + piece_letters[piece_type]
        image = pygame.transform.scale(board_ui.images[piece_key], (icon_size, icon_size))
        screen.blit(image, (panel_x + 20 + i * spacing, start_y + 35))

    # Draws the icons for pieces captured by Black
    for i, (color_prefix, piece_type) in enumerate(captured_by_black):
        piece_key = color_prefix + piece_letters[piece_type]
        image = pygame.transform.scale(board_ui.images[piece_key], (icon_size, icon_size))
        screen.blit(image, (panel_x + 20 + i * spacing, start_y + 125))


def draw_endgame_popup(screen, game_status, font, font_small):
    # Creates a dark transparent overlay so the popup stands out
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    # Defines the popup size and centers it on the screen
    popup_width = 420
    popup_height = 220
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2

    # Draws the popup background and border
    pygame.draw.rect(
        screen,
        (40, 40, 40),
        (popup_x, popup_y, popup_width, popup_height),
        border_radius=12
    )
    pygame.draw.rect(
        screen,
        (90, 90, 90),
        (popup_x, popup_y, popup_width, popup_height),
        width=2,
        border_radius=12
    )

    # Draws the end-game message and subtitle
    title = font.render(game_status, True, (255, 215, 0))
    screen.blit(
        title,
        (popup_x + popup_width // 2 - title.get_width() // 2, popup_y + 35)
    )

    subtitle = font_small.render("Game Over", True, (220, 220, 220))
    screen.blit(
        subtitle,
        (popup_x + popup_width // 2 - subtitle.get_width() // 2, popup_y + 95)
    )

    # Creates Menu and Reset buttons inside the popup
    menu_popup_rect = pygame.Rect(popup_x + 55, popup_y + 145, 130, 45)
    reset_popup_rect = pygame.Rect(popup_x + 235, popup_y + 145, 130, 45)

    pygame.draw.rect(screen, (80, 80, 80), menu_popup_rect, border_radius=8)
    pygame.draw.rect(screen, (80, 80, 80), reset_popup_rect, border_radius=8)

    menu_text = font_small.render("Menu", True, (255, 255, 255))
    reset_text = font_small.render("Reset", True, (255, 255, 255))

    # Centers the Menu and Reset text inside their buttons
    screen.blit(
        menu_text,
        (
            menu_popup_rect.x + menu_popup_rect.width // 2 - menu_text.get_width() // 2,
            menu_popup_rect.y + menu_popup_rect.height // 2 - menu_text.get_height() // 2
        )
    )
    screen.blit(
        reset_text,
        (
            reset_popup_rect.x + reset_popup_rect.width // 2 - reset_text.get_width() // 2,
            reset_popup_rect.y + reset_popup_rect.height // 2 - reset_text.get_height() // 2
        )
    )

    # Returns the popup button rectangles so clicks can be detected later
    return menu_popup_rect, reset_popup_rect


def main():
    # Initializes pygame and creates the game window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Tutor")

    # Creates fonts used in different parts of the app
    font = pygame.font.SysFont("Arial", 34)
    font_small = pygame.font.SysFont("Arial", 24)
    font_status = pygame.font.SysFont("Arial", 30, bold=True)
    clock = pygame.time.Clock()

    # Tracks whether the player is at the menu or inside a game
    game_started = False
    board_ui = None
    ai = None

    # Creates the Menu and Reset buttons shown in the top bar during a game
    menu_rect = pygame.Rect(BOARD_SIZE - 280, 10, 120, 40)
    reset_rect = pygame.Rect(BOARD_SIZE - 140, 10, 120, 40)

    # Controls delayed AI movement so the bot does not move instantly
    ai_pending = False
    ai_move_time = 0
    ai_delay_ms = 700

    running = True
    while running:
        # Resets these values every frame so they can be recalculated
        game_status = None
        game_over = False
        menu_popup_rect = None
        reset_popup_rect = None

        if not game_started:
            # Draws the main menu and stores the difficulty button rectangles
            buttons = draw_menu(screen, font)
        else:
            # Gets the current game status and checks whether the game is over
            game_status = get_game_status(board_ui.board)
            game_over = (
                board_ui.board.is_checkmate()
                or board_ui.board.is_stalemate()
                or board_ui.board.is_insufficient_material()
            )

            # Draws the board background, top bar, and side panel
            screen.fill((35, 35, 35))
            pygame.draw.rect(screen, (45, 45, 45), (0, 0, BOARD_SIZE, TOP_BAR_HEIGHT))

            pygame.draw.rect(screen, (28, 28, 28), (BOARD_SIZE, 0, SIDE_PANEL_WIDTH, HEIGHT))
            pygame.draw.line(screen, (70, 70, 70), (BOARD_SIZE, 0), (BOARD_SIZE, HEIGHT), 2)

            # Draws all main board visuals in order
            board_ui.draw_board()
            board_ui.draw_last_move()
            board_ui.draw_check_highlight()
            board_ui.draw_highlights()
            board_ui.draw_pieces()

            # Shows whose turn it is
            turn_text = "White's Turn" if board_ui.board.turn else "Black's Turn"
            text_surface = font_small.render(turn_text, True, (255, 255, 255))
            screen.blit(text_surface, (20, 18))

            # Draws the Menu and Reset buttons
            pygame.draw.rect(screen, (80, 80, 80), menu_rect, border_radius=8)
            menu_text = font_small.render("Menu", True, (255, 255, 255))
            screen.blit(
                menu_text,
                (
                    menu_rect.x + menu_rect.width // 2 - menu_text.get_width() // 2,
                    menu_rect.y + menu_rect.height // 2 - menu_text.get_height() // 2
                )
            )

            pygame.draw.rect(screen, (80, 80, 80), reset_rect, border_radius=8)
            reset_text = font_small.render("Reset", True, (255, 255, 255))
            screen.blit(
                reset_text,
                (
                    reset_rect.x + reset_rect.width // 2 - reset_text.get_width() // 2,
                    reset_rect.y + reset_rect.height // 2 - reset_text.get_height() // 2
                )
            )

            # Shows game status text such as Check, Checkmate, or Draw
            if game_status:
                if game_over:
                    status_color = (255, 215, 0)
                elif game_status == "Check":
                    status_color = (255, 100, 100)
                else:
                    status_color = (255, 255, 255)

                status_surface = font_status.render(game_status, True, status_color)
                screen.blit(
                    status_surface,
                    (BOARD_SIZE // 2 - status_surface.get_width() // 2, 14)
                )

            # Draws the move history and captured pieces on the right-side panel
            draw_move_history(screen, board_ui.board, font_small)
            draw_captured_pieces(screen, board_ui, board_ui.board, font_small)

            # If the game is over, draws the popup overlay with Menu and Reset options
            if game_over:
                menu_popup_rect, reset_popup_rect = draw_endgame_popup(screen, game_status, font, font_small)

        # Checks whether it is time for the AI to make its delayed move
        current_time = pygame.time.get_ticks()
        if game_started and ai_pending and not game_over and current_time >= ai_move_time:
            move = ai.choose_move(board_ui.board)
            if move:
                board_ui.board.push(move)
                board_ui.last_move = move
            ai_pending = False

        # Handles all input events such as quitting and mouse clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_started:
                    # Checks whether the player clicked one of the difficulty buttons on the menu
                    for difficulty, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            board_ui = BoardUI(screen, difficulty)

                            # Closes any previous AI engine before creating a new one
                            if ai:
                                ai.close()

                            ai = ChessAI(difficulty)
                            ai_pending = False
                            game_started = True
                else:
                    # If the game is over, only popup buttons should respond
                    if game_over and menu_popup_rect and reset_popup_rect:
                        if menu_popup_rect.collidepoint(event.pos):
                            game_started = False
                            ai_pending = False

                            if ai:
                                ai.close()
                                ai = None

                        elif reset_popup_rect.collidepoint(event.pos):
                            difficulty = board_ui.difficulty
                            board_ui = BoardUI(screen, difficulty)

                            if ai:
                                ai.close()

                            ai = ChessAI(difficulty)
                            ai_pending = False

                    # Handles top-bar Menu and Reset buttons during gameplay
                    elif menu_rect.collidepoint(event.pos):
                        game_started = False
                        ai_pending = False

                        if ai:
                            ai.close()
                            ai = None

                    elif reset_rect.collidepoint(event.pos):
                        difficulty = board_ui.difficulty
                        board_ui = BoardUI(screen, difficulty)

                        if ai:
                            ai.close()

                        ai = ChessAI(difficulty)
                        ai_pending = False

                    # Lets the player move only if it is White's turn and the AI is not waiting to move
                    elif not ai_pending and board_ui.board.turn == chess.WHITE:
                        player_moved = board_ui.handle_click(event.pos)

                        # If the player made a legal move, schedule the AI's turn
                        if player_moved and board_ui.board.turn == chess.BLACK:
                            ai_pending = True
                            ai_move_time = pygame.time.get_ticks() + ai_delay_ms

        # Updates the display and limits the game to 60 frames per second
        pygame.display.flip()
        clock.tick(60)

    # Closes the AI engine cleanly before exiting the program
    if ai:
        ai.close()

    pygame.quit()  # Shuts down pygame when the game ends


if __name__ == "__main__":
    main()  # Starts the program by calling the main game function