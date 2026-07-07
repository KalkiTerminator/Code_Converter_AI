#include <cstdio>
#include <cstdint>
#include <chrono>

#pragma float_control(precise, on, push)
#pragma fp_contract(off)

static inline double calculate(uint32_t iterations, int param1, int param2) {
    double result = 1.0;

    int j1 = param1 - param2; // 4*1 - 1 = 3
    int j2 = param1 + param2; // 4*1 + 1 = 5

    const uint32_t UNROLL = 8;
    uint32_t blocks = iterations / UNROLL;
    uint32_t rem = iterations % UNROLL;

    // Maintain strict operation order to mirror Python semantics
    #pragma loop(no_vector)
    for (uint32_t b = 0; b < blocks; ++b) {
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
        result -= 1.0 / (double)j1; result += 1.0 / (double)j2; j1 += param1; j2 += param1;
    }

    for (uint32_t r = 0; r < rem; ++r) {
        result -= 1.0 / (double)j1;
        result += 1.0 / (double)j2;
        j1 += param1;
        j2 += param1;
    }

    return result;
}

int main() {
    using clock = std::chrono::high_resolution_clock;

    auto start_time = clock::now();
    double result = calculate(200000000u, 4, 1) * 4.0;
    auto end_time = clock::now();

    double elapsed = std::chrono::duration<double>(end_time - start_time).count();

    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", elapsed);
    return 0;
}

#pragma float_control(pop)