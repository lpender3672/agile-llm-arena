# Quick Reference: CMake + Clang + MULL Setup

## Installation (Ubuntu/Debian)

```bash
sudo apt-get install cmake clang build-essential libunity-dev
# For MULL (mutation testing): see https://mull.readthedocs.io/
```

## Installation (macOS)

```bash
brew install cmake llvm libunity
```

## Build a Project

```bash
cd projects/pid_controller
mkdir build && cd build
cmake .. -DCMAKE_C_COMPILER=clang
cmake --build .
ctest --verbose
```

## Run Mutation Tests

```bash
cd projects/pid_controller
mull-runner -config mull.yml --log-level=info
```

## Verify Setup

```bash
pytest tests/test_project_build.py -v
```

## Python API

### Build Programmatically

```python
from build_utils import ProjectBuilder

builder = ProjectBuilder("projects/pid_controller")
builder.configure(compiler="clang")
builder.build()
builder.run_tests()
```

### Run Mutation Tests (Python)

```python
from skills import execute_skill
import json

result = execute_skill("run_mutation", {}, "projects/pid_controller")
print(json.loads(result))
# {"mutation_score": 0.88, "killed": 150, "survived": 20, ...}
```

### Run Tests (Python)

```python
from skills import execute_skill
import json

result = execute_skill("run_tests", {}, "projects/pid_controller")
print(json.loads(result))
# {"passed": true, "output": "..."}
```

## Project Structure

```
projects/<name>/
├── CMakeLists.txt              # Build configuration
├── mull.yml                    # Mutation testing config
├── src/
│   ├── module.h               # API header
│   └── module.c               # Implementation
└── test/
    └── test_module.c          # Tests (Unity framework)
```

## CMakeLists.txt Template

```cmake
cmake_minimum_required(VERSION 3.10)
project(my_project C)

set(CMAKE_C_COMPILER clang)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -g -fPIC -m64")
set(CMAKE_C_STANDARD 99)

# Find Unity
find_package(PkgConfig REQUIRED)
pkg_check_modules(UNITY unity)

include_directories(src ${UNITY_INCLUDE_DIRS})

# Library
add_library(mylib src/module.c)

# Test executable
add_executable(test_module test/test_module.c)
target_link_libraries(test_module mylib ${UNITY_LIBRARIES} m)

# Testing
enable_testing()
add_test(NAME module_tests COMMAND test_module)
```

## mull.yml Template

```yaml
mutators:
  - cxx_eq_to_ne
  - cxx_add_to_sub
  - cxx_lt_to_le
  - cxx_le_to_lt

tests:
  - test_module

timeout: 5000
```

## Test Writing (Unity)

```c
#include "unity.h"
#include "../src/module.h"

void setUp(void) {
    // Before each test
}

void tearDown(void) {
    // After each test
}

void test_feature(void) {
    // Arrange
    int result = my_function(5);
    
    // Assert
    TEST_ASSERT_EQUAL_INT(10, result);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_feature);
    return UNITY_END();
}
```

## Common Assertions

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
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)
```

## Mutation Score Interpretation

- **Score = Killed / (Killed + Survived)**
- **90%+** = Excellent test coverage
- **80-90%** = Good coverage, some gaps
- **<80%** = Gaps in test coverage

## Debug CMake Build

```bash
cd build
cmake .. -DCMAKE_C_COMPILER=clang --debug-output
cmake --build . --verbose
```

## Clean Build

```bash
cd projects/my_project
rm -rf build
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `cmake: command not found` | Install: `apt-get install cmake` |
| `clang: command not found` | Install: `apt-get install clang` |
| `unity.h: No such file` | Install: `apt-get install libunity-dev` |
| `mull-runner: command not found` | Optional tool; see mull.readthedocs.io |
| Test fails to link | Check `target_link_libraries` in CMakeLists.txt |
| CMake can't find packages | Run: `pkg-config --list-all \| grep unity` |

## Documentation References

- **Full Build Guide**: [BUILDING.md](BUILDING.md)
- **Project Details**: [TEMPLATE_PROJECTS.md](TEMPLATE_PROJECTS.md)
- **Setup Summary**: [CMAKE_SETUP.md](CMAKE_SETUP.md)
- **CMake**: https://cmake.org/
- **MULL**: https://mull.readthedocs.io/
- **Unity**: https://github.com/ThrowTheSwitch/Unity
- **Clang**: https://clang.llvm.org/
