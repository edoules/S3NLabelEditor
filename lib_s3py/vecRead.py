"""
"""

import os

def vecRead(path6):
    if os.path.isfile(path6):
        with open(path6) as h:
            for line in h:
                inVec, outVec, metaVec = line.strip().split(':::')
                inVec = [float(i) for i in inVec.split(';')]
                outVec = [float(i) for i in outVec.split(';')]
                metaVec = metaVec.split(';')
                [
                    SA,     #0      string      SA, # -- gap-removed Sequence A.
                    ST,     #1      string      SB, # -- Sequence ground truth (basecalls).
                    ET,     #2      string      ES, # -- Sequence ground truth (edits).
                    QAgap,  #3      list(int?)  self.QA[L:R], # original Sequence A QV (gaps in).
                    QT,     #4      list(int?)  self.QB[L:R], # Sequence ground truth QV.
                    SAgap,  #5      string      self.SA[L:R], # original Sequence A (gaps in).
                    SB,     #6      string      self.SBorig[L:R], # original Sequence B.
                    QB,     #7      list(int?)  self.QBorig[L:R], # original Sequence B QV.
                    QA,     #8      list(int?)  QAmetasuck, # gap-removed Sequence A QV.
                    PA,     #9      list(int?)  self.PA[i], # Sequence A PLOC.
                    PB,     #10     list(int?)  self.PB[i], # Sequence B PLOC.
                    SH,     #11     string      # human sequence.
                ] = metaVec
                S = lambda(x): [None if e == '-' else int(e) for e in x.split(',')]
                L = lambda(x): [S(e) for e in x]
                [
                    QAgap, QT, QB, QA, PA, PB
                ] = L([
                    QAgap, QT, QB, QA, PA, PB
                ])
                metaVec = [SA, ST, ET, QAgap, QT, SAgap, SB, QB, QA, PA, PB, SH,]
                yield inVec, outVec, metaVec
    raise StopIteration

nukeVectorDict = {
#          A.,C.,G.,T.,N.,-.,
    'A' : (1.,0.,0.,0.,0.,0.,),
    'C' : (0.,1.,0.,0.,0.,0.,),
    'G' : (0.,0.,1.,0.,0.,0.,),
    'T' : (0.,0.,0.,1.,0.,0.,),
    'W' : (1.,0.,0.,1.,0.,0.,), #AT -- could represent [.5*w for w in W], BUT -- really a superposition
    'S' : (0.,1.,1.,0.,0.,0.,), #CG
    'M' : (1.,1.,0.,0.,0.,0.,), #AC
    'K' : (0.,0.,1.,1.,0.,0.,), #GT
    'R' : (1.,0.,1.,0.,0.,0.,), #AG
    'Y' : (0.,1.,0.,1.,0.,0.,), #CT
    'N' : (0.,0.,0.,0.,1.,0.,), #could represent [.25*n for n in N], BUT -- really "no commitment"
    '-' : (0.,0.,0.,0.,0.,1.,),
}

colsNVD = len(nukeVectorDict['A'])

#nukeVectorDictRev = {nukeVectorDict[key]:key for key in nukeVectorDict}
nukeVectorDictRev = dict([(nukeVectorDict[key],key) for key in nukeVectorDict])

editVectorDict = {
#          M.,L.,G.,S.,I.,D.
    'M' : (1.,0.,0.,0.,0.,0.,),
    'L' : (0.,1.,0.,0.,0.,0.,),
    'G' : (0.,0.,1.,0.,0.,0.,),
    'S' : (0.,0.,0.,1.,0.,0.,),
    'I' : (0.,0.,0.,0.,1.,0.,),
    'D' : (0.,0.,0.,0.,0.,1.,),
    '-' : (0.,0.,0.,0.,0.,0.,),
}

#editVectorDictRev = {editVectorDict[key]:key for key in editVectorDict}
editVectorDictRev = dict([(editVectorDict[key],key) for key in editVectorDict])

colsEVD = len(editVectorDict['M'])

def argmaxtup(xlist):
    for i, x in enumerate(xlist):
        if i == 0 or x > maxvalue:
            maxindex = i
            maxvalue = x
    return tuple([1. if i == maxindex else 0. for i in xrange(len(xlist))])

def vecDecode(ovec, owidth, scalem, scaleM):

    # if we know the base-width, then we know what to expect here.
    # ovec is made out of SBvec + QB + ESvec ...
    # SBvec is 6* basewidth, binary encoding.
    # ESvec is 6* basewidth, one-hot encoding.
    
    ESstart = colsNVD * owidth
    
    SBvec   = ovec[       :ESstart]
    SBvec   = [SBvec[j:j+colsNVD] for j in xrange(0, len(SBvec), colsNVD)]
    SB      = ''.join([nukeVectorDictRev[argmaxtup(j)] for j in SBvec])
    
    ESvec   = ovec[ESstart:       ]
    ESvec   = [[
        0. if k < .5*(scalem + scaleM) else 1. for k in ESvec[j:j+colsEVD
    ]] for j in xrange(0, len(ESvec), colsEVD)]
    ES      = ''.join([editVectorDictRev[argmaxtup(j)] for j in ESvec])
    
    return SB, ES

def grabLenny(Lvec, Lindex, owidth):
    
    ESstart = colsNVD * owidth
    
    SBvec   = Lvec[       :ESstart]
    
    LbyNode = [SBvec[c:c+colsNVD] for c in xrange(owidth)]
    
    #for iL, L in enumerate(LbyNode): print iL, L
    
    LSelect = LbyNode[Lindex]
    
    #print LSelect
    
    X = lambda(x): .5*(x+1)
    
    return X(1.*sum(LSelect)/len(LSelect))
    