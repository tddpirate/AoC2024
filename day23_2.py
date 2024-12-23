#!/usr/bin/env python
########################################################################
#
# day23_2.py
# Was written for AoC2024
#
########################################################################
from collections import defaultdict
import re
import sys
from typing import Dict, FrozenSet
from typing import List
from typing import Set

DEBUG1 = True

########################################################################
# Patterns
########################################################################

CONNECTION_PATTERN: re.Pattern = re.compile(
    r"^\s*(?P<from>[a-zA-Z]{2})\s*-\s*(?P<to>[a-zA-Z]{2})\s*$"
)


########################################################################
# Classes for raising exceptions
########################################################################


class error(Exception):
    pass


########################################################################
if __name__ == "__main__":
    ########################################################################
    # Input data parsing
    ########################################################################

    connections: Dict[str, Set[str]] = defaultdict(set)

    for line in sys.stdin:
        sline = line.strip()
        if len(sline) == 0:
            # Ignore empty lines, no special processing is needed.
            continue
        if sline[0] == "#":
            sys.stdout.write(f"COMMENT: {sline}\n")
            continue

        mo: re.Match = CONNECTION_PATTERN.search(sline)
        if not mo:
            raise error("Malformatted input line", line)
        connections[mo.group("from")].add(mo.group("to"))
        connections[mo.group("to")].add(mo.group("from"))

    ########################################################################
    # Main loop
    ########################################################################

    n_cliques: Set[FrozenSet[str]] = set()

    # A computer may be member of more than one clique.
    # We start with 3-cliques.

    for computer1 in connections.keys():
        for computer2 in connections[computer1]:
            connections3: Set = connections[computer1].intersection(
                connections[computer2]
            )
            for computer3 in connections3:
                n_cliques.add(frozenset([computer1, computer2, computer3]))

    n_cliques_count: int = len(n_cliques)
    sys.stdout.write(f"There are total of {n_cliques_count} 3-cliques\n")

    for computer4 in connections.keys():
        new_cliques: Set[FrozenSet[str]] = set()
        clique: FrozenSet
        for clique in n_cliques:
            # Does computer4 form a n+1-clique when trying to join a n-clique?
            if clique.issubset(connections[computer4]):
                clique_set: Set = set(clique)
                clique_set.add(computer4)
                n_plus_1_clique: FrozenSet = frozenset(clique_set)
                new_cliques.add(n_plus_1_clique)
        if DEBUG1:
            sys.stdout.write(f"{computer4} created {len(new_cliques)} new cliques.\n")
        n_cliques = n_cliques.union(new_cliques)

    max_clique_count = max([len(clique) for clique in n_cliques])
    max_cliques = [clique for clique in n_cliques if len(clique) == max_clique_count]
    sys.stdout.write(
        f"Biggest clique has {max_clique_count} members and there are {len(max_cliques)} such cliques.\n"
    )

    if len(max_cliques) > 1:
        sys.stdout.write(
            "*** AMBIGUOUS ANSWER, will work with 1st clique in the list of biggest cliques ***\n"
        )

    sorted_clique: List[str] = sorted(list(max_cliques[0]))

    ########################################################################
    # Write out answer
    ########################################################################
    answer = ",".join(sorted_clique)
    sys.stdout.write(f"\n\nANSWER ---> {answer=}\n")

else:
    pass

########################################################################
# End of day23_2.py
