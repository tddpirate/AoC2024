#!/usr/bin/env python
########################################################################
#
# day21_1.py
# Was written for AoC2024
#
########################################################################
import argparse
from itertools import pairwise
import sys
from typing import Dict
from typing import List
from typing import Optional, Tuple

DEBUG1 = True
DEBUG2 = True
DEBUG3 = True
DEBUG4 = False
DEBUG5 = False

########################################################################
# Algorithm design
########################################################################
# For part 1 of the puzzle
# ------------------------
# Numeric keypad (depressurized):
# For each numeric 2-keys, find all keypad1 sequences of keypresses
# going between them.
#
# keypad1 (radiation):
# For each keypad 2-keys sequence, find all keypad2 sequences of
# keypresses going between them.
#
# keypad2 (-40 degrees):
# For each keypad 2-keys sequence, find all keypad3 sequences of
# keypresses going between them.
#
# keypad3 (human):
# The distance between each 2 keys is 1.
#
# Costing each move.
# Keypad1's point of view.
# 1. Start with my A key.
# 2. Sequence of target's movement keys.
# 3. Press on my A key.
# Repeat the above for the next target key.
#
# The sequences interact with each other (optimal sequence depends
# upon the end of the previous sequence). However, A keys serve as
# barriers:
# 1. Target keypad starts with Akey.
# 2. Target keypad moves to a sequence whose length depends upon A key.
# ... etc.

########################################################################
# Initial data structures
########################################################################


class Keypad:
    """
    Keypad definition consists of 3-Tuples of keynames and their
    coordinates.
    """

    MOVEMENTS: Dict[str, Tuple[int, int]] = {
        ">": (1, 0),
        "<": (-1, 0),
        "^": (0, -1),
        "v": (0, 1),
    }

    def validate_sequence_of_movements(
        self, x_from: int, y_from: int, movement: str
    ) -> bool:
        """
        Make a series of movements, starting from (x_from, y_from) and ensure
        that you do not fall on a gap.
        """
        if (x_from, y_from) not in self.legalpositions:
            return False
        (x_curr, y_curr) = (x_from, y_from)

        for mov in movement:
            (dx, dy) = Keypad.MOVEMENTS[mov]
            (x_curr, y_curr) = (x_curr + dx, y_curr + dy)
            if (x_curr, y_curr) not in self.legalpositions:
                if DEBUG2:
                    sys.stdout.write(
                        f"For (x={x_from},y={y_from}) and {movement=}, hit illegal position (x={x_curr},y={y_curr})\n"
                    )
                return False
        return True

    def create_arrow_permutations(
        self, x_from: int, y_from: int, x_to: int, y_to: int
    ) -> List[str]:
        if (x_from, y_from) not in self.legalpositions:
            raise error("Illegal initial position", (x_from, y_from))
        if (x_to, y_to) not in self.legalpositions:
            raise error("Illegal target position", (x_to, y_to))
        horiz = ">" if x_to > x_from else "<"
        vert = "v" if y_to > y_from else "^"
        genstr = horiz * abs(x_to - x_from) + vert * abs(y_to - y_from)
        ## Now, permute genstr and filter it by means of validating function.
        # return [
        #    "".join(permuta)
        #    for permuta in set(permutations(genstr))
        #    if self.validate_sequence_of_movements(
        #        x_from=x_from, y_from=y_from, movement=permuta
        #    )
        # ]
        # ----------
        # Consider only orderings which will yield shortest
        # expansion for next robot in chain.
        permutations = set(
            [
                horiz * abs(x_to - x_from) + vert * abs(y_to - y_from),
                vert * abs(y_to - y_from) + horiz * abs(x_to - x_from),
            ]
        )
        before_preferences = [
            permuta
            for permuta in permutations
            if self.validate_sequence_of_movements(
                x_from=x_from, y_from=y_from, movement=permuta
            )
        ]
        if len(before_preferences) == 1:
            return before_preferences
        # If both permutations are validated, then we reduce to
        # one permutation using the following considration.
        # There are three (horiz,vert) combinations in which we
        # prefer one order over the other one.
        if horiz == "<":
            # In both "^<","v<", we prefer the "<" to come first.
            return [horiz * abs(x_to - x_from) + vert * abs(y_to - y_from)]
        else:
            # In ">v", we prefer the "v>" ordering.
            # In ">^", both orderings are fine, and we choose "^>" to reduce testing.
            return [vert * abs(y_to - y_from) + horiz * abs(x_to - x_from)]

    def __init__(self, definition: List[Tuple[str, int, int]]):
        self.legalpositions: Dict[Tuple[int, int], str] = {
            # A legal position is a position (int,int) having a key.
            (x_pos, y_pos): keyvalue
            for (keyvalue, x_pos, y_pos) in definition
        }
        if DEBUG2:
            sys.stdout.write(f"Keypad instance created, {self.legalpositions=}\n")
        # Generate the basic movements.
        self.movements: Dict[
            str, str
        ] = {}  # Move from any char to any char on this keyboard.
        for keyfrom, x_from, y_from in definition:
            for keyto, x_to, y_to in definition:
                if keyfrom == keyto:
                    continue
                # We want to create all paths from keyfrom to keyto,
                # excluding paths passing over gaps (i.e. having
                # positions not in legalpositions).
                movements: List[str] = [
                    movement + "A"
                    for movement in self.create_arrow_permutations(
                        x_from=x_from, y_from=y_from, x_to=x_to, y_to=y_to
                    )
                ]
                if len(movements) > 1:
                    raise error(
                        "More than one optimal path",
                        keyfrom,
                        x_from,
                        y_from,
                        keyto,
                        x_to,
                        y_to,
                        movements,
                    )
                self.movements[keyfrom + keyto] = movements[0]
        if DEBUG2:
            sys.stdout.write("Lengths of movements for this keypad\n")
            for movement in sorted(self.movements.keys()):
                sys.stdout.write(f"movement {movement} -> {self.movements[movement]}\n")


