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
    "Makefile": """\
CC      = gcc
CFLAGS  = -Wall -Wextra -g -Isrc -Itest/unity -lm
UNITY   = test/unity/unity.c

test: test/test_pid
\t./test/test_pid

test/test_pid: src/pid.c test/test_pid.c $(UNITY)
\t$(CC) $(CFLAGS) $^ -o $@ -lm

.PHONY: test
""",
}

FILE_TREE = "\n".join(f"  {k}" for k in SKELETON)
