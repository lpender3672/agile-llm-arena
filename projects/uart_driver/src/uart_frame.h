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
