// ADDING REGULARIZATION ...

//#include "../prefabs/ed_macros.h"

#define _PTNN_TANH_TANH_ // use linear for output, use tanh() for internal.

#include <stdlib.h>
#include <math.h>

#include "ptnn_algorithms.h"
//#include "../testmacro/testmacro.h"

//	Inner Function Prototypes
#ifndef _PTNN_TANH_TANH_
static void nodeFeedForward(nodeLayer* node);
#else
static void nodeFeedForwardTanh(nodeLayer* node); // NEW: Internal layers are now TANH.
#endif

static void treeBackPropagateInternal(nodeLayer* node);

#ifndef _PTNN_TANH_TANH_
static void nodeBackPropagate(nodeLayer* node, double* target);
static void treeBackPropagateLenny(nodeLayer* root, double* target); // MOD_LENNY
#else
static void nodeBackPropagateTanh(nodeLayer* node, double* target); // NEW: Deltas = difference.
static void nodeBackPropagateTanhLenny(nodeLayer* node, double* target); // MOD_LENNY
#endif

#ifndef _PTNN_TANH_TANH_
static void nodeBackPropagateInternal(nodeLayer* node);
#else
static void nodeBackPropagateInternalTanh(nodeLayer* node); // NEW: Derivative of TANH instead.
#endif

static void nodeWeightUpdate(nodeLayer* node, double eta, double alpha, double lambda); // L2 Regularization

/////NEW!
static void nodeZero(nodeLayer* node);

void treeFeedForward(nodeLayer* root)
{
	//__edptrmsg(root);
	if(!root)
		return;
	{
	int i;
	for(i = 0; i < root -> nchildren; i ++)
		treeFeedForward(root -> child[i]);
	}
    #ifdef _PTNN_TANH_TANH_
    nodeFeedForwardTanh(root);
    #else
	nodeFeedForward(root);
    #endif
	
	//__edstrmsg("return(void).");
	return;
}

void treeBackPropagate(nodeLayer* root, double* target)
{
	//__ed2ptrmsg(root, target);
	if(!root)
		return;
    #ifndef _PTNN_TANH_TANH_
	nodeBackPropagate(root, target);
    #else
    nodeBackPropagateTanh(root, target);
    #endif
	{
	int i;
	for(i = 0; i < root -> nchildren; i ++)
		treeBackPropagateInternal(root -> child[i]);
	}
	
	//__edstrmsg("return(void).");
	return;
}

// UPDATE RANGE 20141209 (OK)
void treeBackPropagateLenny(nodeLayer* root, double* target) // MOD_LENNY
{
	//__ed2ptrmsg(root, target);
	if(!root)
		return;
    #ifndef _PTNN_TANH_TANH_
	nodeBackPropagateLenny(root, target);
    #else
    nodeBackPropagateTanhLenny(root, target);
    #endif
	{
	int i;
	for(i = 0; i < root -> nchildren; i ++)
		treeBackPropagateInternal(root -> child[i]);
	}
	
	//__edstrmsg("return(void).");
	return;
}

void treeWeightUpdate(nodeLayer* root, double eta, double alpha, double lambda)
{
	//__edptrmsg(root);
	//__ed2dblmsg(eta, alpha);
	if(!root)
		return;
	{
	int i;
	for(i = 0; i < root -> nchildren; i ++)
		treeWeightUpdate(root -> child[i], eta, alpha, lambda);
	}
	nodeWeightUpdate(root, eta, alpha, lambda);
	
	//__edstrmsg("return(void).");
	return;
}

