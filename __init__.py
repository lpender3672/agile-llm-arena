"""Ring buffer benchmark project definition."""

SPEC = {
    "name": "Ring Buffer",
    "module": "ring_buffer",
    "description": "A fixed-size circular buffer for embedded use (no dynamic allocation).",
    "spec": """
Implement a thread-safe (interrupt-safe) ring buffer in C.

API (defined in ring_buffer.h):

  typedef struct {
      uint8_t  *buf;
      uint16_t  capacity;  // max items
      uint16_t  head;
      uint16_t  tail;
      uint16_t  count;
  } RingBuffer;

  void     rb_init(RingBuffer *rb, uint8_t *storage, uint16_t capacity);
  bool     rb_push(RingBuffer *rb, uint8_t byte);   // returns false if full
  bool     rb_pop(RingBuffer *rb, uint8_t *out);    // returns false if empty
  bool     rb_peek(RingBuffer *rb, uint8_t *out);   // peek without consuming
  uint16_t rb_count(RingBuffer *rb);
  bool     rb_full(RingBuffer *rb);
  bool     rb_empty(RingBuffer *rb);
  void     rb_clear(RingBuffer *rb);

Constraints:
- No malloc. Storage array passed in by caller.
- Capacity of 1 must work correctly.
- Push to full buffer must return false without modifying state.
- Pop from empty buffer must return false without modifying out.
""",
}

# Skeleton files written to sandbox before the model runs
SKELETON = {
    "src/ring_buffer.h": """\
#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t  *buf;
    uint16_t  capacity;
    uint16_t  head;
    uint16_t  tail;
    uint16_t  count;
} RingBuffer;

void     rb_init(RingBuffer *rb, uint8_t *storage, uint16_t capacity);
bool     rb_push(RingBuffer *rb, uint8_t byte);
bool     rb_pop(RingBuffer *rb, uint8_t *out);
bool     rb_peek(RingBuffer *rb, uint8_t *out);
uint16_t rb_count(RingBuffer *rb);
bool     rb_full(RingBuffer *rb);
bool     rb_empty(RingBuffer *rb);
void     rb_clear(RingBuffer *rb);
""",
    "src/ring_buffer.c": """\
#include "ring_buffer.h"

/* TODO: implement */
""",
    "test/test_ring_buffer.c": """\
#include "unity.h"
#include "../src/ring_buffer.h"

void setUp(void) {}
void tearDown(void) {}

/* TODO: write tests */

int main(void) {
    UNITY_BEGIN();
    /* RUN_TEST(...); */
    return UNITY_END();
}
""",
    "Makefile": """\
CC      = gcc
CFLAGS  = -Wall -Wextra -g -Isrc -Itest/unity
UNITY   = test/unity/unity.c

test: test/test_ring_buffer
\t./test/test_ring_buffer

test/test_ring_buffer: src/ring_buffer.c test/test_ring_buffer.c $(UNITY)
\t$(CC) $(CFLAGS) $^ -o $@

.PHONY: test
""",
}

FILE_TREE = "\n".join(f"  {k}" for k in SKELETON)
