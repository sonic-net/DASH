cmake_minimum_required(VERSION 3.5)

project(dash-plugin)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -I /SAI/SAI/inc -I /SAI/SAI/experimental")

find_package(VPP)

add_subdirectory(dash)
