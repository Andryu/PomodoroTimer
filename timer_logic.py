import time
import threading

class PomodoroTimer:
    def __init__(self, update_callback, on_complete_callback, work_minutes=25, break_minutes=5):
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60
        self.current_duration = self.work_duration
        self.time_left = self.current_duration
        self.is_running = False
        self.mode = "Work"  # Work or Break
        self.update_callback = update_callback
        self.on_complete_callback = on_complete_callback
        self._timer_thread = None
        self._stop_event = threading.Event()

    def set_duration(self, work_minutes, break_minutes):
        old_work = self.work_duration
        old_break = self.break_duration
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60

        # If not running, assume we want to apply changes immediately to current state if applicable
        if not self.is_running:
            if self.mode == "Work":
                 # If we were at the start of a session, reset fully.
                 # If we were paused mid-way, maybe we shouldn't jump?
                 # For simplicity, if modifying settings, we reset the timer to the new duration for the current mode.
                 self.current_duration = self.work_duration
            else:
                 self.current_duration = self.break_duration
            self.time_left = self.current_duration
            self.update_callback(self.format_time(self.time_left))

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._stop_event.clear()
            self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self._timer_thread.start()

    def pause(self):
        self.is_running = False
        self._stop_event.set()

    def reset(self):
        self.pause()
        self.time_left = self.current_duration
        self.update_callback(self.format_time(self.time_left))

    def switch_mode(self):
        self.pause()
        if self.mode == "Work":
            self.mode = "Break"
            self.current_duration = self.break_duration
        else:
            self.mode = "Work"
            self.current_duration = self.work_duration
        self.time_left = self.current_duration
        self.update_callback(self.format_time(self.time_left))
        return self.mode

    def _run_timer(self):
        while self.is_running and self.time_left > 0 and not self._stop_event.is_set():
            time.sleep(1)
            if self.is_running: # Check again
                self.time_left -= 1
                self.update_callback(self.format_time(self.time_left))

        if self.time_left == 0 and self.is_running:
            self.is_running = False
            self.on_complete_callback()

    @staticmethod
    def format_time(seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02}:{secs:02}"
