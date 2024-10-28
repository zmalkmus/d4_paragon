import os
import sys
import logging
import copy
import datetime
from board import Board

class ParagonBoard:
    '''
    Diablo 4 Paragon Board
    ----------------------
    1. 5, 21x21 boards
    2. Must hit ALL legendary abilities
    3. Each board can rotate
    4. Make each node a class? D = flat dex, S = 5 str, etc
    
    Output
    ----------------------
        1. Get the shortest path to all legendary nodes?
        3. Instead of shortest path, use highest SCORE
        4. Display all stats acquired on the way
        5. Display PATH

    Tile Mapping
    ----------------------
    START               | S
    GATE                | G

    LEGENDARY 1000, 100 | L
    GLYPH 500           | Y
    RARE 100, 50        | R,r
    MAGIC 50, 10        | M,m
    NORMAL 10, 1        | N,n
    '''

    def __init__(self, 
                character_class: str,
                max_path_len: int = 300,
                board_edge_len: int = 21, 
                class_dir: str = 'classes/'):

        self.character_class = character_class
        self.class_dir = 'classes/'
        self.total_boards = 0
        self.max_path_len = 300
        self.board_edge_len = 21

        self.available_boards = {}
        self.meta_boards = []
        self.stitched_patterns = []
        
        self.load_boards()

    # ===========================
    # Read Methods
    # ===========================

    def load_boards(self):
        """Loads board data for the specified character class from the given directory."""
        directory = os.path.join(self.class_dir, self.character_class)
        
        if not os.path.exists(directory):
            print(f"Directory for character class '{self.character_class}' does not exist.")
            return

        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                board_name = os.path.splitext(filename)[0]
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as file:
                    board_data = [list(line.strip()) for line in file]
                self.available_boards[board_name] = Board(name=board_name, board=board_data)
        
        self.total_boards = len(self.available_boards)

        if ('base' not in self.available_boards):
            print ("ERROR: NO BASE BOARD LOADED. EXITING")
            sys.exit(1)

        print(f"Loaded {len(self.available_boards)} boards for character class '{self.character_class}'.")

    def validate_board(self) -> bool:
        """
        Validate that the board is correct size

        :return: True if the board is valid, False otherwise.
        """

        # Check the number of rows
        if len(self.board) != self.board_edge_len:
            print(f"Validation failed for '{self.name}': Expected {self.board_edge_len} rows, found {len(self.board)}.")
            return False

        for idx, row in enumerate(self.board):
            if len(row) != self.board_edge_len:
                print(f"Validation failed for '{self.name}': Row {idx + 1} expected to have {self.board_edge_len} characters, found {len(row)}.")
                return False

        return True


    # ===========================
    # Evaluation Methods
    # ===========================

    def get_meta_board_dimensions(self):
        """
        Determines the dimensions of the meta board based on the total number of boards (n).

        Dimensions Pattern:
            n: rows x cols
            1: 1x1
            2: 2x1
            3: 3x3
            4: 4x5
            5: 6x7
            6: 8x9
            7: 10x11
            8: 12x13
            9: 14x15
            ...
        """
        
        n = self.total_boards

        if n < 1:
            raise ValueError("n must be >= 1")
        elif n == 1:
            rows, cols = 1, 1
        elif n == 2:
            rows, cols = 2, 1
        elif n == 3:
            rows, cols = 3, 3
        elif n >= 4:
            rows = 2 * n - 4
            cols = 2 * n - 3

        return rows, cols

    def get_meta_board_start(self):
        """
        Determines the starting row and column indices for the meta board based on the total number of boards (n).
        
        Starting Position Pattern:
            n: (row, col)
            1: (0, 0)
            2: (1, 0)
            3: (2, 1)
            4: (3, 2)
            5: (4, 3)
            6: (5, 4)
            7: (6, 5)
            8: (7, 6)
            9: (8, 7)
            ...
        """
        
        n = self.total_boards

        if n < 1:
            raise ValueError("n must be >= 1")
        elif n == 1:
            row, col = 0, 0
        elif n == 2:
            row, col = 1, 0
        elif n == 3:
            row, col = 2, 1
        elif n >= 4:
            row = n - 1
            col = n - 2
        else:
            # This else is technically unnecessary due to the above conditions
            raise ValueError(f"Unhandled case for n = {n}")

        return row, col



    def generate_blank_paragon(self):
        rows, cols = self.get_meta_board_dimensions()
        blank = self.generate_blank_board()
        return [[blank for _ in range(cols)] for _ in range(rows)]

    def generate_blank_board(self):
        board = []
        for i in range(self.board_edge_len):
            r = ''
            for ii in range(self.board_edge_len):
                r += '-'
            board.append(r)

        return Board('blank', board)


    # GONNA NEED TO CONVERT PARAMETERS INTO A SET AND CHECK AGAINST THE BOARDS
    def enumerate_boards(self):
        """Enumerate all possible board combinations"""

        meta_board = self.generate_blank_paragon()

        r, c = self.get_meta_board_start()

        meta_board[r][c] = self.available_boards['base']

        queue = []
        for b in self.available_boards.values():
            if (b.is_base is False):
                queue.append(b)

        self.recur_enumerate_boards(r-1,c,queue,meta_board)


    def recur_enumerate_boards(self, row, col, queue, meta_board):
        directions = [0, 1, 2, 3]

        if len(queue) == 0:
            self.meta_boards.append(copy.deepcopy(meta_board))
            return

        if meta_board[row][col].name != 'blank':
            return

        for b in queue:
            for d in directions:
                m = copy.deepcopy(meta_board)
                rotated_board = b.rotate(d)
                m[row][col] = rotated_board

                temp_queue = [obj for obj in queue if obj.name != b.name]

                if row + 1 < len(meta_board):
                    self.recur_enumerate_boards(row + 1, col, temp_queue, m)
                if row - 1 >= 0:
                    self.recur_enumerate_boards(row - 1, col, temp_queue, m)
                if col + 1 < len(meta_board[0]):
                    self.recur_enumerate_boards(row, col + 1, temp_queue, m)
                if col - 1 >= 0:
                    self.recur_enumerate_boards(row, col - 1, temp_queue, m)


    def stitch_boards(self):
        """Stitch the specific pattern generated by enumerate boards"""
        if not self.meta_boards:
            print("Board patterns not generated.")
            return

        for m in self.meta_boards:
            stitched = []
            for m_row in m:
                for b_row in range(self.board_edge_len):
                    current_row = ["".join(m_col.board[b_row]) for m_col in m_row]
                    stitch_row = " | ".join(current_row)
                    stitched.append(stitch_row)
                stitched.append('=' * (self.board_edge_len * len(m) + (3 * (len(m)-1))) )

            self.stitched_patterns.append(stitched)


    def generate_path_by_score(self):
        pass


    def generate_shortest_path(self):
        pass

    # ===========================
    # Print Methods
    # ===========================

    def print_paragon_board(self, paragon_board):
        for i in range(len(paragon_board)):
            print(i)

    def write_paragon_board(self, filename: str, mode: str = 'w'):
        try:
            with open(filename, mode, encoding='utf-8') as file:
                if mode == 'a' and os.path.getsize(filename) > 0:
                    file.write('\n')  # Add a newline to separate boards
                for row in self.paragon_board:
                    file.write(''.join(row) + '\n')
        except IOError as e:
            logging.error(f"Failed to write paragon board '{self.name}' to '{filename}': {e}")
            print(f"An error occurred while writing to the file: {e}")

    def write_stitched_boards(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.character_class}_stitched_boards_{timestamp}.txt"
        try:
            with open(filename, 'a', encoding='utf-8') as file:
                for stitch in self.stitched_patterns:
                    for row in stitch:
                        file.write(' '.join(row) + '\n')
                    file.write('\n\n\n')

        except IOError as e:
            logging.error(f"Failed to write paragon board '{self.name}' to '{filename}': {e}")
            print(f"An error occurred while writing to the file: {e}")


    def print_path(self, paragon_board):
        pass