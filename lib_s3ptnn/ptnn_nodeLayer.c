#include <stdlib.h>
#include <stdarg.h>
#include <assert.h>
#include "ptnn_nodeLayer.h"
#include "ptnn_weightLayer.h"

#ifdef eddebug
#include <stdio.h>
#include "../debug/ptnn_diagnose.h"
#endif

//	Constructor - nodeLayer as nodeLayer
nodeLayer* newNode(int nchildren, ...)
{
	assert(nchildren > 0);

	nodeLayer* retObj = calloc(1, sizeof(nodeLayer));
	assert(retObj);
	
	retObj -> nchildren = nchildren;
	retObj -> child = calloc(nchildren, sizeof(nodeLayer*));
	assert(retObj -> child);
	retObj -> weight = calloc(nchildren, sizeof(weightLayer*));
	assert(retObj -> weight);
	retObj -> weight_delta = calloc(nchildren, sizeof(weightLayer*));
	assert(retObj -> weight_delta);
	
	{
	va_list argv;
	va_start(argv, nchildren);
	int i;
	for(i = 0; i < nchildren; i ++)
	{
		retObj -> child[i] = va_arg(argv, nodeLayer*);
		retObj -> child[i] -> parent = retObj;
		retObj -> weight[i] = va_arg(argv, weightLayer*);
		retObj -> weight_delta[i] =
			newWeight(
				retObj -> weight[i] -> nnodes,
				retObj -> weight[i] -> ninputs,
				0.0, 0.0, 0.0
			);
		
		#ifdef eddebug
		printf("\nJust allocated weight delta...\n\n");
		exposeWeight(retObj -> weight_delta[i]);
		#endif
		
		retObj -> ninputs += retObj -> weight[i] -> ninputs;
		retObj -> child[i] -> isibling = i;
	}
	retObj -> nnodes = retObj -> weight[0] -> nnodes;
	va_end(argv);
	}
	
	retObj -> activation = calloc(retObj -> nnodes, sizeof(double));
	assert(retObj -> activation);
	retObj -> delta = calloc(retObj -> nnodes, sizeof(double));
	assert(retObj -> delta);
	
	return retObj;
}

//	Constructor - nodeLayer as inputLayer
nodeLayer* newInput(int nnodes)
{
	nodeLayer* retObj = calloc(1, sizeof(nodeLayer));
	assert(retObj);
	//retObj -> weight;
	//retObj -> weight_delta;
	retObj -> activation = calloc(nnodes, sizeof(double));
	assert(retObj -> activation);
	//retObj -> activation;
	//retObj -> delta;
	//retObj -> child;
	//retObj -> parent;
	retObj -> nnodes = nnodes;
	//retObj -> ninputs
	//retObj -> nchildren;
	//retObj -> isibling;
	return retObj;
}

//	Destructor
void delNode(nodeLayer* node)
{
	if(!node)
		return;
	//do not free the weightLayers, but free the array.
	if(node -> weight)
	{
		free(node -> weight);
		node -> weight = NULL;
	}
	//DO FREE the weight_delta since it belongs to this layer privately.
	if(node -> weight_delta)
	{
		int i;
		for(i = 0; i < node -> nchildren; i ++)
			delWeight(node -> weight_delta[i]);
		free(node -> weight_delta);
	}
	if(node -> activation)
	{
		free(node -> activation);
		node -> activation = NULL;
	}
	if(node -> delta)
	{
		free(node -> delta);
		node -> delta = NULL;
	}
	//do not free the children, but free the array.
	if(node -> child)
	{
		free(node -> child);
		node -> child = NULL;
	}
	//do not free the parent.
	if(node -> parent)
		node -> parent = NULL;
	node -> nnodes = -1;
	node -> ninputs = -1;
	node -> nchildren = -1;
	node -> isibling = -1;
	free(node);
	return;
}

//	Mass Destructor
void delTree(nodeLayer* root)
{
	if(!root)
		return;
	{
	int i;
	for(i = 0; i < root -> nchildren; i ++)
		delTree(root -> child[i]);
	}
	delNode(root);
	return;
}