BOARD_NUMERIC_KEYPAD = Keypad(
    definition=[
        # x_from is from left to right
        # y_from is from top to bottom
        ("7", 0, 0),
        ("8", 1, 0),
        ("9", 2, 0),
        ("4", 0, 1),
        ("5", 1, 1),
        ("6", 2, 1),
        ("1", 0, 2),
        ("2", 1, 2),
        ("3", 2, 2),
        #     0, 3 is forbidden
        ("0", 1, 3),
        ("A", 2, 3),
    ]
)

BOARD_DIRECTIONAL_KEYPAD = Keypad(
    definition=[
        #     0, 0 is forbidden
        ("^", 1, 0),
        ("A", 2, 0),
        ("<", 0, 1),
        ("v", 1, 1),
        (">", 2, 1),
    ]
)

########################################################################
# Shortdata input
########################################################################

target_numeric_keypad_output = "029A"
keypad1_to_control_numeric = ["<A^A>^^AvvvA", "<A^A^>^AvvvA", "<A^A^^>AvvvA"]
keypad2_to_control_keypad1 = ["v<<A>>^A<A>AvA<^AA>A<vAAA>^A"]
keypad3_to_control_keypad2 = [
    "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A"
]

SHORTDATA_TEST: Dict[str, str] = {
    "029A": "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A",
    "980A": "<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A:",
    "179A": "<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
    "456A": "<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A",
    "379A": "<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
}


########################################################################
# Classes for raising exceptions
########################################################################
class error(Exception):
    pass


class StopLoop(Exception):
    pass


########################################################################
# Functions
########################################################################


def expand_line_by_keypad(keypad: Keypad, line: str) -> str:
    aline = "A" + line  # All robots start at position "A".
    retval: str = ""
    for pos_from, pos_to in pairwise(aline):
        if pos_from == pos_to:
            retval += "A"
        else:
            retval += keypad.movements[pos_from + pos_to]
        if DEBUG3:
            if line in ["029A", "379A"]:
                sys.stdout.write(f"{line=} debug: {pos_from=},{pos_to=} -> {retval=}\n")
    return retval


########################################################################
# Plan for handling very long sequences.
#
# For each movement in BOARD_DIRECTIONAL_KEYPAD, expand it 10 times.
# Then for input line which needs to be expanded only 10 more times,
# expand it using the 10-times-expanded stuff and accumulate only
# lengths rather than full strings.


def prepare_10x_expansion_dict(
    factor: int, keypad: Keypad = BOARD_DIRECTIONAL_KEYPAD  # TENx_EXPANSION_FACTOR
) -> Dict[str, int]:
    """
    The return value is Dict from str defining movement to
    length of 10x (or TENx_EXPANSION_FACTOR value) expanded string.
    """
    retval: Dict[str, int] = {}
    for movement in keypad.movements.keys():
        move: str = movement
        if DEBUG1:
            sys.stdout.write(f"Starting move: {move}\n")
        # When starting the move:
        # In 1st iteration, we want to expand only the 2nd ("to")
        # character.
        # The 1st ("from") character merely tells us from where we
        # are coming.
        # In subsequent iterations, 1st character is always the "A"
        # of the previous expanded movement.
        move_expanded = keypad.movements[move]
        move = move_expanded
        if DEBUG1:
            sys.stdout.write(f"Expansion 0: {move[:50]} ({len(move)} chars long)\n")
        for loopind in range(1, factor):
            move_expanded = expand_line_by_keypad(keypad=keypad, line=move)
            move = move_expanded
            if DEBUG1:
                sys.stdout.write(
                    f"Expansion {loopind}: {move[:50]} ({len(move)} chars long)\n"
                )

        retval[movement] = len(move)
        if DEBUG1:
            sys.stdout.write(
                f"prepare_10x_expansion_dict: {movement=} -> length={len(move)}\n"
            )
    return retval


########################################################################


