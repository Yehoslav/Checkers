import math
from collections import namedtuple
from typing import NamedTuple

# Position = namedtuple("Positionition", "file rank")
class Position(NamedTuple):
    file: int
    rank: int

    def __repr__(self):
        return f"{'abcdefgh'[self.file]}{self.rank + 1}"


class Checker:
    @property
    def pos(self) -> Position:
        """The pos property."""
        return Position(self.file, self.rank)

    def __init__(self, ch_type, is_hero, file, rank) -> None:
        self.type = ch_type
        self.is_hero = is_hero
        self.file = file
        self.rank = rank


def get_cell(board, cell_pos: Position):
    return board[cell_pos.file][cell_pos.rank]


def get_checker(pos: Position, checkers: set[Checker]) -> Checker | None:
    for checker in checkers:
        if checker.pos == pos:
            return checker


def pos(x):
    rdsin = lambda a: round(math.sin(math.radians(a)))
    rdcos = lambda a: round(math.cos(math.radians(a)))
    return (rdcos(90 * x) + rdsin(90 * x), rdsin(90 * x) - rdcos(90 * x))


def get_immetidate_moves(board, checker_pos, checker_type, checkers: Checker, move_chain = None) -> set:
    """
    Gets the next immediate moves from the given position (i.e. move one square or 
                                                           eat one checker)
    """

    if move_chain is None:
        move_chain = (( "start",  checker_pos), )

    def add(pos1: Position | tuple, pos2: tuple | Position ) -> Position:
        return Position(pos1[0] + pos2[0], pos1[1] + pos2[1])

    def empty(board, pos) -> bool:
        if not (0 <= pos.file <= 7 and 0 <= pos.rank <= 7):
            return False
        return not board[pos.file][pos.rank]["is_occupied"]

    # Check each immidiate position if empty
    d = 1 if checker_type == "white" else -1
    FL = (d*-1,  1) # FrontLeft
    FR = (d* 1,  1) # FrontRight
    BR = (d*-1, -1) # BackRight
    BL = (d* 1, -1) # BackLeft


    def get_im_moves(board, checker_pos, direction, move_chain):
        im_pos = add(checker_pos, direction)
        for move in move_chain:
            if move[0] == 'eat' and move[1] == im_pos:
                return move_chain + (("dead end", im_pos),)

        # print(im_pos)
        if empty(board, im_pos):
            # print(im_pos, "is an empty cell")
            if move_chain[-1][0] == "start":
                return move_chain + (("move", im_pos),)
        elif get_checker(im_pos, checkers).type != checker_type:
            jump_pos = add(checker_pos, add(direction, direction))

            if empty(board, jump_pos):
                return move_chain + (("eat",  im_pos,  jump_pos),)
        return move_chain + (("dead end", im_pos),)

    return { get_im_moves(board, checker_pos, pe, move_chain) for pe in (FL, FR, BR, BL) }


def get_moves(board, checker, checkers):
    move_chains = get_immetidate_moves(board, checker.pos, checker.type, checkers)
    
    min_len = 2
    def found_all_moves(chain) -> bool:
        for moves in chain:
            # print(moves)
            if moves[-1][0] != "dead end" and len(moves) >= min_len:
                return False 
        return True 


    while not found_all_moves(move_chains):
        # if input("Continue: ") != "":
        #     break

        for moves in move_chains:
            if moves[-1][0] == "eat":
                move_chains = move_chains | get_immetidate_moves(board, moves[-1][2], checker.type, checkers, moves)

        # print(move_chains)
        min_len += 1

    return {moves for moves in move_chains if moves[-1][0] != "dead end"}


def move_checker(board, checker, f_pos: Position, checkers: set):
    move_chains = get_moves(board, checker, checkers)

    def find_move(checker, final_position, move_chains):
        for move_chain in move_chains:
            if move_chain[-1][-1] == final_position:
                return move_chain
        return ()


    move_chain = find_move(checker, f_pos, move_chains)

    if len(move_chain) == 0:
        Exception("Move not allowed!")

    for move in move_chain:
        match move:
            case ("start", start_p):
                continue 
            case ("eat", eat_p, end_p):
                board[checker.file][checker.rank]["is_occupied"] = False
                board[eat_p.file][eat_p.rank]["is_occupied"] = False
                board[end_p.file][end_p.rank]["is_occupied"] = True

                checker.file = end_p.file
                checker.rank = end_p.rank
                if (eaten_checker := get_checker(eat_p, checkers)) is None:
                    raise Exception("Did not find the checker to eat at position:", repr(eat_p))
                eaten_checker.file = 10
                eaten_checker.rank = 10
            case ("move", end_p):
                board[checker.file][checker.rank]["is_occupied"] = False
                board[end_p.file][end_p.rank]["is_occupied"] = True

                checker.file = end_p.file
                checker.rank = end_p.rank
            case unknown:
                print("unknown move:", unknown) 



def create_board(empty = False):
    board = [
        [{"rank": rank, "file": file, "is_occupied": False} for rank in range(8)]
        for file in range(8)
    ]
    
    w_player_pices = {
        Checker(is_hero=False, ch_type="white", rank=0, file=0) for _ in range(12)
    }
    b_player_pices = {
        Checker(is_hero=False, ch_type="black", rank=0, file=0) for _ in range(12)
    }

    if empty:
        return board, w_player_pices, b_player_pices

    for i, pice in enumerate(w_player_pices):
        r = pice.rank = i * 2 // 8
        f = pice.file = (i * 2) % 8 + r % 2
        board[f][r]["is_occupied"] = True

    for i, pice in enumerate(b_player_pices):
        r = pice.rank = 7 - i * 2 // 8
        f = pice.file = (i * 2) % 8 + (r) % 2
        board[f][r]["is_occupied"] = True

    return board, w_player_pices, b_player_pices
