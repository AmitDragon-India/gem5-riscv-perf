/*
 * Memory Copy - Memory-bound benchmark
 * Tests memory bandwidth and cache pressure
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIZE (1024 * 1024)  // 1MB

int src[SIZE], dst[SIZE];

int main() {
    // Initialize source
    for (int i = 0; i < SIZE; i++)
        src[i] = i;

    // Memory copy — stress memory bandwidth
    for (int iter = 0; iter < 4; iter++)
        memcpy(dst, src, SIZE * sizeof(int));

    printf("MemCopy done. dst[0]=%d, dst[SIZE-1]=%d\n",
            dst[0], dst[SIZE-1]);
    return 0;
}