def execute_10x_expansion(movelengths: Dict[str, int], line: str) -> int:
    """
    This function saves time and space by accumulating only
    lengths, rather than the full movement strings.
    """
    aline = "A" + line
    retval: int = 0
    for pos_from, pos_to in pairwise(aline):
        if pos_from == pos_to:
            retval += 1  # corresponds to "A"
            if DEBUG5:
                sys.stdout.write(f"""***** add 1 for "A", yielding {retval=} *****\n""")
        else:
            retval += movelengths[pos_from + pos_to]
            if DEBUG5:
                sys.stdout.write(
                    f"""***** "{pos_from + pos_to}": add {movelengths[pos_from + pos_to]} yielding {retval=} *****\n"""
                )
    return retval


########################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Solve the exercise of day 21 of AoC2024",
        epilog="The chain length is a parameter because it needed to be 2 for 1st part of the Dec 21, 2024 puzzle and 25 for the 2nd part. For debugging I needed it to be 4. The speedup wormhole needed to be 2 for debugging, 10 for production use.",
    )

    parser.add_argument(
        "-c",
        "--chain-length",
        type=int,
        default=2,
        dest="chain_length",
        help="Length of robot chain, typically 2 or 25. Default is %(default)d.",
    )
    parser.add_argument(
        "-w",
        "--wormhole",
        type=int,
        default=10,
        dest="wormhole",
        help="Length of speedup wormhole. Default is %(default)d. 0 turns it off",
    )
    args = parser.parse_args()

    ROBOT_CHAIN_LENGTH: int = args.chain_length
    if ROBOT_CHAIN_LENGTH < 2:
        raise error(
            "--chain-length (ROBOT_CHAIN_LENGTH) argument must be >= 2",
            ROBOT_CHAIN_LENGTH,
        )
    TENx_EXPANSION_FACTOR: int = args.wormhole
    if TENx_EXPANSION_FACTOR < 0:
        raise error(
            "--wormhole (TENx_EXPANSION_FACTOR) argument must not be negative",
            TENx_EXPANSION_FACTOR,
        )

    ########################################################################
    # Input data parsing
    ########################################################################
    dict_10x_expansion: Dict[str, int] = prepare_10x_expansion_dict(
        factor=TENx_EXPANSION_FACTOR, keypad=BOARD_DIRECTIONAL_KEYPAD
    )

    complexities = 0

    for line in sys.stdin:
        sline = line.strip()
        if len(sline) == 0:
            # Ignore empty lines, no special processing is needed.
            continue

        # To perform expansion of a line:
        # Replace each character in the original line by a string
        # from a keypad.movements.
        kp1: str = expand_line_by_keypad(keypad=BOARD_NUMERIC_KEYPAD, line=sline)
        kp1_min = len(kp1)
        sys.stdout.write(f"For {sline=}, expansion 1 length:{kp1_min}\n")

        sys.stdout.write(
            f"config: Will perform {ROBOT_CHAIN_LENGTH}+1 iterations\nconfig: (typically, 2+1 iterations for part 1, 25+1 iterations for part 2)\n"
        )
        sys.stdout.write(f"config: TENx expansion factor is {TENx_EXPANSION_FACTOR}\n")
        kp_prev = kp1
        loopind = 2
        kp_curr_min: int = 0  # Will serve as total sequence length.
        while loopind < ROBOT_CHAIN_LENGTH + 2:
            if loopind == (ROBOT_CHAIN_LENGTH + 2 - TENx_EXPANSION_FACTOR):
                # Jump TENx_EXPANSION_FACTOR (typically 10) expansions
                # then break.
                #
                # Note: if total robot chain length is shorter
                # than TENx_EXPANSION_FACTOR, we do not bother to
                # invoke the speedup.
                kp_curr_min = execute_10x_expansion(
                    movelengths=dict_10x_expansion, line=kp_prev
                )
                sys.stdout.write(
                    f"For {sline=}, expansion {loopind}->{loopind+TENx_EXPANSION_FACTOR} length:{kp_curr_min}\n"
                )
                break
            kp_curr: str = expand_line_by_keypad(
                keypad=BOARD_DIRECTIONAL_KEYPAD, line=kp_prev
            )
            kp_curr_min = len(kp_curr)
            sys.stdout.write(
                f"For {sline=}, expansion {loopind} length:{kp_curr_min}\n"
            )
            if DEBUG5:
                sys.stdout.write(f"***** {kp_curr[:1000]} *****\n")
            kp_prev = kp_curr
            loopind += 1

        complexity: int = kp_curr_min * int(sline[:-1])
        sys.stdout.write(
            f"For {sline=}, complexity is {complexity} = {kp_curr_min} * {int(sline[:-1])}\n"
        )

        complexities += complexity

    ########################################################################
    # Write out answer
    ########################################################################
    answer = complexities
    sys.stdout.write(f"\n\nANSWER ---> {answer=}\n")

else:
    pass

########################################################################
# End of day21_1.py
