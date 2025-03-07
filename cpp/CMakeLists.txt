cmake_minimum_required(VERSION 3.27)
project(rat)

add_executable(rat)

set_property(TARGET rat PROPERTY CMAKE_CXX_EXTENSIONS OFF)
target_compile_options(rat PUBLIC -Wall -Wextra -pedantic -Werror -Wfatal-errors -fmodules-ts)
target_compile_features(rat PUBLIC cxx_std_26)

target_sources(rat
  PUBLIC
    FILE_SET CXX_MODULES FILES
      main.cpp)

target_include_directories(rat PUBLIC ${PROJECT_SOURCE_DIR}/include)
