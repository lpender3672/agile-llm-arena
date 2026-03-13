#include <gtest/gtest.h>
#include <cstring>

extern "C" {
#include "uart_frame.h"
}

class UartFrameTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Initialize buffers
        std::memset(encoded_buf, 0, sizeof(encoded_buf));
        std::memset(decoded_buf, 0, sizeof(decoded_buf));
    }

    void TearDown() override {
        // Cleanup after each test if needed
    }

    uint8_t encoded_buf[256];
    uint8_t decoded_buf[UART_FRAME_MAX_PAYLOAD];
    uint8_t decoded_len;
};

// TODO: Add test cases here
// Example test case:
// TEST_F(UartFrameTest, EncodeEmptyPayload) {
//     uint8_t payload[] = {};
//     int result = uart_frame_encode(payload, 0, encoded_buf, sizeof(encoded_buf));
//     EXPECT_GT(result, 0);
// }
