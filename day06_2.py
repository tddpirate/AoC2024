#!/usr/bin/env python
########################################################################
#
# day06_2.py
# Was written for AoC2024
#
########################################################################
import copy
from dataclasses import dataclass
import sys
from typing import Dict, List, Set, Tuple

DEBUG1 = True
DEBUG2 = False

########################################################################
# Classes
########################################################################


@dataclass
class Coords:
    lind: int  # Line No.
    pos: int  # Position in Line

    def __repr__(self) -> str:
        return f"<x{self.lind}y{self.pos}>"

    def __hash__(self) -> int:
        """Assuming that all coordinates are > -10000"""
        return (self.lind + 10000) * (self.pos + 10000)

    def __add__(self, value, /):
        return Coords(self.lind + value.lind, self.pos + value.pos)


########################################################################
# Auxiliary data structures
########################################################################

# Translate from character into direction
GUARDDIRS: Dict[str, Coords] = {
    # value[0]: current position, value[1]: turn to the right
    "^": Coords(-1, 0),
    ">": Coords(0, +1),
    "v": Coords(+1, 0),
    "<": Coords(0, -1),
}

# Turn 90deg to the right
TURN90DEG: Dict[Coords, Coords] = {
    Coords(-1, 0): Coords(0, +1),
    Coords(0, +1): Coords(+1, 0),
    Coords(+1, 0): Coords(0, -1),
    Coords(0, -1): Coords(-1, 0),
}

########################################################################
# Classes for raising exceptions
########################################################################


class error(Exception):
    pass


class StopLoop(Exception):
    pass


########################################################################
# Big functions
########################################################################


def traverse(
    initial_map: List[str],
    initial_guardpos: Coords,
    initial_guarddir: Coords,
) -> Tuple[str, Set[Coords]]:
    guardpos = initial_guardpos
    guarddir = initial_guarddir
    MAP = copy.deepcopy(initial_map)

    visited_pos: Set[Coords] = set()
    visited_pos_dir: Set[Tuple[Coords, Coords]] = set()  # used to detect loops

    while True:
        if DEBUG2:
            sys.stdout.write(
                f"Iteration: guard is at {guardpos}, direction {guarddir}. Already visited {len(visited_pos)} positions excluding the current one.\n"
            )
        if (guardpos, guarddir) in visited_pos_dir:
            # got into infinite loop
            if DEBUG2:
                sys.stdout.write("Ending due to infinite loop\n")
            return ("INFINITE-LOOP", visited_pos)
        visited_pos.add(guardpos)
        visited_pos_dir.add((guardpos, guarddir))

        nextpos = guardpos + guarddir
        if (0 <= nextpos.lind and nextpos.lind < len(MAP)) and (
            0 <= nextpos.pos and nextpos.pos < len(MAP[0])
        ):
            if MAP[nextpos.lind][nextpos.pos] == "#":
                # Obstacle, turn to the right.
                guarddir = TURN90DEG[guarddir]
                if DEBUG2:
                    sys.stdout.write(f"Obstacle at {nextpos}, turning to {guarddir}\n")
            else:
                guardpos = nextpos
        else:
            if DEBUG2:
                sys.stdout.write("Ending due to leaving the map\n")
            return ("LEFT-MAP", visited_pos)


########################################################################
if __name__ == "__main__":
    ########################################################################
    # Input data parsing
    ########################################################################

    MAP: List[str] = []
    guardpos: Coords = Coords(-1, -1)
    guarddir: Coords = Coords(0, 0)

    lind = 0
    for line in sys.stdin:
        sline = line.strip()
        if len(sline) == 0:
            # Ignore empty lines, no special processing is needed.
            continue

        # Is the guard in the current line?
        for cind, ch in enumerate(sline):
            if ch in GUARDDIRS:
                if guarddir != Coords(0, 0):
                    raise error(
                        "More than one guard found",
                        guardpos,
                        guarddir,
                        Coords(lind, cind),
                        GUARDDIRS[ch],
                    )
                guardpos = Coords(lind, cind)
                guarddir = GUARDDIRS[ch]
                if DEBUG1:
                    sys.stdout.write(
                        f"Found the guard at {guardpos}, direction {guarddir}.\n"
                    )

        MAP.append(sline)
        lind += 1

    if guarddir == Coords(0, 0):
        raise error("The guard was not found anywhere")

    if DEBUG1:
        sys.stdout.write(
            f"Map has {len(MAP)} lines, line is {len(MAP[0])} positions long.\n"
        )

    ########################################################################
    # First part
    ########################################################################
    (status, visited_pos) = traverse(MAP, guardpos, guarddir)
    if DEBUG1:
        sys.stdout.write(f"Return value from traverse: {status}\n")

    sys.stdout.write(f"\n\nFirst part answer: {len(visited_pos)}\n\n")

    ########################################################################
    # Second part
    ########################################################################
    # 1. Compute candidate positions for getting the guard to loop.

    blockage_candidates: Set[Coords] = set()
    turn90deg = TURN90DEG.values()
    for pos in visited_pos:
        for delta in turn90deg:
            next_candidate = pos + delta
            if (0 <= next_candidate.lind and next_candidate.lind < len(MAP)) and (
                0 <= next_candidate.pos and next_candidate.pos < len(MAP[0])
            ):
                blockage_candidates.add(next_candidate)
    blockage_candidates.discard(guardpos)  # Do not obscure guard's initial position.
    if DEBUG1:
        sys.stdout.write(
            f"There are {len(blockage_candidates)} obstruction candidates at:\n"
        )

    ########################################################################
    # 2. Evaluate each blockage candidate.
    passed_candidates: Set[Coords] = set()

    counter = 0
    for candidate in blockage_candidates:
        curmap = copy.deepcopy(MAP)
        row_to_update = curmap[candidate.lind][:]
        updated_row = (
            row_to_update[: candidate.pos] + "#" + row_to_update[candidate.pos + 1 :]
        )
        curmap[candidate.lind] = updated_row
        (status, visited_pos) = traverse(curmap, guardpos, guarddir)
        if DEBUG1:
            if counter % 100 == 0:
                sys.stdout.write(
                    f"{counter}/{len(blockage_candidates)}: {candidate=}: {status=} positions={len(visited_pos)}\n"
                )
        if status == "INFINITE-LOOP":
            passed_candidates.add(candidate)

        counter += 1

    ########################################################################
    # Write out answer
    ########################################################################

    answer = len(passed_candidates)
    sys.stdout.write(f"\n\nANSWER ---> {answer=}\n")

else:
    pass

########################################################################
# End of day06_2.py
