# CMake + Clang + MULL Setup Summary

This document summarizes the complete setup for template projects using CMake, Clang, and MULL mutation testing.

## What Changed

### Before
- Makefile-based builds
- Used `mutmut` for Python mutation testing
- Limited compiler control

### Now (CMake + Clang + MULL)
- ✅ CMake 3.10+ for standard C/C++ builds
- ✅ Clang compiler (explicitly specified)
- ✅ MULL for comprehensive C/C++ mutation testing
- ✅ Unity test framework for unit testing
- ✅ Automatic build verification tests

## File Changes

### Updated Project Definitions

**`projects/pid_controller/__init__.py`**
- Replaced Makefile skeleton with CMakeLists.txt
- Added mull.yml configuration
- Kept original API contract and spec

**`projects/uart_driver/__init__.py`**
- Replaced Makefile skeleton with CMakeLists.txt
- Added mull.yml configuration
- Kept original API contract and spec

### Updated Skills

**`skills/run_tests.py`**
- Now supports both CMake and Make-based projects
- Auto-detects CMakeLists.txt
- Calls `cmake configure -> build -> ctest` for CMake projects
- Falls back to `make test` for legacy projects

**`skills/run_mutation.py`**
- Completely rewritten for MULL (was mutmut)
- Auto-builds project before mutation testing
- Uses mull.yml configuration file
- Parses MULL output for mutation score

### New Files Created

**`BUILDING.md`** - Complete build and setup guide
- Installation instructions for all platforms
- Step-by-step build process
- CMake configuration details
- MULL usage and interpretation
- Troubleshooting section

**`TEMPLATE_PROJECTS.md`** - Project documentation
- Overview of PID controller and UART projects
- API specifications and requirements
- Test strategy and mutation score expectations
- Quick start examples

**`build_utils.py`** - Build infrastructure Python module
- `ProjectBuilder` class for CMake projects
- Helper functions for compilation verification
- Mutation testing invocation

**`reference_implementations.py`** - Example implementations
- Full PID controller implementation
- Full UART framing implementation
- Example test suites for both projects

**`tests/test_project_build.py`** - Automated verification tests
- Verifies projects compile with CMake + Clang
- Verifies test executables are created
- Verifies tests execute successfully

**`build.sh`** - Shell script for quick builds
- Convenience script for Linux/macOS
- Builds, tests, and optionally runs MULL

### Documentation Updates

**`README.md`**
- Added template projects section
- Updated project creation instructions
- Updated skills documentation to mention CMake/MULL

## Project Structure (New)

Each template project now has this structure:

```
projects/pid_controller/
├── CMakeLists.txt              # CMake 3.10+ config with Clang
├── mull.yml                    # MULL mutation testing config
├── src/
│   ├── pid.h                   # API header (unchanged)
│   └── pid.c                   # Implementation skeleton
└── test/
    └── test_pid.c              # Unity test skeleton
```

## Building a Project

### Manual Build (Linux/macOS)

```bash
cd projects/pid_controller
mkdir build
cd build
cmake .. -DCMAKE_C_COMPILER=clang
cmake --build .
ctest --verbose
```

### Script Build

```bash
cd projects/pid_controller
chmod +x ../../build.sh
../../build.sh pid_controller
```

### Programmatic Build

```python
from build_utils import ProjectBuilder

builder = ProjectBuilder("projects/pid_controller")
builder.configure(compiler="clang")
builder.build()
builder.run_tests()
```

### Within Skill Execution

The `run_tests` skill now handles CMake automatically:

```python
from skills import execute_skill

result = execute_skill("run_tests", {}, "projects/pid_controller")
# Returns: {"passed": bool, "output": str}
```

## Mutation Testing

### Run MULL Manually

```bash
cd projects/pid_controller
mull-runner -config mull.yml --log-level=info
```

### Run via Skill

```python
from skills import execute_skill
import json

result = execute_skill("run_mutation", {}, "projects/pid_controller")
data = json.loads(result)
# {
#   "mutation_score": 0.88,
#   "killed": 150,
#   "survived": 20,
#   "total": 170,
#   "surviving_mutant_info": "..."
# }
```

