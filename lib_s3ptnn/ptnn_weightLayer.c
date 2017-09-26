#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

#include "ptnn_weightLayer.h"
#include "ptnn_utility.h"

// Constructor
weightLayer* newWeight
	(int nnodes, int ninputs, double average, double amplitude, double hole)
{
	weightLayer* retObj = calloc(1, sizeof(weightLayer));
	assert(retObj);
	retObj -> nnodes = nnodes;
	retObj -> ninputs = ninputs;
	retObj -> weight = calloc(nnodes, sizeof(double*));
	assert(retObj -> weight);
	int i;
	for(i = 0; i < nnodes; i ++)
	{
		retObj -> weight[i] = calloc(ninputs, sizeof(double));
		assert(retObj -> weight[i]);
		int j;
		for(j = 0; j < ninputs; j ++)
			retObj -> weight[i][j] = random_double(average, amplitude, hole);
	}
	retObj -> bias = calloc(nnodes, sizeof(double));
	for(i = 0; i < nnodes; i ++)
	{
		retObj -> bias[i] = random_double(average, amplitude, hole);
	}
	assert(retObj -> bias);
	return retObj;
}

weightLayer* newWeightLenny
	(int nnodes, int ninputs, double average, double amplitude, double hole) // MOD_LENNY
{
    return newWeight(2 * nnodes, ninputs, average, amplitude, hole);
}

// Destructor
void delWeight(weightLayer* weight)
{
	if(!weight)
		return;
	if(weight -> weight)
	{
		int i;
		for(i = 0; i < weight -> nnodes; i ++)
			free(weight -> weight[i]);
		free(weight -> weight);
		weight -> weight = NULL;
	}
	if(weight -> bias)
	{
		free(weight -> bias);
		weight -> bias = NULL;
	}
	weight -> nnodes = -1;
	weight -> ninputs = -1;
	free(weight);
	return;
}
