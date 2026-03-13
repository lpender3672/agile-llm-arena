# Building Template Projects with CMake and Clang

This guide explains how to build and test the template projects using CMake, Clang, and MULL mutation testing.

## Prerequisites

### Required
- **CMake** 3.10 or later
- **Clang** compiler (any recent version)
- **Unity** testing framework (for C unit tests)

### Optional (for mutation testing)
- **MULL** mutation testing tool

#### Installation (Ubuntu/Debian)
```bash
sudo apt-get install cmake clang libunity-dev
# For MULL, see https://mull.readthedocs.io/
```

#### Installation (macOS with Homebrew)
```bash
brew install cmake llvm
brew install libunity
# For MULL: brew install mull (if available) or build from source
```

#### Installation (Windows with MSVC/WSL)
```powershell
# Using vcpkg or pre-built binaries
vcpkg install cmake:x64-windows clang:x64-windows
```

Or use Windows Subsystem for Linux (WSL) with Ubuntu instructions above.

## Building a Project

Each project (e.g., `projects/pid_controller/`) contains:
- `CMakeLists.txt` - CMake build configuration
- `src/` - Source files (.h, .c)
- `test/` - Test files using Unity framework
- `mull.yml` - MULL mutation testing configuration

### Typical Build Process

```bash
cd projects/pid_controller/  # or projects/uart_driver/

# Create build directory
mkdir build
cd build

# Configure with CMake (uses Clang by default)
cmake .. -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++

# Build
cmake --build .

# Run tests
ctest --verbose
```

### Or use the provided build script

```bash
chmod +x build.sh
./build.sh pid_controller
```

## Project Structure

### PID Controller (`projects/pid_controller/`)

**API Contract:**
```c
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
```

**Implementation Requirements:**
- Anti-windup: clamp integral when output is saturated
- Output must be clamped to [output_min, output_max]
- Handle dt == 0.0 without divide-by-zero
- Use derivative on measurement (not error)

### UART Framing Layer (`projects/uart_driver/`)

**API Contract:**
```c
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
```

**Implementation Requirements:**
- COBS (Consistent Overhead Byte Stuffing) encoding
- CRC-8 (polynomial 0x07 / CRC-8/SMBUS)
- Payload size limit enforcement
- No 0x00 bytes in encoded data

## MULL Mutation Testing

MULL is a mutation testing tool for C/C++ that automatically introduces bugs (mutants) into the code to verify your tests catch them.

### Running MULL

```bash
cd projects/pid_controller/
mull-runner -config mull.yml --log-level=info
```

### Understanding MULL Output

- **Killed**: Mutants that your tests detected and failed
- **Survived**: Mutants that passed your tests (missed by tests)
- **Mutation Score**: killed / (killed + survived)

A mutation score of 1.0 means excellent test coverage; lower scores indicate tests that miss certain code paths.

### MULL Configuration (mull.yml)

The configuration file specifies:
- **Mutators**: Types of mutations to apply (e.g., arithmetic operator changes)
- **Tests**: Which test executables to run
- **Timeout**: Maximum time per mutant evaluation (ms)

Example:
```yaml
mutators:
  - cxx_eq_to_ne      # Change == to !=
  - cxx_add_to_sub    # Change + to -
  - cxx_lt_to_le      # Change < to <=

tests:
  - test_pid          # Test executable name

timeout: 5000
```

## CMake Build Details

### Compiler Flags

The CMakeLists.txt uses:
- `-Wall -Wextra`: Enable all warnings
- `-g`: Debug symbols (for MULL and debugging)
- `-fPIC`: Position-independent code
- `-m64`: 64-bit compilation (explicit)
- `-std=c99`: C99 standard

### Unity Integration

Unity is a lightweight C unit testing framework. Tests are written as:

```c
#include "unity.h"
#include "../src/pid.h"

void test_pid_init() {
    PID pid;
    pid_init(&pid, 1.0, 0.1, 0.01, -100.0, 100.0, 0.01);
    TEST_ASSERT_EQUAL_FLOAT(1.0, pid.kp);
    TEST_ASSERT_EQUAL_FLOAT(0.0, pid.integral);
}

void setUp(void) {}  // Test setup (called before each test)
void tearDown(void) {}  // Test cleanup

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_pid_init);
    return UNITY_END();
}
```

### Linking with Libraries

The CMakeLists.txt links:
- `target_link_libraries(test_pid pid_lib ${UNITY_LIBRARIES} m)`
  - `pid_lib`: Your implementation library
  - `${UNITY_LIBRARIES}`: Unity test framework
  - `m`: Math library (for floating-point functions)

## Verification Tests

The workspace includes `tests/test_project_build.py` which verifies:
1. Each project compiles with CMake and Clang
2. Each project's test executable is created
3. Each project's tests run successfully

Run these verification tests:
```bash
pytest tests/test_project_build.py -v
```

## Troubleshooting

### CMake Not Found
```
CMake not found. Install with:
  Ubuntu: sudo apt-get install cmake
  macOS: brew install cmake
  Windows: https://cmake.org/download/
```

### Clang Not Found
```
clang compiler not found. Install with:
  Ubuntu: sudo apt-get install clang
  macOS: brew install llvm
  Windows: Use MSVC or install clang-cl via Visual Studio
```

### Unity Headers Not Found
```
Unity framework not installed. Install with:
  Ubuntu: sudo apt-get install libunity-dev
  macOS: brew install libunity
  Or: Download from https://github.com/ThrowTheSwitch/Unity
```

### MULL Not Available
```
MULL is optional. If you want mutation testing:
  See: https://mull.readthedocs.io/
```

### Build Fails on Windows

Windows may require additional setup:
1. Use Windows Subsystem for Linux (WSL) with Ubuntu
2. Or use Visual Studio with MSVC toolchain (adjust CMakeLists.txt)
3. Or use MinGW with CMake

## Next Steps

1. **Implement the required functions** in `src/` files
2. **Write comprehensive tests** in `test/` files using Unity
3. **Build and verify** with CMake
4. **Run mutation tests** with MULL to find test gaps
5. **Add tests** to kill surviving mutants
6. **Achieve 100% mutation score** for high confidence

## References

- CMake: https://cmake.org/
- Clang: https://clang.llvm.org/
- Unity Testing: https://github.com/ThrowTheSwitch/Unity
- MULL Mutation Testing: https://mull.readthedocs.io/
- COBS Encoding: https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing
