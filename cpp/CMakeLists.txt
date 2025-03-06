cmake_minimum_required(VERSION 3.25)
project(rat)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_compile_options(-Wall -Wextra -pedantic -Werror -Wfatal-errors)

set (SRC main.cpp)
add_executable(rat "${SRC}")
