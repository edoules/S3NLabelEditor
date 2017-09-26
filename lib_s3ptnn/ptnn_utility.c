#include <stdlib.h>
#include <assert.h>
#include <math.h>

#include "ptnn_utility.h"

#ifndef __APPLE__
#define random() rand()
#endif

double random_double(double average, double amplitude, double hole)
{
	double result =
		(2 * amplitude * (random()/(double)RAND_MAX) - amplitude) + average;
	assert(!isnan(result));
	return result > average? result + hole: result - hole;
}

double squared_error(int ndoubles, double* a, double *b)
{
	int activation;
	double retVal = 0.0;
	for(activation = 0; activation < ndoubles; activation ++)
	{
		retVal +=
			(a[activation] - b[activation]) *
				(a[activation] - b[activation]);
	}
	return retVal;
}

double root_mean_squared_error(double sse, int npatterns, int noutputs)
{
	return sqrt(sse / ((double)npatterns) / noutputs);
}
