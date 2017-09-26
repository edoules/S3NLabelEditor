def find_at_most(L, v):

    M = lambda(LL) : LL[len(LL)/2]
    goL = lambda(LL): LL[:len(LL)/2]
    goR = lambda(LL): LL[len(LL)/2:]

    # check v against midpoint to know which half to go into.
    L = [_ for _ in L] # upgrade this from a reference to its own object.
    while len(L) > 1:
        m = M(L)
        if v < m:
            L = goL(L)
        elif v > m:
            L = goR(L)
        else: # v == m:
            return v
    return L[0]

# sped up version -- everything inline instead of expanded.
def find_last_index(L, v): 
    S = 0
    E = len(L)
    while E - S > 1:
        M = (S+E)/2
        m = L[M]
        if v < m:
            E = (S+E)/2
        elif v > m:
            S = (S+E)/2
        else: # v == m:
            for n in xrange(M+1, len(L)):
                if L[n] > v:
                    return n-1
            return len(L) -1
    return M

if __name__ == '__main__':
    A = range(0, 20, 2)
    def example(L, v):
        print L, v, find_at_most(L, v), find_last_index(L, v)
        #print
    example(A, 10)
    example(A, 13)
    example(A, 13.5)
    example(A, 14)
    example(A, 14.9)
    example(A, -1)
    example(A, -5)
    example(A, 22)
    B = [3.5*_ for _ in xrange(-2, 10)]
    example(B, -8)
    example(B, 0)
    example(B, 1.5)
    example(B, 3.5)
    example(B, 7.1)
    example(B, 30)
    example(B, 40)
    example(B, 50)
    C = 'abcddddddefghijjjkkkk'
    example(C, 'c')
    example(C, 'd')
    example(C, 'e')
    example(C, 'i')
    example(C, 'j')
    example(C, 'k')
    example(C, 'z')
