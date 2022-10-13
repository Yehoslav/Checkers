import math 
from collections import namedtuple 

Pos = namedtuple("Position", "file rank")


class Checker:

    @property
    def pos(self):
        """The pos property."""
        return Pos(self.file, self.rank)

    def __init__(self, ch_type, is_hero, file, rank) -> None:
        self.type = ch_type
        self.is_hero = is_hero
        self.file = file
        self.rank = rank


def get_cell(board, cell_pos: Pos):
    return board[cell_pos.file][cell_pos.rank]


def get_checker(pos: Pos, checkers: set[Checker]) -> Checker | None:
    for checker in checkers:
        if checker.pos == pos:
            return checker


def pos(x):
    rdsin = lambda a: round(math.sin(math.radians(a)))
    rdcos = lambda a: round(math.cos(math.radians(a)))
    return (rdcos(90*x) + rdsin(90*x), rdsin(90*x) - rdcos(90*x))

def get_av_moves(board, player, ch_pos: Pos, checkers: dict[Pos, Checker]):
    # board[8][8] = [[cell]] 
    #   where:
    #       cell = {rank: ..., file: ..., ocupied_by: ...}
    # player = [white|black]
    # ch_pos = {rank: ..., file: ...}
    # return [{start_cell: ..., end_cell: ..., eaten: [...]}]

    # Is there a checker in the given possition
    # HACK: Should I check if the cell is empty before calling the function
    # if (cell := get_cell(board, ch_pos)) is None:
    #     # TODO: Create a custom Exception for empty cells
    #     raise ValueError("An empty cell selected.")

    # Is the selected checker owned by the player 
    # HACK: Should the get moves care who is the player?
    # maybe check the player before getting the moves?
    # if cell["type"] != player:
    #     # TODO: Create a custom Exception for wrong owner
    #     raise ValueError("The selected checker is not owned by the player.")

    # match get_cell(board, ch_pos):
    #     case {"is_occupied": False, **cell_data}:
    #         # TODO: Create a custom Exception for empty cells
    #         raise ValueError("An empty cell selected.")
    #     case {"ocupied_by": {"type": ch_type, **checker}, **cell_data}  \
    #         if ch_type != player:
    #         # TODO: Create a custom Exception for wrong owner
    #         raise ValueError("The selected checker is not owned by the player.")

    # HACK: Add description and think of a better name
    def move_to(x, y):
        def move(pos):
            return Pos(file=pos.file+x, rank=pos.rank+y,)
        return move

    direction = 1 if player == "white" else -1 
    moves = []

    for p in (pos(i) for i in range(2)):
        f_pos = move_to(x=p[1], y=direction * p[0])(ch_pos)
        if not (0 <= f_pos.file <= 7 and 0 <= f_pos.rank <= 7):
            continue

        if  not get_cell(board, f_pos)["is_occupied"]:
            moves.append(f_pos)

        elif checkers[ch_pos].type != checkers[f_pos].type:
            print(f"beat {checkers[f_pos].type}")

    return moves


def move_checker(board, checker, f_pos: Pos, checkers: dict[Pos, Checker]):
    if f_pos in get_av_moves(board, checker.type, checker.pos, checkers):
        board[f_pos.file][f_pos.rank]["is_occupied"]   = True  
        board[checker.file][checker.rank]["is_occupied"] = False

        checker.file = f_pos.file
        checker.rank = f_pos.rank
    else:
        raise Exception("Move not allowed")



def create_board():
    board = [[{"rank": rank, "file": file, "is_occupied": False} 
              for rank in range(8)] 
                for file in range(8)]
    w_player_pices = {Checker(is_hero=False, ch_type="white", rank=0, file=0) for _ in range(12)}
    b_player_pices = {Checker(is_hero=False, ch_type="black", rank=0, file=0) for _ in range(12)}

    for i, pice in enumerate( w_player_pices ):
        r = pice.rank =  i*2 //8
        f = pice.file = (i*2)% 8 + r % 2
        board[f][r]["is_occupied"] = True

    for i, pice in enumerate( b_player_pices ):
        r = pice.rank = 7 - i*2 //8
        f = pice.file = (i*2)% 8 + (r) % 2
        board[f][r]["is_occupied"] = True

    return board, w_player_pices, b_player_pices


