#ifndef PTNN_IO_H
#define PTNN_IO_H

#include <stdio.h>

#include "ptnn_weightLayer.h"

int writeWeight(FILE* file, weightLayer* weight);
weightLayer* readWeight(FILE* file);

// -1 for failure, 0 for success.
int overReadWeight(FILE* file, weightLayer* retObj);

#endif
