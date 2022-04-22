cmake_minimum_required(VERSION 3.17)
project(ImpliedVolatility)

set(CMAKE_CXX_STANDARD 17)

add_executable(ImpliedVolatility main.cpp bs_prices.cpp bs_prices.h black_scholes.h black_scholes.cpp interval_bisection.h)