//	Inner Functions
#ifndef _PTNN_TANH_TANH_
static void nodeFeedForward(nodeLayer* node)
{
	//__edptrmsg(node);
	
	if(node -> nchildren < 1)
		return;
	
	/*
		loop2i - A toplevel loop iterating over the children of node.
		loop2j - A nested loop iterating over the nodes of node.
		
		Iterating over the nodes of node is the same as iterating over nodes of
		weight and node's activations (same for every child).
		
		loop2k - A nested loop iterating over the inputs of weight[loop2i].
		
		Iterating over the inputs of weight is the same as iterating over node's
		childrens' activations (different for every child).
	*/
	int loop2i = 0;
	int loop2j = 0;
	int loop2k = 0;
	
	for(loop2j = 0; loop2j < node -> nnodes; loop2j ++)
		node -> activation[loop2j] = 0.0;
	
	for(loop2i = 0; loop2i < node -> nchildren; loop2i++)
	{
		for(loop2j = 0; loop2j < node -> nnodes; loop2j++)
		{
			node -> activation[loop2j] += node -> weight[loop2i] -> bias[loop2j];
			for(loop2k = 0; loop2k < node -> weight[loop2i] -> ninputs; loop2k++)
				node -> activation[loop2j] +=
					node -> weight[loop2i] -> weight[loop2j][loop2k] *
						node -> child[loop2i] -> activation[loop2k];
		}
	}
	
	for(loop2j = 0; loop2j < node -> nnodes; loop2j ++)
		node -> activation[loop2j] =
			1.0 / (1.0 + exp( -node -> activation[loop2j]));
			
	//__edstrmsg("return(void).");
	return;
}
#else
static void nodeFeedForwardTanh(nodeLayer* node)
{
	//__edptrmsg(node);
	
	if(node -> nchildren < 1) return;
    
	int loop2i = 0;
	int loop2j = 0;
	int loop2k = 0;
	
	for(loop2j = 0; loop2j < node -> nnodes; loop2j ++)
		node -> activation[loop2j] = 0.0;
	
	for(loop2i = 0; loop2i < node -> nchildren; loop2i++)
	{
		for(loop2j = 0; loop2j < node -> nnodes; loop2j++)
		{
			node -> activation[loop2j] += node -> weight[loop2i] -> bias[loop2j];
			for(loop2k = 0; loop2k < node -> weight[loop2i] -> ninputs; loop2k++)
				node -> activation[loop2j] +=
					node -> weight[loop2i] -> weight[loop2j][loop2k] *
						node -> child[loop2i] -> activation[loop2k];
		}
	}
	
	for(loop2j = 0; loop2j < node -> nnodes; loop2j ++)
		node -> activation[loop2j] = tanh(node -> activation[loop2j]);
			
	//__edstrmsg("return(void).");
	return;
}
#endif

static void treeBackPropagateInternal(nodeLayer* node)
{
	//__edptrmsg(node);
	if(!node)
		return;
    #ifndef _PTNN_TANH_TANH_
	nodeBackPropagateInternal(node);
    #else
	nodeBackPropagateInternalTanh(node);
    #endif
	{
	int i;
	for(i = 0; i < node -> nchildren; i ++)
		treeBackPropagateInternal(node -> child[i]);
	}
	//__edstrmsg("return(void).");
	return;
}

#ifndef _PTNN_TANH_TANH_
static void nodeBackPropagate(nodeLayer* node, double* target)
{
	//__ed2ptrmsg(node, target);
	int i;
	for(i = 0; i < node -> nnodes; i ++)
	{
		node -> delta[i] =
			(target[i] - node -> activation[i]) *                // dE / dy.
            node -> activation[i] * (1 - node -> activation[i]); // dy / d(net).
	}
	//__edstrmsg("return(void).");
	return;
}

// UPDATE RANGE 20141209 (SKIP)
static void nodeBackPropagateLenny(nodeLayer* node, double* target) // MOD_LENNY
{
	//__ed2ptrmsg(node, target);
	int i;
	for(i = 0; i < node -> nnodes /2; i ++)
	{
		node -> delta[i] =
			(target[i] - node -> activation[i]) *                // dE / dy.
            node -> activation[i] * (1 - node -> activation[i]); // dy / d(net).
        int lenny = i + node -> nnodes /2;
        node -> delta[lenny] =
            (
                (target[i] - node -> activation[i]) * (target[i] - node -> activation[i])
                - node -> activation[lenny]
            ) *
            node -> activation[lenny] * (1 - node -> activation[lenny]); // dy / d(net).
	}
	//__edstrmsg("return(void).");
	return;
}
#else
static void nodeBackPropagateTanh(nodeLayer* node, double* target)
{
	//__ed2ptrmsg(node, target);
	int i;
	for(i = 0; i < node -> nnodes; i ++)
		node -> delta[i] =
            (target[i] - node -> activation[i]) *                  // dE / dy.
            (1.0 - node -> activation[i] * node -> activation[i]); // dy / d(net).
	//__edstrmsg("return(void).");
	return;
}

// UPDATE RANGE 20141209 (TODO)
static void nodeBackPropagateTanhLenny(nodeLayer* node, double* target) // MOD_LENNY
{
	//__ed2ptrmsg(node, target);
	int i;
	for(i = 0; i < node -> nnodes /2; i ++) {
		node -> delta[i] =
            (target[i] - node -> activation[i]) *                  // dE / dy.
            (1.0 - node -> activation[i] * node -> activation[i]); // dy / d(net).
        int lenny = i + node -> nnodes /2;
        node -> delta[lenny] =
            (
                (2.*(
                    (target[i] - node -> activation[i]) *
                    (target[i] - node -> activation[i])
                )-1.)
                - node -> activation[lenny]
            ) *
            (1.0 - node -> activation[lenny] * node -> activation[lenny]); // dy / d(net).
    }
	//__edstrmsg("return(void).");
	return;
}
#endif

