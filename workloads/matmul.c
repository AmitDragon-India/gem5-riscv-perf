/*
 * Matrix Multiplication - Compute-bound benchmark
 * Tests CPU utilization and arithmetic throughput
 */
#include <stdio.h>
#include <stdlib.h>

#define N 64

int A[N][N], B[N][N], C[N][N];

void matmul() {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            C[i][j] = 0;
            for (int k = 0; k < N; k++)
                C[i][j] += A[i][k] * B[k][j];
        }
}

int main() {
    // Initialize matrices
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            A[i][j] = i + j;
            B[i][j] = i - j;
        }

    matmul();

    printf("MatMul done. C[0][0]=%d, C[N-1][N-1]=%d\n", 
            C[0][0], C[N-1][N-1]);
    return 0;
}
