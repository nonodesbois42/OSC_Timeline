import time


class Chronometer:
    """
    Simple class that runs a chronometer.
    The chronometer can start, pause and stop.

    To retrieve the elapsed time of the chronometer you have two options:
    - get_elapsed_time      returns msec
    - to_string             returns string format HH:MM:SS.SSS
    """

    def __init__(self):
        self.start_time = None  # Stores the start time of the chronometer
        self.elapsed_time = 0  # Stores the elapsed time in seconds
        self.is_running = (
            False  # Indicates whether the chronometer is running or paused
        )

    def start(self):
        """
        Starts the chronometer by setting the start time and updating the running state.
        """
        if not self.is_running:
            self.start_time = time.perf_counter()
            self.is_running = True

    def pause(self):
        """
        Pauses the chronometer by updating the elapsed time and setting the running state to False.
        """
        if self.is_running:
            self.elapsed_time += time.perf_counter() - self.start_time
            self.is_running = False

    def stop(self):
        """
        Stops the chronometer by updating the elapsed time and setting the running state to False.
        """
        if self.is_running:
            self.elapsed_time += time.perf_counter() - self.start_time
            self.is_running = False

    def reset(self):
        """
        Resets the elapsed time to 0.
        """
        self.elapsed_time = 0

    def get_elapsed_time(self):
        """
        Returns the elapsed time in seconds.
        If the chronometer is running, adds the current time difference to the elapsed time.
        """
        if self.is_running:
            elapsed = self.elapsed_time + (time.perf_counter() - self.start_time)
        else:
            elapsed = self.elapsed_time

        return elapsed

    def to_string(self):
        """
        Returns the formatted string representation of the elapsed time in the format "hh:mm:ss.sss".
        """
        return Chronometer.format_msec(self.get_elapsed_time())

    @classmethod
    def format_msec(clc, elapsed: int):
        """
        Returns the formatted string representation of the elapsed time in the format "hh:mm:ss.sss".
        Accepts the elapsed time in msec as an argument.
        """
        # Calculate hours, minutes, seconds, and milliseconds
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed % 1) * 1000)

        # Format the time as a string
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        return time_str


# timer = Chronometer()
# timer.start()

# # Let the timer run for a while...
# time.sleep(5)

# timer.pause()

# # Get the elapsed time in the desired format
# elapsed_time = timer.to_string()
# print(f"Elapsed time: {elapsed_time}")

# # Resume the timer
# timer.start()

# # Let the timer run again...
# time.sleep(3)

# timer.stop()

# elapsed_time = timer.to_string()
# print(f"Elapsed time: {elapsed_time}")
