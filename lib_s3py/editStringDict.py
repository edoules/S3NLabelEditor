"""

Edit String Dictionaries
Python

I contain simple mapping functions that convert pairs of DNA symbols into edit string symbols.

Read the substdef table as a row-major table where the first symbol is the row name, and the second
symbol is the column name.

=== Edit string symbols are defined as follows ===

+------- My Simplified Symbols
|
|   +--- My Standard Symbols
|   |

M - * -- match ANY token EXCEPT '-' to itself -- /ACGTWSMKRYBDHVN/
- - - -- match '-' to itself -- /-/

S - s -- A -> T -- transition (purine -> purine) or (pyrimidine -> pyrimidine), where x != x
S - v -- A -> C -- transversion (purine -> pyrimidine) or (pyrimidine -> purine)

S - 1 -- C -> W -- subs from 1-base to 2-base -- substitute because C not in W
L - 2 -- A -> W -- loss from 1-base to 2-base -- degenerate because A in {W = {A, T}}
L - 3 -- W -> N -- loss from 2-base to 4-base -- degenerate because W in {N = {A, C, G, T}}
L - 4 -- A -> N -- loss from 1-base to 4-base -- degenerate because A in N

G - 5 -- N -> A -- gain from 4-base to 1-base -- resolution because A in N
G - 6 -- N -> W -- gain from 4-base to 2-base -- resolution because W in N
G - 7 -- W -> A -- gain from 2-base to 1-base -- resolution because A in W
S - 8 -- W -> C -- subs from 2-base to 1-base -- substitute because C not in W

S - 0 -- W -> S -- partial subs from 2-base to 2-base -- substitute where 0 = (W intersect S)
S - a -- W -> M -- partial subs from 2-base to 2-base -- substitute where A = (W intersect M)
S - c -- S -> M -- partial subs from 2-base to 2-base -- substitute where C = (S intersect M)
S - g -- S -> K -- partial subs from 2-base to 2-base -- substitute where G = (S intersect K)
S - t -- W -> K -- partial subs from 2-base to 2-base -- substitute where T = (W intersect K)

I - i -- insert from '-' to ANY EXCEPT '-'
D - d -- delete from ANY EXCEPT '-' to '-'

"""

### THIS TABLE IS ROW-MAJOR -- it is currently correct, but that means there's some code in my
### repository that is exactly backward :/

substdef = """
.ACGTWSMKRYBDHVN-
AAvvs212121!!!!4d
CvCsv122112!!!!4d
GvsGv121221!!!!4d
TsvvT211212!!!!4d
W7887W0atat!!!!3d
S87780Scggc!!!!3d
M7788acM0ac!!!!3d
K8877tg0Kgt!!!!3d
R7878agagR0!!!!3d
Y8787tcct0Y!!!!3d
B!!!!!!!!!!B!!!!d
D!!!!!!!!!!!D!!!d
H!!!!!!!!!!!!H!!d
V!!!!!!!!!!!!!V!d
N5555666666!!!!Nd
-iiiiiiiiiiiiiii-
"""

rowheader = []
substdict = {}

for iline, line in enumerate(substdef.split()):
    if iline == 0:
        colhead = line
        for r in colhead:
            substdict[r] = {}
            rowheader += [r]
        continue
    for ic, field in enumerate(line):
        if ic == 0:
            c = field
            continue
        substdict[c][rowheader[ic]] = field # This line was changed: indexing now RowMajor

simplify_substdict = {
    "A" : "M",
    "C" : "M",
    "G" : "M",
    "T" : "M",
    "W" : "M",
    "S" : "M",
    "M" : "M",
    "K" : "M",
    "R" : "M",
    "Y" : "M",
    "B" : "M",
    "D" : "M",
    "H" : "M",
    "V" : "M",
    "N" : "M",
    "-" : "-",
    "s" : "S",
    "v" : "S",
    "1" : "S",
    "2" : "L",
    "3" : "L",
    "4" : "L",
    "5" : "G",
    "6" : "G",
    "7" : "G",
    "8" : "S",
    "0" : "S",
    "a" : "S",
    "c" : "S",
    "g" : "S",
    "t" : "S",
    "i" : "I",
    "d" : "D",
}

def estr(seqA, seqB):
    return ''.join([substdict[a][b] for a, b in zip(seqA, seqB)])

def simple_estr(seqA, seqB):
    return ''.join([simplify_substdict[substdict[a][b]] for a, b in zip(seqA, seqB)])
