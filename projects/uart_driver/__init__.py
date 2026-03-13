"""UART driver (software layer) benchmark project definition."""

SPEC = {
    "name": "UART Framing Layer",
    "module": "uart_frame",
    "description": "Software UART framing layer: frame encoding/decoding with COBS + CRC8.",
    "spec": """
Implement a UART framing layer in C using COBS encoding and CRC-8.

API (defined in uart_frame.h):

  #define UART_FRAME_MAX_PAYLOAD  128
  #define UART_FRAME_DELIMITER    0x00

  typedef enum {
      UART_FRAME_OK = 0,
      UART_FRAME_ERR_TOO_LONG,
      UART_FRAME_ERR_BAD_CRC,
      UART_FRAME_ERR_ENCODING,
  } UartFrameError;

  // Encode: payload -> COBS-encoded frame with CRC appended, terminated by 0x00
  // out_buf must be at least (len + 3) bytes.
  // Returns encoded length (including delimiter) or negative error.
  int uart_frame_encode(const uint8_t *payload, uint8_t len,
                        uint8_t *out_buf, uint8_t out_size);

  // Decode: COBS frame (without delimiter) -> payload
  // Returns UART_FRAME_OK or error code.
  UartFrameError uart_frame_decode(const uint8_t *frame, uint8_t frame_len,
                                   uint8_t *payload_out, uint8_t *payload_len);

CRC-8 polynomial: 0x07 (CRC-8/SMBUS).
COBS: standard Consistent Overhead Byte Stuffing — no 0x00 bytes in encoded data.
Payload > UART_FRAME_MAX_PAYLOAD returns UART_FRAME_ERR_TOO_LONG.
""",
}

SKELETON = {
    "src/uart_frame.h": """\
#pragma once
#include <stdint.h>

#define UART_FRAME_MAX_PAYLOAD  128
#define UART_FRAME_DELIMITER    0x00

typedef enum {
    UART_FRAME_OK = 0,
    UART_FRAME_ERR_TOO_LONG,
    UART_FRAME_ERR_BAD_CRC,
    UART_FRAME_ERR_ENCODING,
} UartFrameError;

int            uart_frame_encode(const uint8_t *payload, uint8_t len,
                                 uint8_t *out_buf, uint8_t out_size);
UartFrameError uart_frame_decode(const uint8_t *frame, uint8_t frame_len,
                                 uint8_t *payload_out, uint8_t *payload_len);
""",
    "src/uart_frame.c": """\
#include "uart_frame.h"

/* TODO: implement */
""",
    "test/test_uart_frame.c": """\
#include "unity.h"
#include "../src/uart_frame.h"

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
""",
    "mull.yml": """\
# MULL Mutation Testing Configuration for UART Frame Layer
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
  - test_uart_frame

timeout: 5000
""",
}

FILE_TREE = "\n".join(f"  {k}" for k in SKELETON)
