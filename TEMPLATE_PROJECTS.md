# Template Projects - CMake, Clang, and MULL Setup

This document describes the benchmark template projects used for testing LLM-driven development workflows with mutation testing.

## Quick Start

### Build and Test a Project

```bash
cd projects/pid_controller
mkdir build
cd build
cmake .. -DCMAKE_C_COMPILER=clang
cmake --build .
ctest --verbose
```

### Run Mutation Testing

```bash
cd projects/pid_controller
mull-runner -config mull.yml --log-level=info
```

## Projects Overview

### 1. PID Controller (`projects/pid_controller/`)

A discrete-time PID (Proportional-Integral-Derivative) controller implementation for embedded systems.

**What you need to implement:**
- `pid_init()` - Initialize PID struct with gains and limits
- `pid_update()` - Calculate PID output given setpoint and measurement
- `pid_reset()` - Zero out integral and previous error

**Key requirements:**
- Anti-windup (don't accumulate integral when output is saturated)
- Output clamping to min/max limits
- Handle zero sample time without crashing
- Derivative calculated on measurement (not error) to avoid derivative kick

**Test points:**
- Initialization verification
- Boundary condition handling (zero dt, saturation)
- Anti-windup behavior
- Step response characteristics

**Expected mutation score:** ~80-95% (comprehensive coverage needed for anti-windup and clamping logic)

### 2. UART Framing Layer (`projects/uart_driver/`)

A software UART framing layer using COBS (Consistent Overhead Byte Stuffing) encoding and CRC-8 checksums.

**What you need to implement:**
- `uart_frame_encode()` - Encode payload with COBS and CRC-8
- `uart_frame_decode()` - Decode and verify COBS frame

**Key requirements:**
- COBS encoding to eliminate 0x00 bytes in transmission
- CRC-8 (polynomial 0x07, SMBUS variant) for error detection
- Handle oversized payloads (> 128 bytes)
- Error handling for corrupted frames

**Test points:**
- Empty and full payloads
- CRC calculation correctness
- COBS edge cases (runs of 0x00, overflow)
- Round-trip encode/decode verification

**Expected mutation score:** ~85-95% (bit manipulation and CRC calculations are mutation-heavy)

## Build System: CMake + Clang

### Why CMake?

- **Standard C/C++ build tool** across all platforms
- **MULL integration** - MULL uses CMake to understand project structure
- **Cross-platform** - Works on Linux, macOS, Windows (via WSL)
- **Reproducible** - Version-controlled build specifications

### Why Clang?

- **Modern compiler** with excellent diagnostics
- **MULL support** - MULL has native Clang integration
- **Open source** and widely available
- **Consistent** behavior across platforms

### Compiler Flags

The CMakeLists.txt applies:

```cmake
-Wall -Wextra      # All warnings
-g                 # Debug symbols (required by MULL)
-fPIC              # Position-independent code
-std=c99           # C99 standard
```

## Testing: Unity Framework

[Unity](https://github.com/ThrowTheSwitch/Unity) is a lightweight C unit testing framework.

### Test Structure

```c
#include "unity.h"
#include "../src/module.h"

void setUp(void) {
    // Called before each test
}

void tearDown(void) {
    // Called after each test
}

void test_my_function() {
    // Arrange
    int result = my_function(5);
    
    // Assert
    TEST_ASSERT_EQUAL_INT(10, result);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_my_function);
    return UNITY_END();
}
```

### Common Assertions

```c
TEST_ASSERT(condition)
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_EQUAL_INT(expected, actual)
TEST_ASSERT_EQUAL_FLOAT(expected, actual)
TEST_ASSERT_NOT_EQUAL(unexpected, actual)
TEST_ASSERT_GREATER_THAN(threshold, actual)
TEST_ASSERT_LESS_THAN(threshold, actual)
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_NOT_NULL(pointer)
```

## Mutation Testing: MULL

### What is MULL?

MULL automatically modifies your code (creates "mutants") and checks if your tests can detect them. If a mutant passes all tests, it "survived" - indicating a gap in test coverage.

**Example mutations:**
- `x < y` becomes `x <= y`
- `a + b` becomes `a - b`
- `if (a) {...}` becomes `if (!a) {...}`

### Running MULL

```bash
cd projects/pid_controller
mull-runner -config mull.yml --log-level=info
```

### Interpreting Results

```
Killed:    150    # Mutants caught by tests
Survived:   20    # Mutants missed by tests
Score:     88.2%  # killed / (killed + survived)
```

Higher scores indicate better test coverage of the code.

### mull.yml Configuration

```yaml
mutators:
  - cxx_eq_to_ne      # == becomes !=
  - cxx_add_to_sub    # + becomes -
  # ... more mutators

tests:
  - test_pid          # Which test executable to run

timeout: 5000       # Milliseconds per mutant
```

### Strategy: Use MULL Feedback

1. **Low score?** Some code paths aren't tested
2. **Check MULL report** for which mutants survived
3. **Write new tests** to kill those mutants
4. **Iterate** until score reaches 95%+

## Project Structure

Each project follows this layout:

```
projects/pid_controller/
├── CMakeLists.txt          # CMake build configuration
├── mull.yml               # MULL mutation testing config
├── src/
│   ├── pid.h             # Header (API contract)
│   └── pid.c             # Implementation (to fill in)
└── test/
    └── test_pid.c        # Unit tests using Unity
```

## Verification Tests

The workspace includes `tests/test_project_build.py` which verifies:

1. **Compilation** - Projects build with CMake + Clang
2. **Linking** - Test executables are created
3. **Execution** - Tests run without crashing

Run verification:

```bash
pytest tests/test_project_build.py -v
```

## Reference Implementations

Complete working implementations are provided in `reference_implementations.py` for:
- PID controller (with anti-windup)
- UART framing (with COBS + CRC-8)
- Example test suites

These can be used to verify the build infrastructure or as guidance for implementation.

## Installation Requirements

### Ubuntu/Debian

```bash
sudo apt-get install cmake clang libunity-dev
# For MULL mutation testing:
# https://mull.readthedocs.io/installation.html
```

### macOS

```bash
brew install cmake llvm libunity
```

### Windows

Use Windows Subsystem for Linux (WSL) with Ubuntu, or set up Visual Studio with MSVC.

## Common Tasks

### Generate Project from Skeleton

```python
from projects.pid_controller import SKELETON

for filename, content in SKELETON.items():
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)
```

### Build and Test Programmatically

```python
from build_utils import ProjectBuilder

builder = ProjectBuilder("projects/pid_controller")
builder.configure(compiler="clang")
builder.build()
builder.run_tests()
results = builder.run_mutation_tests()
print(f"Mutation score: {results['mutation_score']:.1%}")
```

## Next Steps

1. **Study the API** in the header files (pid.h, uart_frame.h)
2. **Write comprehensive tests** for edge cases
3. **Implement the functions** to pass tests
4. **Run MULL** to find test gaps
5. **Improve tests** until mutation score > 95%

## References

- **CMake**: https://cmake.org/
- **Clang**: https://clang.llvm.org/
- **Unity Testing**: https://github.com/ThrowTheSwitch/Unity
- **MULL**: https://mull.readthedocs.io/
- **COBS Encoding**: https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing
- **PID Control**: https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller
