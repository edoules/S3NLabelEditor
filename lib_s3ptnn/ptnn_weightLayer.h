#ifndef PTNN_WEIGHTLAYER_H
#define PTNN_WEIGHTLAYER_H

typedef struct {
	int nnodes;
	int ninputs;
	double** weight;
	double* bias;
} weightLayer;

// Constructor
weightLayer* newWeight
	(int nnodes, int ninputs, double average, double amplitude, double hole);

weightLayer* newWeightLenny
	(int nnodes, int ninputs, double average, double amplitude, double hole);

// Destructor
void delWeight(weightLayer* weight);

#endif
