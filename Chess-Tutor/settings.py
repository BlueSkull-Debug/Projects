# Defines the size of the chessboard (in pixels)
# This controls how large the playable board area is
BOARD_SIZE = 760

# Height of the top UI bar (where turn info, menu, and reset buttons are displayed)
TOP_BAR_HEIGHT = 60

# Width of the right-side panel (used for move history and captured pieces)
SIDE_PANEL_WIDTH = 240

# Total window width = board + side panel
WIDTH = BOARD_SIZE + SIDE_PANEL_WIDTH

# Total window height = board + top bar
HEIGHT = BOARD_SIZE + TOP_BAR_HEIGHT

# Standard chessboard dimensions (8x8 grid)
ROWS = 8
COLS = 8

# Size of each individual square on the board
# Calculated by dividing total board size by number of columns
SQUARE_SIZE = BOARD_SIZE // COLS

# RGB color for light squares on the board (beige tone)
LIGHT_SQUARE = (240, 217, 181) #Searched for Light Square tone with help of ChatGPT

# RGB color for dark squares on the board (brown tone)
DARK_SQUARE = (181, 136, 99) #Searched up darker Color tone on a chess board with help of ChatGPT

# Difficulty labels used throughout the program
# These are compared in logic for AI behavior, highlights, and things of that nature.
EASY = "easy"
MEDIUM = "medium"
HARD = "hard"