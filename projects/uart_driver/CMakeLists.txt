cmake_minimum_required(VERSION 3.14)
project(uart_driver C CXX)

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

# Library: UART frame implementation
add_library(uart_frame_lib src/uart_frame.c)
target_include_directories(uart_frame_lib PUBLIC src)

# Test executable (C++ with gtest)
add_executable(test_uart_frame test/test_uart_frame.cc)
target_link_libraries(test_uart_frame uart_frame_lib gtest_main)
target_include_directories(test_uart_frame PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Enable testing
enable_testing()
add_test(NAME uart_frame_tests COMMAND test_uart_frame)
