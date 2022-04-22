//
// Created by Nick Lombardi on 2022-04-22.
//

#ifndef _INTERVAL_BISECTION_H
#define _INTERVAL_BISECTION_H

#include <cmath>

// Function tempalte
// Find an x s.t. |g(x) - y| < epsilon, interval (m, n)
template<typename T>
double interval_bisection(double y_target,         // Target y value
                          double m,         // Starting interval
                          double n,         // Ending interval
                          double epsilon,   // Tolerance level
                          T g) {            // Function object of type T, name g

    // Set initial midpoint -> x
    // Find the mapped y value of g(x)
    double x = 0.5 * (m+n);
    double y = g(x);

    // While y - y_target > epsilon -> subdivide interval in smaller halves and re-evaluate y
    do {
        if (y < y_target) {
            m = x;
        }
        if (y > y_target) {
            n = x;
        }
        x = 0.5 * (m+n);
        y = g(x);
    } while (fabs(y-y_target) > epsilon);

    return x;

}

#endif //_INTERVAL_BISECTION_H
