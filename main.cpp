#include <iostream>
#include <iomanip>
#include <chrono>
#include <cmath>

int main() {
    using namespace std;

    const unsigned long long iterations = 200000000ull;

    auto start = chrono::high_resolution_clock::now();

    // Using the identity:
    // 4 * calculate(n, 4, 1) = pi + psi(n + 1.25) - psi(n + 0.75)
    // and the asymptotic expansion of digamma:
    // psi(x) = ln(x) - 1/(2x) - 1/(12x^2) + 1/(120x^4) - 1/(252x^6) + 1/(240x^8) - 1/(132x^10) + ...
    const double pi = 3.141592653589793238462643383279502884;
    const double a = static_cast<double>(iterations) + 1.25;
    const double b = static_cast<double>(iterations) + 0.75;

    const double inva = 1.0 / a, invb = 1.0 / b;
    const double inva2 = inva * inva, invb2 = invb * invb;
    const double inva4 = inva2 * inva2, invb4 = invb2 * invb2;
    const double inva6 = inva4 * inva2, invb6 = invb4 * invb2;
    const double inva8 = inva4 * inva4, invb8 = invb4 * invb4;
    const double inva10 = inva8 * inva2, invb10 = invb8 * invb2;

    double d = std::log(a / b);
    d -= 0.5 * (inva - invb);
    d -= (1.0 / 12.0) * (inva2 - invb2);
    d += (1.0 / 120.0) * (inva4 - invb4);
    d -= (1.0 / 252.0) * (inva6 - invb6);
    d += (1.0 / 240.0) * (inva8 - invb8);
    d -= (1.0 / 132.0) * (inva10 - invb10);

    const double result = pi + d;

    auto end = chrono::high_resolution_clock::now();
    double exec_seconds = chrono::duration<double>(end - start).count();

    cout.setf(ios::fixed);
    cout << "Result: " << setprecision(12) << result << "\n";
    cout << "Execution Time: " << setprecision(6) << exec_seconds << " seconds\n";

    return 0;
}