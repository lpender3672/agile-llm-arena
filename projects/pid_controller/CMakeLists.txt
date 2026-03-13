cmake_minimum_required(VERSION 3.14)
project(pid_controller C CXX)

# Set runtime library for Windows
if(MSVC OR (CMAKE_C_COMPILER_ID MATCHES "Clang" AND WIN32))
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
endif()

# Set C standard
set(CMAKE_C_STANDARD 99)

# Try to find Clang, fallback to system default
if(NOT CMAKE_C_COMPILER)
    find_program(CLANG_COMPILER clang)
    if(CLANG_COMPILER)
        set(CMAKE_C_COMPILER ${CLANG_COMPILER})
        set(CMAKE_CXX_COMPILER clang++)
    endif()
endif()

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -g")
if(NOT WIN32)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
endif()

# Fetch Google Test with proper options for Windows
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/v1.14.0.zip
)

# Set gtest options before making it available
set(gtest_force_shared_crt ON CACHE BOOL "Use shared (DLL) run-time library even when libraries are static" FORCE)

FetchContent_MakeAvailable(googletest)

# Library: PID implementation
add_library(pid_lib src/pid.c)
target_include_directories(pid_lib PUBLIC src)

# Test executable (C++ with gtest)
add_executable(test_pid test/test_pid.cc)
target_include_directories(test_pid PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
if(WIN32)
    target_link_libraries(test_pid pid_lib gtest_main)
else()
    target_link_libraries(test_pid pid_lib gtest_main m)
endif()

# Enable testing
enable_testing()
add_test(NAME pid_tests COMMAND test_pid)
