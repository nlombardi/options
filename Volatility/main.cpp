#ifndef _MAIN_CPP
#define _MAIN_CPP

#include "black_scholes.h"
#include "interval_bisection.h"
#include <iostream>

int main(int argc, char **argv) {
    // Create parameter list
    double S {0}; std::cin >> S;    // Spot price
    double K {0}; std::cin >> K;    // Strike price
    double r {0}; std::cin >> r;    // RFR
    double T {0}; std::cin >> T;    // Time to maturity in years
    double C {0}; std::cin >> C;    // Option market price

    // Create BS Call functor
    BlackScholesCall bsc(S, K, r, T);

    // Interva bisection parameters
    double low_vol = 0.05;
    double high_vol = 0.35;
    double epsilon = 0.001;

    // Calc implied volatility
    double sigma = interval_bisection(C, low_vol, high_vol, epsilon, bsc);

    // Output the implied vol
    std::cout << "Implied Vol: " << sigma << std:endl;
}

#endif