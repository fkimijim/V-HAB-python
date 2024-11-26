class TimestepObserver:
    """
    A monitor to track and log the smallest time steps in a simulation.
    """

    def __init__(self, simulation, reporting_limit=0, history_ticks=100):
        """
        Initialize the TimestepObserver.

        Args:
            simulation (object): Reference to the simulation infrastructure.
            reporting_limit (float): Minimum time step limit for reporting.
            history_ticks (int): Number of ticks to keep in the debug history.
        """
        self.simulation = simulation
        self.reporting_limit = reporting_limit
        self.history_ticks = history_ticks
        self.debug_history = []  # Stores recent time step information
        self.timer = None  # Will hold a reference to the simulation's timer
        self.simulation.bind("step_post", self.on_step_post)

    def on_step_post(self):
        """
        Executes after each simulation step to track the smallest time step.
        """
        if self.timer is None:
            # Initialize the timer reference during the first call
            self.timer = self.simulation.timer

        # Find the smallest non-negative time step
        time_steps = [step for step in self.timer.time_steps if step >= 0]
        min_step = min(time_steps)
        min_indices = [i for i, step in enumerate(self.timer.time_steps) if step == min_step]

        reports = []
        for idx in min_indices:
            callback = self.timer.callbacks[idx]
            caller = callback.owner  # Assuming callbacks have an `owner` attribute

            if hasattr(caller, "name"):
                reports.append(
                    f"{caller.name} used a minimal time step of {min_step:.6f} seconds "
                    f"in simulation tick {self.timer.tick}."
                )
            else:
                reports.append(
                    f"An unnamed entity used a minimal time step of {min_step:.6f} seconds "
                    f"in simulation tick {self.timer.tick}."
                )

        # Print reports if the time step is below the reporting limit
        if self.reporting_limit > 0 and min_step < self.reporting_limit:
            for report in reports:
                print(report)

        # Add to debug history (circular buffer)
        if len(self.debug_history) >= self.history_ticks:
            self.debug_history.pop(0)  # Remove oldest entry
        self.debug_history.append({
            "tick": self.timer.tick,
            "time_step": min_step,
            "reports": reports,
        })

    def find_smallest_time_step(self):
        """
        Find and display the smallest time step from the debug history.
        """
        if not self.debug_history:
            print("No data available.")
            return

        smallest = min(self.debug_history, key=lambda entry: entry["time_step"])
        print(f"Smallest time step: {smallest['time_step']:.6f} seconds")
        for report in smallest["reports"]:
            print(report)
