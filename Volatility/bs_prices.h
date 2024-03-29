//
// Created by Nick Lombardi on 2022-04-19.
//

#ifndef __BS_PRICES_H
#define __BS_PRICES_H

#define _USE_MATH_DEFINES

#include <iostream>
#include <cmath>

// Std. Norm prob. density fn
double norm_pdf(const double x) {
    return (1.0/(pow(2*M_PI, 0.5)))*exp(-0.5*x*x);
}

// Approx to cumulative distribution fn
// for the std. norm dist
// Recursive
double norm_cdf(const double x) {
    double k = 1.0/(1.0 + 0.2316419*x);
    double k_sum = k*(0.319381530 +
                    k*(-0.356563782 +
                    k*(1.781477937 +
                    k*(-1.821255978 + 1.330274429*k))));

    if (x >= 0.0) {
        return (1.0 - (1.0/pow(2*M_PI, 0.5)))*exp(-0.5*x*x) * k_sum);
    } else {
        return 1.0 - norm_cdf(-x);
    }
}

// Calculates d_j, for j in {1,2}; from closed form solution for Euro call / put
double d_j(const int j, const double S, const double K, const double r, const double sigma, const double T) {
    return (log(S/K) + T*(r + (pow(-1, j-1))*0.5*sigma*sigma))/(sigma*(pow(T,0.5)));
}

// Calculates d_j, for j in {1,2}; w. Dividends or Neg Income
double d_j_div(const int j, const double S, const double q, const double K, const double r, const double sigma, const double T) {
    return (log(S/K) + T*(r - q + (pow(-1, j-1))*0.5*sigma*sigma))/(sigma*(pow(T,0.5)));
}

// Calculate Euro vanilla call price based on S (spot), K (strike), r (RFR), vol, T (time to maturity)
double call_price(const double S, const double K, const double r, const double sigma, const double T) {
    return S * norm_cdf(d_j(1, S, K, r, sigma, T)) - K * exp(-r*T) * norm_cdf(d_j(2, S, K, r, sigma, T));
}

#endif //_USE_MATH_DEFINES
