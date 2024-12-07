#!/usr/bin/env python
########################################################################
#
# day07_2.py
# Was written for AoC2024
#
########################################################################
import re
import sys
from typing import List

DEBUG1 = True
DEBUG2 = False

########################################################################
# Patterns
########################################################################

FIRST_SPLIT_PATTERN: re.Pattern = re.compile(r"^(?P<result>\d+):(?P<rest>[ 0-9]+)$")


########################################################################
# Classes for raising exceptions
########################################################################
class error(Exception):
    pass


########################################################################
# Functions
########################################################################

def intconcat(val1: int, val2: int) -> int:
    return int(str(val1) + str(val2))


def recurtree(target: int, interim: int, args: List[int]) -> bool:
    """Recursive tree traversal.
       At each node we try both + and *
       Terminate with False if we overshoot the target value
           and/or reach exactly the value but did not empty the args.
       Recurse by calling recurtree(target, interim OP val, args[1:])
    """
    if DEBUG2:
        sys.stdout.write(f"Entered recurtree with {target=} {interim=} {args=}\n")
    if len(args) == 0:
        return interim == target
    if interim > target:
        return False

    if recurtree(target, interim + args[0], args[1:]):
        return True
    elif recurtree(target, interim * args[0], args[1:]):
        return True
    else:
        return recurtree(target, intconcat(interim, args[0]), args[1:])


if __name__ == "__main__":
    ########################################################################
    # Input data parsing
    ########################################################################

    cntgood = 0
    sumgood = 0

    for (lind, line) in enumerate(sys.stdin):
        sline = line.strip()
        if len(sline) == 0:
            # Ignore empty lines, no special processing is needed.
            continue

        mo: re.Match = FIRST_SPLIT_PATTERN.search(sline)
        if mo is None:
            raise error("bad input line", sline)
        result = int(mo.group("result"))
        rest = mo.group("rest")
        arguments = list(map(int, re.split(r"\s+", rest.strip())))

        if DEBUG1:
            sys.stdout.write(f"line {lind}: {result=} arguments={arguments}\n")

        flag = recurtree(result, 1, arguments)
        if flag:
            cntgood += 1
            sumgood += result

    ########################################################################
    # Main loop
    ########################################################################

    sys.stdout.write(f"Found {cntgood} good equations\n")

    ########################################################################
    # Write out answer
    ########################################################################
    answer =sumgood
    sys.stdout.write(f"\n\nANSWER ---> {answer=}\n")

else:
    pass

########################################################################
# End of day07_2.py
