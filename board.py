class Board:
    def __init__(self, name: str, board: list[list[str]]):
        self.name = name
        self.board = board
        self.is_base = name == 'base'

    def rotate(self, R: int):
        """Rotate the board R times clockwise by 90 degrees each."""
        rotated_board = self.board
        for _ in range(R % 4):
            rotated_board = [list(row) for row in zip(*rotated_board[::-1])]
        return Board(self.name, rotated_board)

    def copy(self):
        return Board(self.name, [row[:] for row in self.board])

    def print_board(self) -> None:
        """Display the board in the specified format."""
        for row in self.board:
            print(''.join(row))
