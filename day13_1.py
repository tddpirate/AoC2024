#!/usr/bin/env python
########################################################################
#
# day13_1.py
# Was written for AoC2024
#
########################################################################
from dataclasses import dataclass
from itertools import chain
import re
import sys
from typing import Optional
from typing import List

DEBUG1 = False

########################################################################
# Data structures
########################################################################


@dataclass
class XY:
    x: int
    y: int

    def __repr__(self) -> str:
        return f"XY(x={self.x}, y={self.y})"

    def __hash__(self) -> int:
        """Assuming that all coordinates are nonnegative"""
        return (self.x + 1) * (self.y + 1)


@dataclass
class Claw:
    ba: XY
    bb: XY
    prize: XY

    def __repr__(self) -> str:
        return f"Claw(ba={self.ba}, bb={self.bb}, prize={self.prize})"

    def __hash__(self) -> int:
        """Assuming that all coordinates are nonnegative"""
        return hash(self.ba + 1) * hash(self.bb + 1) * hash(self.prize + 1)


########################################################################
# Patterns
########################################################################

BA_BB_PATTERN: re.Pattern = re.compile(
    r"^\s*Button\s+(?P<label>A|B):\s+X\+(?P<x>\d+),\s+Y\+(?P<y>\d+)\s*$"
)

PRIZE_PATTERN: re.Pattern = re.compile(r"^\s*Prize:\s+X=(?P<x>\d+),\s+Y=(?P<y>\d+)\s*$")


########################################################################
# Classes for raising exceptions
########################################################################


class error(Exception):
    pass


class StopLoop(Exception):
    pass


########################################################################
if __name__ == "__main__":
    ########################################################################
    # Input data parsing
    ########################################################################

    claws: List[Claw] = []
    ba: Optional[XY] = None
    bb: Optional[XY] = None
    prize: Optional[XY] = None

    for line in chain(sys.stdin, ["\n"]):
        sline = line.strip()
        if len(sline) == 0:
            if ba is None and bb is None and prize is None:
                # Ignore extra empty lines, no special processing is needed.
                pass
            elif ba is not None and bb is not None and prize is not None:
                # Finished defining a Claw machine
                if len(sys.argv) > 1:
                    # Adjust for part 2 of the puzzle.
                    prize = XY(
                        x=prize.x + 10_000_000_000_000, y=prize.y + 10_000_000_000_000
                    )
                claws.append(Claw(ba=ba, bb=bb, prize=prize))
                ba = None
                bb = None
                prize = None
            else:
                raise error("Claw definition is incomplete", ba, bb, prize)
        else:
            mo: re.Match = BA_BB_PATTERN.search(sline)
            if mo:
                xyval = XY(x=int(mo.group("x")), y=int(mo.group("y")))
                if mo.group("label") == "A":
                    if ba is not None:
                        raise error(
                            "Duplicate Button A in claw machine", ba, bb, prize, sline
                        )
                    else:
                        ba = xyval
                elif mo.group("label") == "B":
                    if bb is not None:
                        raise error(
                            "Duplicate Button B in claw machine", ba, bb, prize, sline
                        )
                    else:
                        bb = xyval
                else:
                    raise error("Bad Button line in claw machine", ba, bb, prize, sline)
            elif mo := PRIZE_PATTERN.search(sline):
                if prize is not None:
                    raise error("Duplicate Prize in claw machine", ba, bb, prize, sline)
                else:
                    prize = XY(x=int(mo.group("x")), y=int(mo.group("y")))
            else:
                raise error("Malformed line in claw definition", sline)

        if DEBUG1:
            sys.stdout.write(
                f"{sline=}:\n {ba=} {bb=} {prize=}    {len(claws)} so far\n"
            )

    ########################################################################
    # Main loop
    ########################################################################

    tokens_total: int = 0
    prizes_total: int = 0

    for clawind, claw in enumerate(claws):
        # The system of equations in unknowns A,B is:
        #   prize.x = A*ba.x + B*bb.x
        #   prize.y = A*ba.y + B*bb.y
        # Eliminate B:
        #   bb.y*prize.x = A*ba.x*bb.y + B*bb.x*bb.y
        #   bb.x*prize.y = A*ba.y*bb.x + B*bb.x*bb.y
        #   after subtraction: bb.y*prize.x - bb.x*prize.y = A(ba.x*bb.y - ba.y*bb.x)
        # Condition for solution: ba.x*bb.y - ba.y*bb.x != 0 and also integer.
        # A,B need also to be non-negative.
        det = claw.ba.x * claw.bb.y - claw.ba.y * claw.bb.x
        if det == 0:
            sys.stdout.write(f"Claw {clawind} has no solution - zero determinant\n")
            continue
        A_numerator = claw.bb.y * claw.prize.x - claw.bb.x * claw.prize.y
        if (A_numerator % det) != 0:
            sys.stdout.write(
                f"Claw {clawind} has no integer solution {A_numerator} % {det} = {A_numerator % det}\n"
            )
            continue
        A = A_numerator // det
        B_numerator = claw.prize.x - A * claw.ba.x
        if (B_numerator % claw.bb.x) != 0:
            sys.stdout.write(
                f"Claw {clawind} has no integer solution {B_numerator} % {claw.bb.x} = {B_numerator % claw.bb.x}\n"
            )
            continue
        B = B_numerator // claw.bb.x

        if (A < 0) or (B < 0):
            raise error("Negative button presses.", A, B)

        tokens = 3 * (A_numerator // det) + (B_numerator // claw.bb.x)
        tokens_total += tokens
        prizes_total += 1
        if DEBUG1:
            sys.stdout.write(
                f"Claw {clawind}: {A=} {B=}  -->  {tokens=}   {tokens_total=} {prizes_total=}\n"
            )

    ########################################################################
    # Write out answer
    ########################################################################
    answer = tokens_total

    sys.stdout.write(f"\n\nANSWER ---> {answer=}\n")

else:
    pass

########################################################################
# End of day13_1.py
