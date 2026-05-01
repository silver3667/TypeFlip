"""Verify the singleton mutex actually prevents a second daemon process.

Spawns two child processes, each calling _acquire_singleton. The first
should succeed; the second should print the multi-instance message and
exit with code 2.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHILD_SCRIPT = textwrap.dedent(
    """
    import os, sys, time
    sys.path.insert(0, %r)
    from daemon.daemon import _acquire_singleton
    handle = _acquire_singleton()
    print('CHILD-ACQUIRED', flush=True)
    time.sleep(float(sys.argv[1]))
    """
).strip() % _root


def main() -> int:
    # Process A holds the mutex for 4 seconds.
    a = subprocess.Popen(
        [sys.executable, "-c", CHILD_SCRIPT, "4"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait for A to print CHILD-ACQUIRED so we know it has the mutex.
    deadline = time.time() + 5
    a_ready = False
    while time.time() < deadline:
        line = a.stdout.readline()
        if not line:
            time.sleep(0.05)
            continue
        if "CHILD-ACQUIRED" in line:
            a_ready = True
            break
    if not a_ready:
        a.kill()
        print("FAIL: process A never acquired mutex")
        return 1

    # Process B should fail to acquire (exit code 2) while A is still alive.
    b = subprocess.run(
        [sys.executable, "-c", CHILD_SCRIPT, "0.1"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    print("--- Process B output ---")
    print(b.stdout.strip())
    print(f"Process B exit code: {b.returncode}")

    # Wait for A to finish.
    a.wait(timeout=10)

    # Now process C should be able to acquire (mutex released when A exited).
    c = subprocess.run(
        [sys.executable, "-c", CHILD_SCRIPT, "0.1"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    print("--- Process C output (after A exited) ---")
    print(c.stdout.strip())
    print(f"Process C exit code: {c.returncode}")

    b_blocked = b.returncode == 2 and "ANOTHER DAEMON" in b.stdout
    c_acquired = c.returncode == 0 and "CHILD-ACQUIRED" in c.stdout
    print()
    print(f"[{'OK ' if b_blocked else 'FAIL'}] B was blocked by singleton")
    print(f"[{'OK ' if c_acquired else 'FAIL'}] C acquired after A exited (no stale lock)")
    return 0 if (b_blocked and c_acquired) else 1


if __name__ == "__main__":
    raise SystemExit(main())
