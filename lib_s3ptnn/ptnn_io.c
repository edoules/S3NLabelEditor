#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

#include "ptnn_weightLayer.h"
#include "ptnn_io.h"

int writeWeight(FILE* file, weightLayer* weight)
{
	fprintf(file, "%d\n", weight -> nnodes);
	fprintf(file, "%d\n", weight -> ninputs);
	int i;
	int j;
	for(i = 0; i < weight -> nnodes; i ++)
		for(j = 0; j < weight -> ninputs; j ++)
			if(fprintf(file, "%lf\n", weight -> weight[i][j]) < 1)
				return -1;
	for(i = 0; i < weight -> nnodes; i ++)
		if(fprintf(file, "%lf\n", weight -> bias[i]) < 1)
			return -1;
	return 0;
}

/////
//#include "../debug/ptnn_diagnose.h"
/////

weightLayer* readWeight(FILE* file)
{
	weightLayer* retObj = calloc(1, sizeof(weightLayer));
	assert(retObj);
	if(fscanf(file, "%d\n", &(retObj -> nnodes)) < 1)
		return NULL;
	if(fscanf(file, "%d\n", &(retObj -> ninputs)) < 1)
		return NULL;
	
	int i;
	retObj -> weight = calloc(retObj -> nnodes, sizeof(double*));
	for(i = 0; i < retObj -> nnodes; i ++)
		retObj -> weight[i] = calloc(retObj -> ninputs, sizeof(double));
	retObj -> bias = calloc(retObj -> nnodes, sizeof(double));
	
	int j;
	for(i = 0; i < retObj -> nnodes; i ++)
		for(j = 0; j < retObj -> ninputs; j ++)
			if(fscanf(file, "%lf\n", &(retObj -> weight[i][j])) < 1)
				return NULL;
	for(i = 0; i < retObj -> nnodes; i ++)
		if(fscanf(file, "%lf\n", &(retObj -> bias[i])) < 1)
			return NULL;
    
	return retObj;
}


///// EDOULES -- THIS IS NEW 20140914 -- OVERREAD A WEIGHT

int overReadWeight(FILE* file, weightLayer* retObj)
{
	assert(retObj);
    
    int check_nnodes = 0;
    int check_ninputs = 0;
    
	if(fscanf(file, "%d\n", &(check_nnodes)) < 1) return -1;
	if(fscanf(file, "%d\n", &(check_ninputs)) < 1) return -1;
    if(retObj -> nnodes != check_nnodes) return -1;
    if(retObj -> ninputs != check_ninputs) return -1;
    
	int i;
    assert(retObj -> weight);
	for(i = 0; i < retObj -> nnodes; i ++)
        assert(retObj -> weight[i]);
	assert(retObj -> bias);
	
	int j;
	for(i = 0; i < retObj -> nnodes; i ++)
		for(j = 0; j < retObj -> ninputs; j ++)
			if(fscanf(file, "%lf\n", &(retObj -> weight[i][j])) < 1)
				return -1;
	for(i = 0; i < retObj -> nnodes; i ++)
		if(fscanf(file, "%lf\n", &(retObj -> bias[i])) < 1)
			return -1;
	
	return 0;
}
