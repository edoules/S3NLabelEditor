#include "ptnn_nodeLayer.h"
#include "ptnn_algorithms.h"
#include "ptnn_utility.h"
#include "ptnn_train.h"

#ifdef eddebug
#include <stdlib.h>
#include <stdio.h>
#include "../debug/ptnn_diagnose.h"
#endif

double treeTrain(nodeLayer* root, double* target, double eta, double alpha, double lambda)
{
	#ifdef eddebug
	static int ALLOW_ONLY = 0;
	if(ALLOW_ONLY == 1)
		exit(0);
	if(ALLOW_ONLY == 0)
	{
		printf("\n\nALLOW_ONLY[%d]: Before anything...\n\n", ALLOW_ONLY);
		exposeTree(root);
	}
	ALLOW_ONLY ++;
	#endif
	
	treeFeedForward(root);
	
	#ifdef eddebug
	printf("\n\nALLOW_ONLY[%d]: After Feed Forward...\n\n", ALLOW_ONLY);
	exposeTree(root);
	#endif

	treeBackPropagate(root, target);

	#ifdef eddebug
	printf("\n\nALLOW_ONLY[%d]: After Back Propagate...\n\n", ALLOW_ONLY);
	exposeTree(root);
	#endif

	treeWeightUpdate(root, eta, alpha, lambda);

	#ifdef eddebug
	printf("\n\nALLOW_ONLY[%d]: After Weight Update...\n\n", ALLOW_ONLY);
	exposeTree(root);
	#endif

	return squared_error(root -> nnodes, root -> activation, target);
}

double treeTrainLenny(nodeLayer* root, double* target, double eta, double alpha, double lambda)
{
	treeFeedForward(root);
	treeBackPropagateLenny(root, target);
	treeWeightUpdate(root, eta, alpha, lambda);
	return squared_error(root -> nnodes/2, root -> activation, target);
}
