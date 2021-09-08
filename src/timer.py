import time

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """start a new timer"""
        if self._start_time:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()

    def stop(self):
        if not self._start_time:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        return int(elapsed_time + 0.5)

if __name__ == '__main__':
    t = Timer()
    t.start()
    time.sleep(2)
    print(f"{t.stop()} sec has been elapsed")
