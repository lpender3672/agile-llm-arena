"""
Reference implementation examples for template projects.
Can be used as guidance or copied into projects to verify build/test infrastructure.
"""

# PID Controller reference implementation
PID_IMPLEMENTATION = """\
#include "pid.h"
#include <math.h>

void pid_init(PID *pid, float kp, float ki, float kd,
              float output_min, float output_max, float dt) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integral = 0.0f;
    pid->prev_measurement = 0.0f;
    pid->output_min = output_min;
    pid->output_max = output_max;
    pid->dt = dt;
}

float pid_update(PID *pid, float setpoint, float measurement) {
    if (pid->dt == 0.0f) {
        return 0.0f;
    }
    
    // Calculate error
    float error = setpoint - measurement;
    
    // Proportional term
    float p_term = pid->kp * error;
    
    // Integral term with anti-windup
    float i_term = pid->ki * pid->integral;
    float i_term_new = pid->integral + error * pid->dt;
    
    // Derivative term on measurement (not error) to avoid derivative kick
    float d_term = pid->kd * (pid->prev_measurement - measurement) / pid->dt;
    
    // Calculate unclamped output
    float output = p_term + i_term + d_term;
    
    // Clamp output
    if (output < pid->output_min) {
        output = pid->output_min;
    } else if (output > pid->output_max) {
        output = pid->output_max;
    }
    
    // Anti-windup: only update integral if not saturated
    if (output == p_term + i_term + d_term) {
        pid->integral = i_term_new;
    }
    
    pid->prev_measurement = measurement;
    
    return output;
}

void pid_reset(PID *pid) {
    pid->integral = 0.0f;
    pid->prev_measurement = 0.0f;
}
"""

# UART Frame reference implementation
UART_IMPLEMENTATION = """\
#include "uart_frame.h"

// CRC-8 calculation using polynomial 0x07 (CRC-8/SMBUS)
static uint8_t crc8_smbus(const uint8_t *data, uint8_t len) {
    uint8_t crc = 0x00;
    for (uint8_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

// COBS encoding: add 0x00 delimiters, remove 0x00 from data
int uart_frame_encode(const uint8_t *payload, uint8_t len,
                      uint8_t *out_buf, uint8_t out_size) {
    if (len == 0 || len > UART_FRAME_MAX_PAYLOAD) {
        return -1;
    }
    
    if (out_size < len + 3) {
        return -1;  // Buffer too small
    }
    
    // Calculate CRC of payload
    uint8_t crc = crc8_smbus(payload, len);
    
    // COBS encode: replace 0x00 with escape sequences
    uint8_t out_idx = 0;
    uint8_t code_idx = 0;
    uint8_t code = 1;
    
    for (uint8_t i = 0; i < len; ++i) {
        if (payload[i] == 0x00) {
            out_buf[code_idx] = code;
            code_idx = out_idx;
            out_idx++;
            code = 1;
        } else {
            out_buf[out_idx++] = payload[i];
            code++;
            if (code == 0xFF) {
                out_buf[code_idx] = code;
                code_idx = out_idx;
                out_idx++;
                code = 1;
            }
        }
    }
    
    // Add CRC
    if (crc == 0x00) {
        out_buf[code_idx] = code;
        code_idx = out_idx;
        out_idx++;
        code = 1;
    } else {
        out_buf[out_idx++] = crc;
        code++;
    }
    
    out_buf[code_idx] = code;
    
    // Add final delimiter
    out_buf[out_idx++] = UART_FRAME_DELIMITER;
    
    return out_idx;
}

UartFrameError uart_frame_decode(const uint8_t *frame, uint8_t frame_len,
                                 uint8_t *payload_out, uint8_t *payload_len) {
    if (frame_len == 0) {
        return UART_FRAME_ERR_ENCODING;
    }
    
    // COBS decode
    uint8_t out_idx = 0;
    uint8_t i = 0;
    
    while (i < frame_len) {
        uint8_t code = frame[i];
        i++;
        
        if (code == 0x00) {
            return UART_FRAME_ERR_ENCODING;
        }
        
        for (uint8_t j = 1; j < code; ++j) {
            if (i >= frame_len) {
                return UART_FRAME_ERR_ENCODING;
            }
            payload_out[out_idx++] = frame[i];
            i++;
            
            if (out_idx > UART_FRAME_MAX_PAYLOAD) {
                return UART_FRAME_ERR_TOO_LONG;
            }
        }
        
        if (i < frame_len && code < 0xFF) {
            payload_out[out_idx++] = 0x00;
        }
    }
    
    // Last byte should be CRC, check it
    if (out_idx < 1) {
        return UART_FRAME_ERR_ENCODING;
    }
    
    uint8_t received_crc = payload_out[out_idx - 1];
    uint8_t expected_crc = crc8_smbus(payload_out, out_idx - 1);
    
    if (received_crc != expected_crc) {
        return UART_FRAME_ERR_BAD_CRC;
    }
    
    *payload_len = out_idx - 1;
    
    if (*payload_len > UART_FRAME_MAX_PAYLOAD) {
        return UART_FRAME_ERR_TOO_LONG;
    }
    
    return UART_FRAME_OK;
}
"""

