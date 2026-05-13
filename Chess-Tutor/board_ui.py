import pygame  # Imports pygame library so we can draw graphics and handle input
import chess   # Imports python-chess library for board logic and legal moves

# Import constants that control board size, colors, and difficulty we created on settings.py
from settings import (
    ROWS,
    COLS,
    SQUARE_SIZE,
    LIGHT_SQUARE,
    DARK_SQUARE,
    EASY,
    HARD,
    TOP_BAR_HEIGHT,
)

#colors (last value is transparency) #had to search up how to make them more transparent.
GREEN = (0, 255, 0, 120)         # Used for move highlights
RED = (255, 0, 0, 120)           # Used for danger / check highlights
SELECT_COLOR = (255, 255, 0, 90) # Used for selected square overlay


class BoardUI:
    def __init__(self, screen, difficulty):
        self.screen = screen               # The main pygame window surface
        self.board = chess.Board()         # Creates a fresh chess board (starting position)

        # Creates a font object used for rendering text (not heavily used here but available)
        self.font = pygame.font.SysFont("Arial", 44)

        self.selected_square = None        # Stores which square the player has clicked (None = nothing selected)
        self.difficulty = difficulty       # Stores difficulty level (affects highlights)

        self.images = {}                   # Dictionary to store piece images (e.g. "wp"= white pawn , "bk"= black king)

        self.load_images()                 # Calls function to load all piece images into memory

        self.last_move = None              # Stores the most recent move for highlighting

    def load_images(self):
        pieces = ["p", "r", "n", "b", "q", "k"]  # List of piece types (pawn, rook, knight, bishop, queen, king) these were also used to name the images per chess pieces

        for piece in pieces:
            # Load white and black images from assets folder
            self.images["w" + piece] = pygame.image.load(f"assets/w{piece}.png")
            self.images["b" + piece] = pygame.image.load(f"assets/b{piece}.png")

            # Resize images to match square size so they fit on the board
            self.images["w" + piece] = pygame.transform.scale(
                self.images["w" + piece], (SQUARE_SIZE, SQUARE_SIZE)
            )
            self.images["b" + piece] = pygame.transform.scale(
                self.images["b" + piece], (SQUARE_SIZE, SQUARE_SIZE)
            )

    def draw_board(self):
        # Loop through each row and column to draw all 64 squares
        for row in range(ROWS):
            for col in range(COLS):
                # Alternate colors based on row + col parity (checkerboard pattern)
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE

                # Draw rectangle at correct screen position
                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        col * SQUARE_SIZE,                  # x position
                        row * SQUARE_SIZE + TOP_BAR_HEIGHT, # y position (offset by top bar)
                        SQUARE_SIZE,                        # width
                        SQUARE_SIZE                         # height
                    )
                )

    def draw_pieces(self):
        # Iterate over all 64 squares
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)  # Get piece on that square

            if piece is not None:  # If a piece exists
                col = chess.square_file(square)          # Get column (0–7)
                row = 7 - chess.square_rank(square)      # Convert to screen row (flip vertically)

                # Determine color prefix for image lookup
                color = "w" if piece.color == chess.WHITE else "b"

                # Convert piece to lowercase symbol (e.g. "P" → "p")
                piece_key = color + piece.symbol().lower()

                image = self.images[piece_key]  # Get correct image

                # Draw image at correct position
                self.screen.blit(
                    image,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE + TOP_BAR_HEIGHT)
                )

    def get_square_from_mouse(self, pos):
        x, y = pos  # Mouse position

        if y < TOP_BAR_HEIGHT:  # If click is in top UI area
            return None        # Ignore it

        y -= TOP_BAR_HEIGHT  # Adjust y so it matches board coordinates

        col = x // SQUARE_SIZE  # Convert pixel x → column index
        row = y // SQUARE_SIZE  # Convert pixel y → row index

        # If click is outside board boundaries
        if not (0 <= col < COLS and 0 <= row < ROWS):
            return None

        chess_row = 7 - row  # Convert to chess coordinate system
        return chess.square(col, chess_row)  # Return square index

    def handle_click(self, pos):
        clicked_square = self.get_square_from_mouse(pos)  # Convert click to square

        if clicked_square is None:
            return False  # Ignore invalid clicks

        piece = self.board.piece_at(clicked_square)  # Get piece at clicked square

        if self.selected_square is None:
            # First click: selecting a piece
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = clicked_square  # Save selected square
            return False

        # Second click: attempt to move selected piece
        move = chess.Move(self.selected_square, clicked_square)

        # Check for pawn promotion
        selected_piece = self.board.piece_at(self.selected_square)
        if selected_piece is not None and selected_piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(clicked_square)

            # If pawn reaches last rank, promote to queen
            if (selected_piece.color == chess.WHITE and target_rank == 7) or (
                selected_piece.color == chess.BLACK and target_rank == 0
            ):
                move = chess.Move(self.selected_square, clicked_square, promotion=chess.QUEEN)

        # If move is valid according to chess rules
        if move in self.board.legal_moves:
            self.board.push(move)        # Apply move to board
            self.last_move = move        # Store move for highlighting
            self.selected_square = None  # Clear selection
            return True

        self.selected_square = None  # Reset selection if move invalid
        return False

    def get_legal_moves_for_selected(self):
        if self.selected_square is None:
            return []  # No selection → no moves

        legal_moves = []

        # Filter all legal moves to only those starting from selected square
        for move in self.board.legal_moves:
            if move.from_square == self.selected_square:
                legal_moves.append(move)

        return legal_moves

    def draw_highlights(self):
        if self.selected_square is None:
            return  # Nothing selected → nothing to highlight

        if self.difficulty == HARD:
            return  # HARD mode removes all helper highlights

        # Get position of selected square
        selected_col = chess.square_file(self.selected_square)
        selected_row = 7 - chess.square_rank(self.selected_square)

        # Draw yellow border around selected piece
        border_rect = pygame.Rect(
            selected_col * SQUARE_SIZE,
            selected_row * SQUARE_SIZE + TOP_BAR_HEIGHT,
            SQUARE_SIZE,
            SQUARE_SIZE
        )
        pygame.draw.rect(self.screen, (255, 215, 0), border_rect, width=4, border_radius=6)

        # Loop through all legal moves for this piece
        for move in self.get_legal_moves_for_selected():
            target_col = chess.square_file(move.to_square)
            target_row = 7 - chess.square_rank(move.to_square)

            piece = self.board.piece_at(move.to_square)

            x = target_col * SQUARE_SIZE
            y = target_row * SQUARE_SIZE + TOP_BAR_HEIGHT

            center_x = x + SQUARE_SIZE // 2
            center_y = y + SQUARE_SIZE // 2

            if piece is not None and piece.color != self.board.turn:
                # Draw green ring if move is a capture
                pygame.draw.circle(
                    self.screen,
                    (0, 220, 0),
                    (center_x, center_y),
                    SQUARE_SIZE // 2 - 8,
                    width=5
                )
            else:
                # Draw small green dot for normal move
                pygame.draw.circle(
                    self.screen,
                    (0, 180, 0),
                    (center_x, center_y),
                    SQUARE_SIZE // 7
                )

        # Show danger (threats) only in EASY mode
        if self.difficulty == EASY:
            temp_board = self.board.copy()      # Copy board so we don't modify real game
            temp_board.turn = not self.board.turn  # Switch to opponent

            for move in temp_board.legal_moves:
                if move.to_square == self.selected_square:
                    attacker_square = move.from_square

                    col = chess.square_file(attacker_square)
                    row = 7 - chess.square_rank(attacker_square)

                    x = col * SQUARE_SIZE
                    y = row * SQUARE_SIZE + TOP_BAR_HEIGHT

                    center_x = x + SQUARE_SIZE // 2
                    center_y = y + SQUARE_SIZE // 2

                    # Draw red ring on attacking enemy piece
                    pygame.draw.circle(
                        self.screen,
                        (220, 60, 60),
                        (center_x, center_y),
                        SQUARE_SIZE // 2 - 10,
                        width=4
                    )

    def draw_last_move(self):
        if not self.last_move:
            return  # No move yet

        # Create semi-transparent surfaces
        from_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        to_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        # Light yellow for origin
        from_surface.fill((255, 235, 120, 70))

        # Stronger yellow for destination
        to_surface.fill((255, 215, 0, 110))

        from_col = chess.square_file(self.last_move.from_square)
        from_row = 7 - chess.square_rank(self.last_move.from_square)

        to_col = chess.square_file(self.last_move.to_square)
        to_row = 7 - chess.square_rank(self.last_move.to_square)

        # Draw highlights
        self.screen.blit(from_surface, (from_col * SQUARE_SIZE, from_row * SQUARE_SIZE + TOP_BAR_HEIGHT))
        self.screen.blit(to_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE + TOP_BAR_HEIGHT))

    def draw_check_highlight(self):
        if not self.board.is_check():
            return  # Only highlight if king is in check

        king_square = self.board.king(self.board.turn)
        if king_square is None:
            return

        col = chess.square_file(king_square)
        row = 7 - chess.square_rank(king_square)

        check_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        check_surface.fill((255, 0, 0, 110))  # Red highlight

        self.screen.blit(
            check_surface,
            (col * SQUARE_SIZE, row * SQUARE_SIZE + TOP_BAR_HEIGHT)
        )