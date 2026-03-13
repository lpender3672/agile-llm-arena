cmake_minimum_required(VERSION 3.10)
project(pid_controller C)

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

# Library: PID implementation
add_library(pid_lib src/pid.c)
target_include_directories(pid_lib PUBLIC src)

# Test executable
add_executable(test_pid test/test_pid.c)
target_link_libraries(test_pid pid_lib ${UNITY_LIBRARIES} m)

# Enable testing
enable_testing()
add_test(NAME pid_tests COMMAND test_pid)

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

# Library: PID implementation
add_library(pid_lib src/pid.c)
target_include_directories(pid_lib PUBLIC src)

# Test executable
add_executable(test_pid test/test_pid.c)
target_link_libraries(test_pid pid_lib ${UNITY_LIBRARIES} m)

# Enable testing
enable_testing()
add_test(NAME pid_tests COMMAND test_pid)
