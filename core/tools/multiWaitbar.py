import time
import threading
from queue import Queue
import tkinter as tk
from tkinter import ttk

class MultiWaitbar:
    """
    MultiWaitbar: Manages multiple progress bars in a single window.
    """

    def __init__(self):
        self.root = None
        self.bars = {}
        self.lock = threading.Lock()
        self.update_queue = Queue()
        self.timer = None
        self.timer_interval = 0.02

    def _initialize_window(self):
        if self.root is None:
            self.root = tk.Tk()
            self.root.title("Progress")
            self.root.geometry("400x200")
            self.root.protocol("WM_DELETE_WINDOW", self.close_all)

    def add_or_update_bar(self, label, value=0, **kwargs):
        with self.lock:
            self._initialize_window()

            if label not in self.bars:
                # Add a new bar
                frame = ttk.Frame(self.root)
                frame.pack(fill=tk.X, pady=5, padx=10)

                label_widget = ttk.Label(frame, text=label, width=20, anchor="w")
                label_widget.pack(side=tk.LEFT, padx=(0, 10))

                progress_var = tk.DoubleVar(value=value * 100)
                progress_bar = ttk.Progressbar(
                    frame, variable=progress_var, maximum=100, length=200
                )
                progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

                cancel_button = ttk.Button(frame, text="X", command=lambda: self.cancel_bar(label))
                cancel_button.pack(side=tk.LEFT, padx=(10, 0))

                self.bars[label] = {
                    "frame": frame,
                    "label": label_widget,
                    "progress_var": progress_var,
                    "progress_bar": progress_bar,
                    "cancel_button": cancel_button,
                    "cancelled": False,
                    "start_time": time.time(),
                }
            else:
                # Update an existing bar
                bar = self.bars[label]
                bar["progress_var"].set(value * 100)

            # Handle optional parameters
            if "color" in kwargs:
                color = kwargs["color"]
                # Convert RGB to hex if necessary
                if isinstance(color, (tuple, list)):
                    color = "#{:02x}{:02x}{:02x}".format(
                        int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
                    )
                bar["progress_bar"].config(style=f"{label}.Horizontal.TProgressbar")
                style = ttk.Style(self.root)
                style.configure(f"{label}.Horizontal.TProgressbar", troughcolor=color)

            if "reset" in kwargs and kwargs["reset"]:
                self.bars[label]["start_time"] = time.time()

            self._start_timer()

    def increment_bar(self, label, increment):
        if label in self.bars:
            current_value = self.bars[label]["progress_var"].get() / 100
            self.add_or_update_bar(label, value=current_value + increment)

    def cancel_bar(self, label):
        if label in self.bars:
            self.bars[label]["cancelled"] = True

    def is_cancelled(self, label):
        if label in self.bars:
            return self.bars[label]["cancelled"]
        return False

    def close_bar(self, label):
        with self.lock:
            if label in self.bars:
                bar = self.bars[label]
                bar["frame"].destroy()
                del self.bars[label]
                if not self.bars:  # Close the window if no bars are left
                    self.close_all()

    def close_all(self):
        with self.lock:
            if self.root:
                self.root.destroy()
                self.root = None
                self.bars = {}

    def _start_timer(self):
        if self.timer is None:
            self.timer = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer.start()

    def _timer_loop(self):
        while True:
            time.sleep(self.timer_interval)
            self.root.update_idletasks()
            self.root.update()

    def show(self):
        if self.root:
            self.root.mainloop()

# Example Usage
if __name__ == "__main__":
    multi_waitbar = MultiWaitbar()
    multi_waitbar.add_or_update_bar("Task 1", 0.1, color="blue")
    multi_waitbar.add_or_update_bar("Task 2", 0.5, color=(0.8, 0.0, 0.1))
    multi_waitbar.add_or_update_bar("Task 3", 0.9, color="green")

    # Simulate a loop to increment bars
    for i in range(10):
        time.sleep(1)
        multi_waitbar.increment_bar("Task 1", 0.1)
        multi_waitbar.increment_bar("Task 2", 0.05)
        if multi_waitbar.is_cancelled("Task 3"):
            print("Task 3 cancelled!")
            break

    multi_waitbar.close_all()