## Installation for Users

### Ubuntu/Debian

```bash
# Build tools
sudo apt-get install cmake clang build-essential

# Testing framework
sudo apt-get install libunity-dev

# Mutation testing (if using MULL)
# Follow: https://mull.readthedocs.io/installation.html
```

### macOS

```bash
brew install cmake llvm libunity
# For MULL: brew install mull (if available)
```

### Windows

- Use WSL (Windows Subsystem for Linux) with Ubuntu
- Or Visual Studio with MSVC (requires CMakeLists.txt adjustment)

## CMakeLists.txt Walkthrough

The generated CMakeLists.txt includes:

```cmake
cmake_minimum_required(VERSION 3.10)
project(pid_controller C)

# Use Clang explicitly
set(CMAKE_C_COMPILER clang)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -g -fPIC -m64")
set(CMAKE_C_STANDARD 99)

# Find Unity framework
find_package(PkgConfig REQUIRED)
pkg_check_modules(UNITY unity)

# Create implementation library
add_library(pid_lib src/pid.c)

# Create test executable
add_executable(test_pid test/test_pid.c)
target_link_libraries(test_pid pid_lib ${UNITY_LIBRARIES} m)

# Enable testing
enable_testing()
add_test(NAME pid_tests COMMAND test_pid)
```

## mull.yml Walkthrough

The mutation testing configuration:

```yaml
mutators:
  - cxx_eq_to_ne              # == → !=
  - cxx_add_to_sub            # + → -
  - cxx_lt_to_le              # < → <=
  # ... more operators

tests:
  - test_pid                  # Which executables to test

timeout: 5000                 # ms per mutant
```

## Verification

Run automated tests to verify setup:

```bash
pytest tests/test_project_build.py -v
```

This verifies:
- ✓ Projects compile with CMake + Clang
- ✓ Test executables are created
- ✓ Tests execute successfully

## Migration Path

If you have existing Make-based projects:

1. Existing projects continue to work (`run_tests` auto-detects Make vs CMake)
2. New template projects use CMake by default
3. Gradually migrate existing projects to CMake as needed

## Key Advantages

### CMake Benefits
- Universal C/C++ build standard
- Cross-platform support
- Works with MULL for mutation testing
- Version-controlled build specifications
- Easier for LLMs to understand and modify

### Clang Benefits
- Modern compiler with excellent diagnostics
- Native MULL support
- Open source and widely available
- Consistent behavior across platforms

### MULL Benefits (vs mutmut)
- Designed for compiled languages (C/C++)
- More sophisticated mutations
- Better integration with CMake
- Comprehensive mutation operators
- Detailed mutation reports

## Next Steps

1. **Install dependencies** - cmake, clang, libunity-dev
2. **Verify setup** - `pytest tests/test_project_build.py -v`
3. **Build a project** - `cd projects/pid_controller && mkdir build && cd build && cmake .. && cmake --build .`
4. **Run mutations** - `mull-runner -config ../mull.yml`
5. **Start developing** - Implement functions and write tests

## Reference

- CMakeLists.txt: [BUILDING.md](BUILDING.md) / [cmake.org](https://cmake.org/)
- MULL: [mull.readthedocs.io](https://mull.readthedocs.io/)
- Unity: [github.com/ThrowTheSwitch/Unity](https://github.com/ThrowTheSwitch/Unity)
- Clang: [clang.llvm.org](https://clang.llvm.org/)

## Troubleshooting

### CMake not found
```bash
# Ubuntu
sudo apt-get install cmake
# macOS
brew install cmake
```

### MULL not found
```
MULL is optional. To install: https://mull.readthedocs.io/
If not needed, run_mutation skill will indicate it's unavailable.
```

### Build fails with "clang not found"
```bash
# Ubuntu
sudo apt-get install clang
# macOS
brew install llvm
```

### Tests don't compile
1. Check Unity is installed: `pkg-config --cflags --libs unity`
2. Verify CMakeLists.txt links Unity: `target_link_libraries(test_xxx ... ${UNITY_LIBRARIES})`
3. Check test includes: `#include "unity.h"`
