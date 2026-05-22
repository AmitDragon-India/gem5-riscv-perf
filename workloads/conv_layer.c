/*
 * 2D Convolution Layer - AI inference proxy benchmark
 * Mixed compute and memory bound — models DNN workloads
 */
#include <stdio.h>
#include <stdlib.h>

#define IN_H  32
#define IN_W  32
#define K     3      // kernel size
#define OUT_H (IN_H - K + 1)
#define OUT_W (IN_W - K + 1)
#define FILTERS 8

int input[IN_H][IN_W];
int kernel[FILTERS][K][K];
int output[FILTERS][OUT_H][OUT_W];

void conv2d() {
    for (int f = 0; f < FILTERS; f++)
        for (int i = 0; i < OUT_H; i++)
            for (int j = 0; j < OUT_W; j++) {
                int sum = 0;
                for (int ki = 0; ki < K; ki++)
                    for (int kj = 0; kj < K; kj++)
                        sum += input[i+ki][j+kj] * kernel[f][ki][kj];
                output[f][i][j] = sum;
            }
}

int main() {
    // Initialize input and kernels
    for (int i = 0; i < IN_H; i++)
        for (int j = 0; j < IN_W; j++)
            input[i][j] = i * IN_W + j;

    for (int f = 0; f < FILTERS; f++)
        for (int i = 0; i < K; i++)
            for (int j = 0; j < K; j++)
                kernel[f][i][j] = f + i - j;

    conv2d();

    printf("Conv2D done. output[0][0][0]=%d, output[%d][%d][%d]=%d\n",
            output[0][0][0],
            FILTERS-1, OUT_H-1, OUT_W-1,
            output[FILTERS-1][OUT_H-1][OUT_W-1]);
    return 0;
}
