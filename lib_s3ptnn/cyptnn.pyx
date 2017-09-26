cimport cython
from libc.stdlib cimport malloc, free
import time

#####
import sys
#####

cdef extern from "stdlib.h":
    void srandom(unsigned seed)

cdef extern from "stdio.h":
    ctypedef struct FILE:
        pass
    FILE *fopen(char* path, char* mode) #FIXME -- should be const char* X2, not char*. :-(
    int fclose(FILE *fp)

def cysrandom(seed = None):
    if seed == None:
        srandom(time.time())
    else:
        srandom(seed)

cdef extern from "ptnn_weightLayer.h":
    ctypedef struct weightLayer:
        pass
    weightLayer* newWeight(int nnodes, int ninputs, double average, double amplitude, double hole)
    weightLayer* newWeightLenny(int nnodes, int ninputs, double average, double amplitude, double hole)
    void delWeight(weightLayer* weight)

cdef extern from "ptnn_nodeLayer.h":
    ctypedef struct nodeLayer:
        int nnodes
        double* activation
    nodeLayer* newInput(int nnodes)
    void delNode(nodeLayer* root)

cdef extern from "ptnn_newNode1.h":
    nodeLayer* newNode1(nodeLayer* n, weightLayer* w)

cdef extern from "ptnn_train.h":
    double treeTrain(nodeLayer* root, double* target, double eta, double alpha, double lambda_)
    double treeTrainLenny(nodeLayer* root, double* target, double eta, double alpha, double lambda_)

cdef extern from "ptnn_io.h":
    int writeWeight(FILE* file, weightLayer* weight)
    weightLayer* readWeight(FILE* file)
    int overReadWeight(FILE* file, weightLayer* weight)

cdef extern from "ptnn_algorithms.h":
    void treeFeedForward(nodeLayer* root)

cdef class cyFILE:
    cdef FILE* _F_
    def __cinit__(self, pypath, pymode):
        pybytepath = pypath.encode('ascii')
        pybytemode = pymode.encode('ascii')
        cdef char* cpath = pybytepath
        cdef char* cmode = pybytemode
        self._F_ = fopen(cpath, cmode)
        if self._F_ is NULL:
            raise Exception()
    def __dealloc__(self):
        if self._F_ is not NULL:
            fclose(self._F_)

cdef class cyWeightLayer:
    cdef weightLayer* _w_
    def __cinit__(self, int nnodes, int ninputs, double average, double amplitude, double hole, Lenny = False):
        if not Lenny:
            self._w_ = newWeight(nnodes, ninputs, average, amplitude, hole)
        else:
            self._w_ = newWeightLenny(nnodes, ninputs, average, amplitude, hole)
        if self._w_ is NULL:
            raise MemoryError()
    def __dealloc__(self):
        if self._w_ is not NULL:
            delWeight(self._w_)
    def read(self, cyFILE cyfile):
        if self._w_ is not NULL:
            delWeight(self._w_)
        self._w_ = readWeight(cyfile._F_)
        if self._w_ is NULL:
            raise Exception()
    def write(self, cyFILE cyfile):
        writeWeight(cyfile._F_, self._w_)
    def overRead(self, cyFILE cyfile):
        cdef int retVal = overReadWeight(cyfile._F_, self._w_)
        if retVal == -1: raise ValueError("Couldn't overread file -- IO or bad matrix dimensions.")

cdef class cyNodeLayer:
    cdef nodeLayer* _n_
    def __cinit__(self, cyNodeLayer n = None, cyWeightLayer w = None, int ninputs = 0):
        if ninputs > 0:
            self._n_ = newInput(ninputs)
        else:
            self._n_ = newNode1(n._n_, w._w_)
        if self._n_ is NULL:
            raise MemoryError()
    def __dealloc__(self):
        if self._n_ is not NULL:
            delNode(self._n_)
    def setActivations(self, doubleList):
        cdef int i
        for i in xrange(self._n_.nnodes):
            self._n_.activation[i] = doubleList[i]
    def getActivations(self):
        return [self._n_.activation[i] for i in xrange(self._n_.nnodes)]
    def treeTrain(self, pytarget, double eta, double alpha, double lambda_):
        cdef double* ctarget = <double *>malloc(self._n_.nnodes * cython.sizeof(double))
        if ctarget is NULL: raise MemoryError()
        cdef int i
        for i in xrange(self._n_.nnodes): ctarget[i] = pytarget[i]
        cdef double sse = treeTrain(self._n_, ctarget, eta, alpha, lambda_)
        free(ctarget)
        return sse
    def treeTrainLenny(self, pytarget, double eta, double alpha, lambda_):
        cdef double* ctarget = <double *>malloc(self._n_.nnodes * cython.sizeof(double))
        if ctarget is NULL: raise MemoryError()
        cdef int i
        for i in xrange(self._n_.nnodes /2): ctarget[i] = pytarget[i]
        cdef double sse = treeTrainLenny(self._n_, ctarget, eta, alpha, lambda_)
        free(ctarget)
        return sse
    def treeFeedForward(self):
        treeFeedForward(self._n_)
