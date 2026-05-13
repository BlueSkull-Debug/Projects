import random  # Imports Python's random library so Easy mode can choose a random legal move
import chess  # Imports python-chess for board objects, legal moves, and chess rules
import chess.engine  # Imports the chess engine module so Stockfish can be used for Medium and Hard difficulty
from settings import EASY, MEDIUM, HARD  # Imports the difficulty labels from settings.py


class ChessAI:
    def __init__(self, difficulty):
        # Saves the chosen difficulty so the AI knows how it should behave
        self.difficulty = difficulty
        self.engine = None  # Starts with no chess engine loaded

        # Only loads Stockfish for Medium and Hard difficulty
        # Easy mode uses random moves, so it does not need the engine
        if self.difficulty in (MEDIUM, HARD):
            self.engine = chess.engine.SimpleEngine.popen_uci("./stockfish")

    def choose_move(self, board):
        # Creates a list of all currently legal moves available on the board
        legal_moves = list(board.legal_moves)

        # If there are no legal moves, the game is over, so return nothing
        if not legal_moves:
            return None

        # Chooses the move style based on the selected difficulty
        if self.difficulty == EASY:
            return self.random_move(legal_moves)

        if self.difficulty == MEDIUM:
            return self.stockfish_move(board, time_limit=0.1)

        if self.difficulty == HARD:
            return self.stockfish_move(board, time_limit=0.5)

        # Fallback option in case the difficulty value is unexpected
        return self.random_move(legal_moves)

    def random_move(self, legal_moves):
        # Picks one legal move at random from the list
        return random.choice(legal_moves)

    def stockfish_move(self, board, time_limit=0.2):
        # If no engine is loaded, fall back to a random move
        # This prevents the program from crashing if Stockfish is unavailable
        if self.engine is None:
            return self.random_move(list(board.legal_moves))

        # Asks Stockfish to choose the best move using the current board position
        # The time_limit controls how long Stockfish is allowed to think
        result = self.engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move  # Returns the move chosen by Stockfish

    def close(self):
        # Shuts down the Stockfish engine cleanly when the game ends or difficulty changes
        if self.engine is not None:
            self.engine.quit()