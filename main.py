from checkers import checkers as ch
from checkers import utils as u
import itertools


def main():
    # TODO: Create board
    board, w, b = ch.create_board()

    players = itertools.cycle(["white", "black"])

    # TODO: Start game
    checkers = {ch.Position(c.file, c.rank): c for c in w | b}
    print(u.board_to_str(board, checkers))
    player = next(players)
    while True:
        action = input(f"{player}> ")
        match action.split():
            case ["gm", alpha]:
                pos = u.alpha_to_pos(alpha)
                if ch.get_cell(board, pos)["is_occupied"]:
                    print(  ch.get_moves(
                        board,
                        ch.get_checker(pos, w | b),
                        w | b,
                    ))
                else: 
                    print("### The cell is blank!!!")
            case ["mv", s_pos, f_pos]:
                checker = ch.get_checker(
                    u.alpha_to_pos(s_pos), 
                    w if player == "white" else b)

                if checker is None:
                    print("### The cell is blank")
                    continue
                ch.move_checker(
                    board=board,
                    checker=checker,
                    f_pos=u.alpha_to_pos(f_pos), 
                    checkers=w|b)
                player = next(players)
            case ["pb"]:
                checkers = {ch.Position(c.file, c.rank): c for c in w | b}
                print(u.board_to_str(board, checkers))
            case ["q"]:
                break
            case _:
                print("### Unknown action!!!")


if __name__ == "__main__":
    main()
