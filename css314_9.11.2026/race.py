import threading
import time

counter = 0


def increment():
    global counter

    for _ in range(1_000_000):
        # Separate the read and write to expose the race
        value = counter
        time.sleep(0)
        counter = value + 1


for run in range(1, 11):
    counter = 0

    threads = []

    for _ in range(10):
        t = threading.Thread(target=increment)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    error = 10_000_000 - counter

    print(
        f"Run #{run}: "
        f"Actual = {counter}, "
        f"Error = {error}"
    )