#ifndef _PTNN_TANH_TANH_
static void nodeBackPropagateInternal(nodeLayer* node)
{
	//__edptrmsg(node);
	
	int i = 0;
	for(i = 0; i < node -> nnodes; i ++)
	{
		double netBlame = 0.0;
		int j = 0;
		for(j = 0; j < node -> parent -> weight[node -> isibling] -> nnodes; j ++)
		{
			netBlame +=
				node -> parent -> delta[j] *
					node -> parent -> weight[node -> isibling] -> weight[j][i];
		}
		if(node -> nchildren)
			node -> delta[i] =
				node -> activation[i] * (1.0 - node -> activation[i]) * // dy / d(net).
                netBlame;                                               // dE / dy.
	}
	
	//__edstrmsg("return(void).");
	return;
}
#else
static void nodeBackPropagateInternalTanh(nodeLayer* node)
{
	//__edptrmsg(node);
	
	int i = 0;
	for(i = 0; i < node -> nnodes; i ++)
	{
		double netBlame = 0.0;
		int j = 0;
		for(j = 0; j < node -> parent -> weight[node -> isibling] -> nnodes; j ++)
		{
			netBlame +=
				node -> parent -> delta[j] *
					node -> parent -> weight[node -> isibling] -> weight[j][i];
		}
		if(node -> nchildren)
			node -> delta[i] =
                (1.0 - node -> activation[i] * node -> activation[i]) * // dy / d(net).
                netBlame;                                               // dE / dy.
	}
	
	//__edstrmsg("return(void).");
	return;
}
#endif

static void nodeWeightUpdate(nodeLayer* node, double eta, double alpha, double lambda)
{
	//__edptrmsg(node);
	//__ed2dblmsg(eta, alpha);
	
	if(node -> nchildren < 1)
		return;
	
	/*
		loop2i - A toplevel loop iterating over the children of node.
		loop2j - A nested loop iterating over the nodes of node.
		
		Iterating over the nodes of node is the same as iterating over nodes of
		weight and node's activations (same for every child).
		
		loop2k - A nested loop iterating over the inputs of weight[loop2i].
		
		Iterating over the inputs of weight is the same as iterating over node's
		childrens' activations (different for every child).
	*/
	int loop2i = 0;
	int loop2j = 0;
	int loop2k = 0;
	
	double eta_delta;
    double eta_lambda = eta * lambda;
	
	for(loop2i = 0; loop2i < node -> nchildren; loop2i++)
	{
		for(loop2j = 0; loop2j < node -> nnodes; loop2j++)
		{
			eta_delta = eta * node -> delta[loop2j];
			for(loop2k = 0; loop2k < node -> weight[loop2i] -> ninputs; loop2k++)
			{
				node -> weight_delta[loop2i] -> weight[loop2j][loop2k] =
					eta_delta * node -> child[loop2i] -> activation[loop2k] +
                        alpha * node -> weight_delta[loop2i] -> weight[loop2j][loop2k] -
                            eta_lambda * node -> weight[loop2i] -> weight[loop2j][loop2k];
                        
				node -> weight[loop2i] -> weight[loop2j][loop2k] +=
					node -> weight_delta[loop2i] -> weight[loop2j][loop2k];
			}
            
			node -> weight_delta[loop2i] -> bias[loop2j] =
				eta_delta + alpha * node -> weight_delta[loop2i] -> bias[loop2j];
                
			node -> weight[loop2i] -> bias[loop2j] +=
				node -> weight_delta[loop2i] -> bias[loop2j];
		}
	}
	
	//__edstrmsg("return(void).");
	return;
}

/////NEW!
void treeZero(nodeLayer* root)
{
	//__edptrmsg(root);
	if(!root)
		return;
	{
	int i;
	for(i = 0; i < root -> nchildren; i ++)
		treeZero(root -> child[i]);
	}
	nodeZero(root);
	
	//__edstrmsg("return(void).");
	return;
}

/////NEW!
static void nodeZero(nodeLayer* node)
{
	//__edptrmsg(node);

	if(node -> nchildren < 1)
		return;
	
	/*
		loop2i - A toplevel loop iterating over the children of node.
		loop2j - A nested loop iterating over the nodes of node.
		
		Iterating over the nodes of node is the same as iterating over nodes of
		weight and node's activations (same for every child).
		
		loop2k - A nested loop iterating over the inputs of weight[loop2i].
		
		Iterating over the inputs of weight is the same as iterating over node's
		childrens' activations (different for every child).
	*/
	int loop2i = 0;
	int loop2j = 0;
	int loop2k = 0;
	
	/*	Clear these fields:
		node -> weight_delta[loop2i] -> weight[loop2j][loop2k]
		node -> weight_delta[loop2i] -> bias[loop2j]
	*/
	
	for(loop2i = 0; loop2i < node -> nchildren; loop2i++)
		for(loop2j = 0; loop2j < node -> nnodes; loop2j++)
		{
			node -> weight_delta[loop2i] -> bias[loop2j] = 0.0;
			for(loop2k = 0; loop2k < node -> weight[loop2i] -> ninputs; loop2k++)
				node -> weight_delta[loop2i] -> weight[loop2j][loop2k] = 0.0;
		}
			
	//__edstrmsg("return(void).");
	return;
}
