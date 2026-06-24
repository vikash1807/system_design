""" 
Functional Requirements
1. board -> 3 x 3 grid
2. player vs player
3. inform for invalid selections
4. input -> hardcode in main
5. maintain scoreboard


Non-functional Requirements
1. OOD principals
2. clear console output

Identify entities 
Board -> maintain grid structure, operations like is it full, placing symbols at positions.
cell -> holds value, later we can add other methods like highlighing a cell(winning cells).

"""

from enum import Enum
from dataclasses import dataclass


class Symbol(Enum):
    X = 'X'
    O = 'O'
    EMPTY = '-'


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WINNER_X = "winner_x"
    WINNER_O = "winner_o"
    DRAW = "draw"


class Player:
    def __init__(self, name : str, symbol : Symbol):

        if symbol == symbol.EMPTY:
            raise ValueError("player symbol can't be empty.")
        
        self._name = name
        self._symbol = symbol

    @property
    def name(self):
        return self._name
    
    @property
    def symbol(self):
        return self._symbol
    

class Cell:
    def __init__(self):
        self._symbol = Symbol.EMPTY

    @property
    def symbol(self):
        return self._symbol
    
    @symbol.setter
    def symbol(self, value : Symbol):
        self._symbol = value
    
    def is_empty(self):
        return self._symbol == Symbol.EMPTY


# size of the board and cells
class Board:
    def __init__(self, size : int):
        self._size = size
        self._grid : list[list[Cell]] = []
        self._initialize_board()

    @property
    def size(self):
        return self._size
    
    def _initialize_board(self):
        self._grid = [[Cell() for _ in range(self._size)] for _ in range(self._size)]

    def _validate_position(self, row : int, col : int):
        if row >= self._size or row < 0 or col >= self._size or col < 0:
            raise ValueError("selected grid cell is out of bound.")

    def is_cell_empty(self, row : int, col : int):
        self._validate_position(row, col)

        cell = self._grid[row][col]
        return cell.is_empty()

    def place_symbol(self, row : int, col : int, value : Symbol):
        self._validate_position(row, col)

        if self._grid[row][col].is_empty:
            self._grid[row][col].symbol = value
        else:
            raise ValueError("selected grid is already filled.")
        
    def is_full(self):
        for i in range(self._size):
            for j in range(self._size):
                if self.is_cell_empty(i,j):
                    return False
        return True
                
    def get_cell(self, row: int, col: int) -> Cell:
        self._validate_position(row, col)
        return self._grid[row][col]

    def print_board(self):
        print()
        for i, row in enumerate(self._grid):
            row_str = " | ".join(f" {cell.symbol.value} " for cell in row)
            print(row_str)
            if i < self._size - 1:
                print("-" * (self._size * 5 - 1))
        print()

class Game:
    def __init__(self, player1 : Player, player2 : Player, board_size : int):
        self._board = Board(board_size)
        self._players = [player1, player2]
        self._player_index = 0
        self._status = GameStatus.IN_PROGRESS

    @property
    def status(self):
        return self._status
    
    def _check_win(self, row : int, col : int, symbol : Symbol):
        board = self._board
        size = board.size

        # check for coloumn
        count = 0
        for r in range(size):
            if board.get_cell(r, col).symbol != symbol:
                break
            else:
                count += 1
        if count == size:
            return True
        
        # check for row
        count = 0
        for c in range(size):
            if board.get_cell(row, c).symbol != symbol:
                break
            else:
                count += 1

        if count == size:
            return True
        
        # Check the main diagonal (only if the move is on it)
        if row == col and all(board.get_cell(i, i) == symbol for i in range(size)):
            return True

        # Check the anti-diagonal (only if the move is on it)
        if row + col == size - 1 and all(board.get_cell(i, size - 1 - i)== symbol for i in range(size)):
            return True

        return False

    def make_move(self, row : int, col : int) -> None:
        # check game is over or not
        if self._status != GameStatus.IN_PROGRESS:
            print(f"Game is already over! Winner is {self._status.value}")
            return 
        
        # validate the move
        if not self._board.is_cell_empty(row, col):
            raise Exception("cell already filled.")
        
        # place the symbol
        current_player = self._players[self._player_index]
        self._board.place_symbol(row, col, current_player.symbol)

        # check for win
        if self._check_win(row, col, current_player.symbol):
            self._status = (GameStatus.WINNER_O if current_player.symbol == Symbol.O
                            else GameStatus.WINNER_X)
            return
        
        # check for draw
        if self._board.is_full():
            self._status = GameStatus.DRAW
            return
    
        # switch the player
        self._player_index = (self._player_index + 1)%2

    def print_board(self):
        return self._board.print_board()
    
    @property
    def winner(self):
        if self._status == GameStatus.WINNER_X:
            return next(p.name for p in self._players if p.symbol == Symbol.X)
        elif self._status == GameStatus.WINNER_O:
            return next(p.name for p in self._players if p.symbol == Symbol.O)
        return None
    
def main():
    
    alice = Player("Alice", Symbol.X)
    bob = Player("Bob", Symbol.O)
    game = Game(alice, bob, 3)

    print("========== TIC TAC TOE ==========")

    # Alice (X) completes the top row and wins
    game.make_move(0, 0)  # X at (0,0)
    game.make_move(0, 1)  # X at (0,1)
    game.make_move(1, 1)  # O at (1,1)
    game.make_move(2, 2)  # X at (0,2) - Alice wins!
    game.make_move(1, 0)  # O at (1,0)
    game.make_move(1, 2)  # O at (1,0)
    game.make_move(2, 0)  # O at (1,0)
    # game.make_move(0, 2)  # O at (1,0)
    # game.make_move(2,1)  # O at (1,0)

    game.print_board()
    print(f"Winner: {game.winner}")

if __name__ == "__main__":
    main()