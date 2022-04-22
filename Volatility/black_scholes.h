//
// Created by Nick Lombardi on 2022-04-22.
//

#ifndef _BLACK_SCHOLES_H
#define _BLACK_SCHOLES_H

class BlackScholesCall {
private:
    double S; // asset price
    double K;
    double r;
    double T;

public:
    BlackScholesCall(double _S, double _K, double _r, double _T);
    // volatility is repeatedly called as we step closer to the implied value
    double operator()(double sigma) const;
};

#endif //_BLACK_SCHOLES_H
