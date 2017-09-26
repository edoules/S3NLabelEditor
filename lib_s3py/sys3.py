"""

Sys3 Development Version

"""

### System Library ###

from sys import stderr
from itertools import chain
import json

### Custom Library ###

from cyptnn import cyWeightLayer, cyNodeLayer, cysrandom, cyFILE
from abiIO import grab_raw_signal, grab_chromatogram, grab_ploc, grab_pbas, grab_pcon
from main_helper import find_edge, insert_gaps, compute_trims, trunc_shortest, count_matches, count_matches_contig
from editStringDict import simple_estr
from vecRead import vecDecode, grabLenny, argmaxtup
from find_at_most import find_last_index

### Variables ###

BUILD = "2015-09-17"
VERSION = "3.50"
COMMENT = "boldsystems.org"
AUTHORS = "Eddie YT Ma, Sujeevan Ratnasingham, Stefan C Kremer"

arg_interlaced = False
scalem = -.8
scaleM = +.8
bwidth = 9
owidth = 5
cwidth = bwidth * 12 +1
ninputs = 499
nhidden = 124
noutput = 60
WEIGHTFILE = "parameters/neural_weights_file.txt"
PFILE = "parameters/prediction_error_file.txt"
acceptThreshold = .01 * .8
cols = 120
QVconvertToN = 20

### Support Functions and Datastructures ###

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

nukeVecFn = lambda row: [scaleM if i else scalem for i in nukeVectorDict[row]]

baseIndex = lambda x: x+1 #make sure we print out base indices as 1-based for bioinformaticians

### Main Functions ###

