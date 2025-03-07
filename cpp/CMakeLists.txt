cmake_minimum_required(VERSION 3.27)
project(rat)

add_executable(rat)

set_property(TARGET rat PROPERTY CMAKE_CXX_STANDARD 26)
set_property(TARGET rat PROPERTY CMAKE_CXX_STANDARD_REQUIRED 26)
set_property(TARGET rat PROPERTY CMAKE_CXX_EXTENSIONS OFF)
target_compile_options(rat PUBLIC -Wall -Wextra -pedantic -Werror -Wfatal-errors -fmodules-ts)

target_sources(rat PUBLIC
      ${PROJECT_SOURCE_DIR}/main.cpp
    PUBLIC
    FILE_SET CXX_MODULES
    BASE_DIRS ${PROJECT_SOURCE_DIR}
    FILES
    )
target_include_directories(rat PUBLIC ${PROJECT_SOURCE_DIR}/include)
