from .checkers import Position, Checker

def alpha_to_pos(alpha: str) -> Position:
    if len(alpha) != 2:
        raise ValueError("The Alphanumeric notation can only have a length of 2. I.e a2, b5")
    if 97 <= ord(alpha[0]) <= 104:
        return Position(
            ord(alpha[0]) - 97,
            int(alpha[1]) -1 ,
        )
    raise ValueError("The first element of the Alphanumeric notation should be in range a-h.")

def pos_to_alpha(pos: Position) -> str:
    return f"{'abcdefgh'[pos.file]}{pos.rank + 1}"

def parse_move_chain(move_chain) -> str:
    parsed_move = ""
    for move in move_chain:
        match move:
            case ["start", c_pos]:
                parsed_move += pos_to_alpha(c_pos)
            case ["move", c_pos]:
                parsed_move += " -> " + pos_to_alpha(c_pos)
            case ["eat", b_pos, c_pos]:
                parsed_move += " -/ " + pos_to_alpha(b_pos) + " /-> " + pos_to_alpha(c_pos )
    return parsed_move


def board_to_str(board: list[list[dict]], checkers: dict[Position, Checker]) -> str:
    str_board = "n | 1 2 3 4 5 6 7 8\n--+----------------\n"
    for i, column in enumerate(board):
        str_board += f"{'abcdefgh'[i]} | "
        for square in column:
            cell_color =  square["file"] + square["rank"]
            cell_char = ""
            if cell_color % 2 == 0:
                cell_char = ". "

            if cell_color % 2 == 1:
                cell_char = "* "


            if square["is_occupied"]:
                cell_char = "o " if checkers[Position(square["file"], square["rank"])].type == "white" else "@ "

            str_board += cell_char
            if square["rank"] == 7:
                str_board += "\n"

    return str_board


