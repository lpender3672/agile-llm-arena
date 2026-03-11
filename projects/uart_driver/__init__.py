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
    "Makefile": """\
CC      = gcc
CFLAGS  = -Wall -Wextra -g -Isrc -Itest/unity
UNITY   = test/unity/unity.c

test: test/test_uart_frame
\t./test/test_uart_frame

test/test_uart_frame: src/uart_frame.c test/test_uart_frame.c $(UNITY)
\t$(CC) $(CFLAGS) $^ -o $@

.PHONY: test
""",
}

FILE_TREE = "\n".join(f"  {k}" for k in SKELETON)
