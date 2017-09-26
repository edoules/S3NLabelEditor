#ifndef PTNN_NODELAYER_H
#define PTNN_NODELAYER_H

#include "ptnn_weightLayer.h"

typedef struct nodeLayer {
	weightLayer** weight; // Array weightLayer links this with its children
	weightLayer** weight_delta;
	double* activation;
	double* delta;
	struct nodeLayer** child; // An array of children
	struct nodeLayer* parent;
	int nnodes;
	int ninputs;
	int nchildren;
	int isibling;
} nodeLayer;

//	Constructor - nodeLayer as nodeLayer
nodeLayer* newNode(int nchildren, ...);

//	Constructor - nodeLayer as inputLayer
nodeLayer* newInput(int nnodes);

//	Destructor
void delNode(nodeLayer* node);

//	Mass Destructor
void delTree(nodeLayer* root);

#endif