def analyze(handle, weightfile = WEIGHTFILE, pfile = PFILE):

    outAssoc = {
        'meta':{
            'build':BUILD,
            'version':VERSION,
            'comment':COMMENT,
            'authors':AUTHORS,
            'qv_convert':QVconvertToN,
            'threshold':acceptThreshold,
        },
        'edits':{
            'ibase':[],
            'ploc':[],
            'recall':'',
            'votes':'',
            'lzhao':[],
            'perror':[],
            'accept':'',
        }
    }
    outAssoc['KB'] = None
    outAssoc['ge20'] = None
    outAssoc['sys3'] = None
    
    seqA = grab_pbas(handle)
    qvseqA = grab_pcon(handle)
    seqAtoN = ''.join(['N' if qa < QVconvertToN else sa for sa, qa in zip(seqA, qvseqA)])
    QAscale = [scalem if qq in (None, '-') else (.01*qq*(scaleM-scalem))+scalem for qq in qvseqA]
    plocseqA = grab_ploc(handle)
    ibaseDict = dict((ploc,ibase) for ibase, ploc in enumerate(plocseqA))
    chrom = dict((nuke,grab_chromatogram(handle, nuke)) for nuke in 'GATC')
    
    if not (len(seqA) == len(qvseqA) == len(plocseqA)):
        try:
            errmsg = "ERROR: (%s) ABIF lengths mismatch (PBAS, PCON, PLOC):" % handle.name, len(seqA), len(qvseqA), len(plocseqA)
        except AttributeError:
            errmsg = "ERROR: (%s) ABIF lengths mismatch (PBAS, PCON, PLOC):" % "", len(seqA), len(qvseqA), len(plocseqA)
        print >>stderr, errmsg
        return json.dumps({"error":errmsg})

    SAvec = list(chain(*[nukeVecFn(a) for a in seqA]))
    
    boff = bwidth/2
    indexList = list(xrange(boff, len(seqA) - boff))
    
    Wih = cyWeightLayer(nhidden, ninputs, 0., 0., 0.)
    Wh2 = cyWeightLayer(nhidden, nhidden, 0., 0., 0.)
    Who = cyWeightLayer(noutput, nhidden, 0., 0., 0., Lenny = True)

    Ni = cyNodeLayer(ninputs = ninputs)
    Nh = cyNodeLayer(Ni, Wih)
    N2 = cyNodeLayer(Nh, Wh2)
    No = cyNodeLayer(N2, Who)
    
    #e.g. READING WEIGHTS.
    cyH = None
    try:
        cyH = cyFILE(weightfile, "r")
        Wih.overRead(cyH)
        Wh2.overRead(cyH)
        Who.overRead(cyH)
    except:
        errmsg = "ERROR: WEIGHTS NOT READ."
        print >>stderr, errmsg
        return json.dumps({"error":errmsg})
    finally:
        del cyH

    try:
        #load probability file ...
        predictLenny = [] # that is, keep me as a sorted list to binary search through.
        predictError = {} # but -- keep me as a dictionary to look up error given Lenny.
        with open(pfile) as phandle:
            for line in phandle:
                line = line.strip().split()
                _, pL, pE, _ = line
                pL = float(pL)
                pE = float(pE)
                predictLenny += [pL]
                predictError[pL] = pE # it's ok -- just keep overwriting with the greatest error :)
    except:
        errmsg = "ERROR: ERROR PREDICTION CURVE NOT READ."
        print >>stderr, errmsg
        return json.dumps({"error":errmsg})
    
    five_hits = {}
    
    for i in indexList:
    
        L = i - boff
        R = i + boff +1
        
        chopStart = bwidth/2-(owidth/2   )
        chopEnd   = bwidth/2+(owidth/2 +1)
        
        SA        = seqAtoN[L:R]
        PA        = plocseqA[L:R]
        VA        = SAvec[colsNVD*L:colsNVD*R]
        QA        = QAscale[L:R]
        
        CL = plocseqA[i] - cwidth/2
        CR = plocseqA[i] + cwidth/2 +1
        if CL < 0: continue
        if CR > len(chrom['A']): continue

        ChromData = [chrom[nuke][CL:CR] for nuke in 'ACGT']
        
        m = min(chain(*ChromData))
        M = max(chain(*ChromData))
        ChromData = list(chain(*[[(
            (scaleM-scalem)*(value - m)/(M - m)
        )+scalem for value in channel] for channel in ChromData]))
        
        invec  = VA + QA + ChromData
        
        VAseq = ''.join([nukeVectorDictRev[argmaxtup(j)] for j in [VA[j:j+colsNVD] for j in xrange(0, len(VA), colsNVD)]])
    
        C5 = lambda(x): x[2:-2]
        for sa, pa in zip(C5(SA), C5(PA)):
            if sa =='N':
                if pa not in five_hits: five_hits[pa] = []
                five_hits[pa] += [(invec, C5(PA), sa, C5(SA), VAseq)]
    
    #tsv = []
    rSequence = [_ for _ in seqAtoN]
    uSequence = [_ for _ in seqAtoN]
    mSequence = [_ for _ in seqAtoN]
    cSequence = [_ for _ in seqAtoN]
    for ploc_major in sorted(five_hits):
        
        if len(five_hits[ploc_major]) < 5: continue
        
        acc_hits = {}
        acc_lenny = []
        acc_majority_lenny = {}

        for jvec, (invec, pa, sa, SA, VAseq) in enumerate(five_hits[ploc_major]):
        
            if jvec == 2:
                centre = PS[jcur]
                centre_lenny = grabLenny(lenny, jcur, owidth)
        
            jcur = pa.index(ploc_major)
            
            Ni.setActivations(invec)
            rmse = No.treeTrainLenny(2*noutput*[0.], 0, 0, 0)

            rawout  = No.getActivations()
            predict = rawout[:noutput]
            lenny   = rawout[noutput:]

            acc_lenny += [grabLenny(lenny, jcur, owidth)]

            PS, PE = vecDecode(predict, owidth, scalem, scaleM)
            
            #print jcur, PS, PE, sa, SA, VAseq
            
            if PS[jcur] not in acc_hits: acc_hits[PS[jcur]] = 0
            acc_hits[PS[jcur]] += 1
            
            if PS[jcur] not in acc_majority_lenny: acc_majority_lenny[PS[jcur]] = []
            acc_majority_lenny[PS[jcur]] += [grabLenny(lenny, jcur, owidth)]
            
        unanimous = 'N'
        if len(five_hits[ploc_major]) == 5 and len(acc_hits) == 1:
            unanimous = [sp for sp in acc_hits][0]
        
        majority = 'N'
        hits_acc = {}
        majority_count = 0
        for b in acc_hits:
            c = acc_hits[b]
            if c not in hits_acc: hits_acc[c] = []
            hits_acc[c] += [b]
        most = hits_acc[sorted(hits_acc)[-1]]
        if len(most) == 1:
            majority = most[0]
            majority_count = sorted(hits_acc)[-1]
        
        mu_lenny = float('+inf')
        if unanimous in 'ACGT':
            mu_lenny = sum(acc_lenny)/len(acc_lenny)

        majority_lenny = float('+inf')
        if majority in 'ACGT':
            majority_lenny = sum(acc_majority_lenny[majority])/len(acc_majority_lenny[majority])

        pError = predictError[predictLenny[find_last_index(predictLenny, mu_lenny)]]
        belowThreshold = pError < acceptThreshold
        verbalThreshold = ['N','Y'][belowThreshold]

        if mu_lenny != float('+inf'):
        
            outAssoc['edits']['ibase'] += [baseIndex(ibaseDict[ploc_major])]
            outAssoc['edits']['ploc'] += [ploc_major]
            outAssoc['edits']['recall'] += unanimous #if belowThreshold else 'N'
            outAssoc['edits']['votes'] += '5'
            outAssoc['edits']['lzhao'] += [mu_lenny]
            outAssoc['edits']['perror'] += [pError]
            outAssoc['edits']['accept'] += verbalThreshold
            
            uSequence[ibaseDict[ploc_major]] = unanimous if belowThreshold else 'N'

        elif majority_lenny != float('+inf'):
        
            outAssoc['edits']['ibase'] += [baseIndex(ibaseDict[ploc_major])]
            outAssoc['edits']['ploc'] += [ploc_major]
            outAssoc['edits']['recall'] += majority #'N'
            outAssoc['edits']['votes'] += str(majority_count)
            outAssoc['edits']['lzhao'] += [None]
            outAssoc['edits']['perror'] += [None]
            outAssoc['edits']['accept'] += 'N'
        
        else:
        
            outAssoc['edits']['ibase'] += [baseIndex(ibaseDict[ploc_major])]
            outAssoc['edits']['ploc'] += [ploc_major]
            outAssoc['edits']['recall'] += centre #'N'
            outAssoc['edits']['votes'] += 'C'
            outAssoc['edits']['lzhao'] += [None]
            outAssoc['edits']['perror'] += [None]
            outAssoc['edits']['accept'] += 'N'
    
    uSequence = ''.join(uSequence)
    
    outAssoc['KB'] = seqA
    outAssoc['ge20'] = seqAtoN
    outAssoc['sys3'] = uSequence
    
    return json.dumps(outAssoc, indent=4, sort_keys=1)
