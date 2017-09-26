#ifndef PTNN_TRAIN_H
#define PTNN_TRAIN_H

#include "ptnn_nodeLayer.h"

/*
	returns squared error for this epoch.
*/
double treeTrain(nodeLayer* root, double* target, double eta, double alpha, double lambda);

/*
    Lenny nodes in this output layer: the left half is actual outputs, the right half are Lennies.
*/
double treeTrainLenny(nodeLayer* root, double* target, double eta, double alpha, double lambda);

#endif
