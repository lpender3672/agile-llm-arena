cmake_minimum_required(VERSION 3.10)
project(uart_driver C)

set(CMAKE_C_COMPILER clang)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -g -fPIC -m64")
set(CMAKE_C_STANDARD 99)

# Find Unity testing framework
find_package(PkgConfig REQUIRED)
pkg_check_modules(UNITY unity)

if(NOT UNITY_FOUND)
    message(STATUS "Unity not found via pkg-config, using system paths")
    set(UNITY_INCLUDE_DIRS "/usr/include")
    set(UNITY_LIBRARIES "unity")
endif()

include_directories(src)
include_directories(${UNITY_INCLUDE_DIRS})

# Library: UART frame implementation
add_library(uart_frame_lib src/uart_frame.c)
target_include_directories(uart_frame_lib PUBLIC src)

# Test executable
add_executable(test_uart_frame test/test_uart_frame.c)
target_link_libraries(test_uart_frame uart_frame_lib ${UNITY_LIBRARIES})

# Enable testing
enable_testing()
add_test(NAME uart_frame_tests COMMAND test_uart_frame)
