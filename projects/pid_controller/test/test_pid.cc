#include <gtest/gtest.h>

extern "C" {
#include "pid.h"
}

class PIDTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Initialize PID controller before each test
        pid_init(&pid, 1.0f, 0.1f, 0.01f, -100.0f, 100.0f, 0.01f);
    }

    void TearDown() override {
        // Cleanup after each test if needed
    }

    PID pid;
};

// TODO: Add test cases here
// Example test case:
// TEST_F(PIDTest, Initialization) {
//     EXPECT_EQ(pid.kp, 1.0f);
//     EXPECT_EQ(pid.ki, 0.1f);
// }
