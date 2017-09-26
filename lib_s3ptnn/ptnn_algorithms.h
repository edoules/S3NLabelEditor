#ifndef PTNN_ALGORITHMS_H
#define PTNN_ALGORITHMS_H

#include "ptnn_nodeLayer.h"

void treeFeedForward(nodeLayer* root);
void treeBackPropagate(nodeLayer* root, double* target);
void treeBackPropagateLenny(nodeLayer* root, double* target); //MOD_LENNY
void treeWeightUpdate(nodeLayer* root, double eta, double alpha, double lambda); //MOD_R2

/////NEW for tparseonce training mode!
void treeZero(nodeLayer* root);

#endif
