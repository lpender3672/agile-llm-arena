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
