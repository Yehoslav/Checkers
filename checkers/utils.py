from .checkers import Pos, Checker

def alpha_to_pos(alpha: str) -> Pos:
    if len(alpha) != 2:
        raise ValueError("The Alphanumeric notation can only have a length of 2. I.e a2, b5")
    if 97 <= ord(alpha[0]) <= 104:
        return Pos(
            ord(alpha[0]) - 97,
            int(alpha[1]) -1 ,
        )
    raise ValueError("The first element of the Alphanumeric notation should be in range a-h.")

def pos_to_alpha(pos: Pos) -> str:
    return f"{'abcdefgh'[pos.file]}{pos.rank + 1}"

def board_to_str(board: list[list[dict]], checkers: dict[Pos, Checker]) -> str:
    str_board = "n | 1 2 3 4 5 6 7 8\n--+----------------\n"
    for i, column in enumerate(board):
        str_board += f"{'abcdefgh'[i]} | "
        for square in column:
            cell_color =  square["file"] + square["rank"]
            cell_char = ""
            if cell_color % 2 == 0:
                cell_char = ". "

            if cell_color % 2 == 1:
                cell_char = "# "


            if square["is_occupied"]:
                cell_char = "o " if checkers[Pos(square["file"], square["rank"])].type == "white" else "@ "

            str_board += cell_char
            if square["rank"] == 7:
                str_board += "\n"

    return str_board