# Example tests for PID controller
PID_TESTS_EXAMPLE = """\
#include "unity.h"
#include "../src/pid.h"

void setUp(void) {}
void tearDown(void) {}

void test_pid_init() {
    PID pid;
    pid_init(&pid, 1.0f, 0.1f, 0.01f, -100.0f, 100.0f, 0.01f);
    
    TEST_ASSERT_EQUAL_FLOAT(1.0f, pid.kp);
    TEST_ASSERT_EQUAL_FLOAT(0.1f, pid.ki);
    TEST_ASSERT_EQUAL_FLOAT(0.01f, pid.kd);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, pid.integral);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, pid.prev_measurement);
    TEST_ASSERT_EQUAL_FLOAT(-100.0f, pid.output_min);
    TEST_ASSERT_EQUAL_FLOAT(100.0f, pid.output_max);
    TEST_ASSERT_EQUAL_FLOAT(0.01f, pid.dt);
}

void test_pid_reset() {
    PID pid;
    pid_init(&pid, 1.0f, 0.1f, 0.01f, -100.0f, 100.0f, 0.01f);
    pid.integral = 5.0f;
    pid.prev_measurement = 10.0f;
    
    pid_reset(&pid);
    
    TEST_ASSERT_EQUAL_FLOAT(0.0f, pid.integral);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, pid.prev_measurement);
}

void test_pid_zero_dt() {
    PID pid;
    pid_init(&pid, 1.0f, 0.1f, 0.01f, -100.0f, 100.0f, 0.0f);
    
    float output = pid_update(&pid, 50.0f, 0.0f);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, output);
}

void test_pid_output_clamping() {
    PID pid;
    pid_init(&pid, 1000.0f, 0.0f, 0.0f, -50.0f, 50.0f, 0.01f);
    
    float output = pid_update(&pid, 100.0f, 0.0f);
    TEST_ASSERT_EQUAL_FLOAT(50.0f, output);  // Clamped to max
    
    output = pid_update(&pid, -100.0f, 0.0f);
    TEST_ASSERT_EQUAL_FLOAT(-50.0f, output);  // Clamped to min
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_pid_init);
    RUN_TEST(test_pid_reset);
    RUN_TEST(test_pid_zero_dt);
    RUN_TEST(test_pid_output_clamping);
    return UNITY_END();
}
"""

# Example tests for UART frame
UART_TESTS_EXAMPLE = """\
#include "unity.h"
#include "../src/uart_frame.h"
#include <string.h>

void setUp(void) {}
void tearDown(void) {}

void test_encode_simple_payload() {
    uint8_t payload[] = {0x01, 0x02, 0x03};
    uint8_t out_buf[256];
    
    int result = uart_frame_encode(payload, 3, out_buf, 256);
    
    TEST_ASSERT_GREATER_THAN(0, result);
    TEST_ASSERT_EQUAL_UINT8(UART_FRAME_DELIMITER, out_buf[result - 1]);
}

void test_encode_empty_payload() {
    uint8_t out_buf[256];
    
    int result = uart_frame_encode(NULL, 0, out_buf, 256);
    
    TEST_ASSERT_EQUAL(-1, result);
}

void test_encode_too_long_payload() {
    uint8_t payload[200];
    uint8_t out_buf[256];
    
    int result = uart_frame_encode(payload, 200, out_buf, 256);
    
    TEST_ASSERT_EQUAL(-1, result);
}

void test_decode_valid_frame() {
    uint8_t payload[] = {0x01, 0x02, 0x03};
    uint8_t encoded[256];
    uint8_t decoded[256];
    uint8_t decoded_len;
    
    int enc_len = uart_frame_encode(payload, 3, encoded, 256);
    TEST_ASSERT_GREATER_THAN(0, enc_len);
    
    UartFrameError result = uart_frame_decode(encoded, enc_len - 1, decoded, &decoded_len);
    
    TEST_ASSERT_EQUAL(UART_FRAME_OK, result);
    TEST_ASSERT_EQUAL(3, decoded_len);
}

void test_decode_bad_crc() {
    uint8_t frame[] = {0x03, 0x01, 0x02, 0xFF, 0x00};  // Bad CRC
    uint8_t payload[256];
    uint8_t payload_len;
    
    UartFrameError result = uart_frame_decode(frame, 4, payload, &payload_len);
    
    TEST_ASSERT_EQUAL(UART_FRAME_ERR_BAD_CRC, result);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_encode_simple_payload);
    RUN_TEST(test_encode_empty_payload);
    RUN_TEST(test_encode_too_long_payload);
    RUN_TEST(test_decode_valid_frame);
    RUN_TEST(test_decode_bad_crc);
    return UNITY_END();
}
"""
