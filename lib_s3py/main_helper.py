"""

I contain all the helper functions that used to clutter main.py

"""

from sys import stderr
from editStringDict import simple_estr
import re

# (2) Trim 20-25-6.
# delete any tail region params:
#   - is size 25.
#   - contains 6 basecalls of qv < 20.            
def find_edge(qvseq):
    WINDOW_SIZE = 20
    MINIMUM_QV = 20
    MAXIMUM_LOW_CALLS = 6
    edge = 0
    for iqv, _ in enumerate(qvseq):
        count_under_20 = sum([1 for qqv in qvseq[iqv:iqv+WINDOW_SIZE] if qqv < MINIMUM_QV])
        #print count_under_20
        if count_under_20 >= MAXIMUM_LOW_CALLS:
            edge = iqv
        else:
            break
    return edge
                
# Apply alignments to QVs.
def insert_gaps(q, a):#, debug = False):
    #if debug: print >>stderr, 'main_helper.py', q
    #if debug: print >>stderr, 'main_helper.py', a
    #if debug: print >>stderr, 'main_helper.py', len(q), len(a), len([aa for aa in a if aa != '-'])
    retlist = []
    iq = 0
    for i, aa in enumerate(a):
        #if debug: print >>stderr, i, iq, aa, q[iq] if iq < len(q) else '!'
        if aa in '-':
            retlist += [None]
        else:
            retlist += [q[iq]]
            iq += 1
    return retlist

# remove terminal gaps!
# remove terminal Ns!
def compute_trims(a):
    import re
    head = re.search('^[-N]+', a)
    tail = re.search('[-N]+$', a)
    if head == None:
        head = 0
    else:
        head = head.end()
    if tail == None:
        tail = len(a)
    else:
        tail = tail.start()
    return head, tail

def compute_trims_only(a):
    import re
    head = re.search('^[-]+', a)
    tail = re.search('[-]+$', a)
    if head == None:
        head = 0
    else:
        head = head.end()
    if tail == None:
        tail = len(a)
    else:
        tail = tail.start()
    return head, tail

def count_matches(a, b):
    return sum([1 for aa, bb in zip(a,b) if aa == bb])

def count_matches_contig_estr(e):
    #print >>stderr, ESTR
    ALL = re.findall('[M]+', e)
    #print >>stderr, ALL
    if len(ALL) == 0: return 0
    return max([len(R) for R in ALL])
    

def count_matches_contig(a, b):
    ESTR = simple_estr(a, b)
    return count_matches_contig_estr(ESTR)

def trunc_shortest(*args):
    m = min([len(a) for a in args])
    return tuple([a[:m] for a in args])
