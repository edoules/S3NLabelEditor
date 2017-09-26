#ifndef PTNN_UTILITY_H
#define PTNN_UTILITY_H

double random_double(double average, double amplitude, double hole);

double squared_error(int ndoubles, double* a, double *b);

double root_mean_squared_error(double sse, int npatterns, int noutputs);

#endif
