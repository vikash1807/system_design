## Python Concurrency & Asyncio — Quick Reference

----------

### 1. Concurrency vs Parallelism

Concurrency:
- Multiple tasks make progress during the same period.
- They do NOT have to execute at the exact same time.

Parallelism:
- Multiple tasks execute at the exact same time, usually on different CPU cores.

Simple idea:
Concurrency = dealing with multiple tasks.
Parallelism = executing multiple tasks simultaneously.


### 2. Process

A process is a running instance of a program.
- Has its own memory/address space.
- Can contain multiple threads.


### 3. Thread

A thread is an execution path inside a process.
- Threads in the same process share memory.
- Threading provides concurrency.
- In traditional CPython, the GIL limits parallel execution of Python bytecode.
- Threads can still run native/GIL-releasing work in parallel.

Use threading commonly for:
- Blocking I/O
- Existing synchronous libraries
- Work that can benefit from multiple threads


### 4. asyncio

asyncio is Python's asynchronous concurrency framework.
It mainly uses:
- Event loop
- Coroutines
- asyncio Tasks
- await

Usually, many asyncio Tasks run on one OS thread.


### 5. Coroutine

Defined using:

    async def fetch_data():
        ...

Calling it:

    coro = fetch_data()

creates a coroutine object.

A coroutine can pause and resume at await points.

------------

###  6. await

await means:
"Pause this coroutine and give control back to the event loop until the awaited operation is ready."

Example:

    data = await fetch_data()

This allows other asyncio Tasks to run while waiting.

------------

###  7. asyncio.create_task()

create_task() does NOT create a thread.

It schedules a coroutine as an asyncio Task:

    task = asyncio.create_task(fetch_data())

Mental model:

    Event Loop
      ├── Task A
      ├── Task B
      └── Task C

Tasks usually run on the same OS thread and are scheduled cooperatively.


### 8. Blocking vs Non-blocking

Bad inside an asyncio event loop:

    time.sleep(5)

It blocks the event-loop thread.

Use:

    await asyncio.sleep(5)

This lets other Tasks run.

------------

### 10. Locks

threading.Lock:
- Protects shared state between threads.

    with lock:
        shared_state += 1

asyncio.Lock:
- Protects shared state between asyncio Tasks.

    async with lock:
        shared_state += 1

Important:
Single-threaded asyncio can STILL have race conditions.


### 11. Race Conditions

A race condition occurs when the result depends on the timing/interleaving
of concurrent operations.

Example:
    read value
    modify value
    write value

Two concurrent operations can interleave and overwrite each other's work.


### 12. Task vs Coroutine vs Future

Coroutine:
- Async work that can be suspended/resumed.

Task:
- A coroutine scheduled on the event loop.

Future:
- A placeholder for a result that will be available later.
- A Task is Future-like and wraps a coroutine.
