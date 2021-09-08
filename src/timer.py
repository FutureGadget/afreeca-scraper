import time

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None

    @classmethod
    def threshold(self, threshold):
        self._start_time = None
        self._threshold = threshold
        return self()

    def increase_threshold(self):
        self._threshold = self._threshold * 1.3

    def increase_threshold_and_reset(self):
        self._threshold = self._threshold * 1.3
        self._start_time = time.perf_counter()

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

    def elapsed(self):
        if not self._start_time:
            raise TimerError(f"Timer is not running. Use .start() to start it")
        elapsed_time = time.perf_counter() - self._start_time
        return int(elapsed_time + 0.5)
    
    def is_over_due(self):
        if not self._start_time:
            raise TimerError(f"Timer is not running. Use .start() to start it")
        if self.elapsed() >= self._threshold:
            return True
        else:
            return False

    def reset(self):
        self._start_time = time.perf_counter()

if __name__ == '__main__':
    t = Timer.threshold(4)
    t.increase_threshold()
    t.start()
    time.sleep(4)
    assert t.is_over_due() == False
