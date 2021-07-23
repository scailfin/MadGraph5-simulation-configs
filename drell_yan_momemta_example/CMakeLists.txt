cmake_minimum_required(VERSION 3.7...3.20)

if(${CMAKE_VERSION} VERSION_LESS 3.12)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()

project(Drell-Yan-Examples)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic -Wextra")

# Require c++11 *at least*, use default compiler standard if possible
if (CMAKE_CXX_STANDARD_COMPUTED_DEFAULT STRLESS "11" OR
        CMAKE_CXX_STANDARD_COMPUTED_DEFAULT STREQUAL "98")
    set(CMAKE_CXX_STANDARD 11)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
endif()

# Stick to the standard
set(CMAKE_CXX_EXTENSIONS OFF)

# Find dependencices

# CMake will automagically also link to MoMEMta's dependencies, ie LHAPDF and ROOT
find_package(MoMEMta CONFIG REQUIRED)

# But MoMEMta doesn't use TreePlayer: we have to add it ourselves
find_library(ROOT_TREEPLAYER_LIBRARY TreePlayer HINTS ${ROOT_LIBRARY_DIR} REQUIRED)

# Add src code for example
add_subdirectory(momemta)
