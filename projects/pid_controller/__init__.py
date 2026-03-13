"""PID controller benchmark project definition."""

SPEC = {
    "name": "PID Controller",
    "module": "pid",
    "description": "Discrete-time PID controller for embedded motor/process control.",
    "spec": """
Implement a discrete-time PID controller in C.

API (defined in pid.h):

  typedef struct {
      float kp, ki, kd;
      float integral;
      float prev_error;
      float output_min, output_max;  // clamping limits
      float dt;                       // sample period (seconds)
  } PID;

  void  pid_init(PID *pid, float kp, float ki, float kd,
                 float output_min, float output_max, float dt);
  float pid_update(PID *pid, float setpoint, float measurement);
  void  pid_reset(PID *pid);   // zero integral and prev_error

Requirements:
- Anti-windup: clamp integral when output is saturated.
- Output must be clamped to [output_min, output_max].
- dt == 0.0 must not cause divide-by-zero (return 0.0).
- Derivative on measurement (not error) to avoid derivative kick.
""",
}

SKELETON = {
    "src/pid.h": """\
#pragma once

typedef struct {
    float kp, ki, kd;
    float integral;
    float prev_measurement;
    float output_min, output_max;
    float dt;
} PID;

void  pid_init(PID *pid, float kp, float ki, float kd,
               float output_min, float output_max, float dt);
float pid_update(PID *pid, float setpoint, float measurement);
void  pid_reset(PID *pid);
""",
    "src/pid.c": """\
#include "pid.h"

/* TODO: implement */
""",
    "test/test_pid.c": """\
#include "unity.h"
#include "../src/pid.h"

void setUp(void) {}
void tearDown(void) {}

/* TODO: write tests */

int main(void) {
    UNITY_BEGIN();
    return UNITY_END();
}
""",
    "CMakeLists.txt": """\
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
""",
    "mull.yml": """\
# MULL Mutation Testing Configuration for PID Controller
mutators:
  - cxx_eq_to_ne
  - cxx_lt_to_le
  - cxx_gt_to_ge
  - cxx_le_to_lt
  - cxx_ge_to_gt
  - cxx_add_to_sub
  - cxx_sub_to_add
  - cxx_mul_to_div
  - cxx_rem_to_div
  - cxx_bitwise_and_to_or
  - cxx_bitwise_or_to_and
  - cxx_bitwise_xor_to_or

tests:
  - test_pid

timeout: 5000
""",
}

FILE_TREE = "\n".join(f"  {k}" for k in SKELETON)
