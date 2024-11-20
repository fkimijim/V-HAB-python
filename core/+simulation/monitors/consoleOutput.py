class ConsoleOutput:
    """
    ConsoleOutput class replicates the functionality of providing detailed
    command-line logging for a simulation framework. It includes reporting intervals,
    debug message filtering, and support for verbosity levels.
    """

    def __init__(self, simulation_infrastructure, major_interval=100, minor_interval=10):
        """
        Initializes the ConsoleOutput instance.

        Args:
            simulation_infrastructure (object): Reference to the simulation infrastructure.
            major_interval (int): Major reporting interval in ticks.
            minor_interval (int): Minor reporting interval in ticks.
        """
        self.simulation_infrastructure = simulation_infrastructure
        self.major_interval = major_interval
        self.minor_interval = minor_interval

        self.last_tick_display = 0
        self.last_out_object_uuid = ""
        self.min_level = 1
        self.max_verbosity = 1
        self.debug_filters = {
            "types": [],
            "identifiers": [],
            "methods": [],
            "uuids": [],
            "paths": []
        }

        # Bind simulation events to methods
        simulation_infrastructure.bind("init_post", self.on_init_post)
        simulation_infrastructure.bind("step_post", self.on_step_post)
        simulation_infrastructure.bind("pause", self.on_pause)
        simulation_infrastructure.bind("finish", self.on_finish)
        simulation_infrastructure.bind("run", self.on_run)

    def on_init_post(self):
        """Called after simulation initialization."""
        print("Initialization complete!")

    def on_step_post(self):
        """Prints simulation progress at defined intervals."""
        timer = self.simulation_infrastructure.timer
        tick = timer.current_tick
        time = timer.current_time

        # Minor interval check
        if self.minor_interval > 0 and tick % self.minor_interval == 0 and time > 0:
            print(".", end="", flush=True)

        # Major interval check
        if tick % self.major_interval == 0:
            delta_time = time - self.last_tick_display
            self.last_tick_display = time
            print(f"\nTick: {tick}, Time: {time:.2f}s, Delta: {delta_time:.2f}s")

    def on_pause(self):
        """Prints simulation statistics when paused."""
        print("\n+-- SIMULATION PAUSED --+")
        self.print_simulation_statistics()

    def on_finish(self):
        """Prints simulation statistics when finished."""
        print("\n+-- SIMULATION COMPLETED --+")
        self.print_simulation_statistics()

    def on_run(self):
        """Called when the simulation starts."""
        print("Simulation running...")

    def print_simulation_statistics(self):
        """Gathers and prints simulation statistics."""
        timer = self.simulation_infrastructure.timer
        sim_time = timer.current_time
        tick = timer.current_tick
        print(f"Sim Time: {sim_time:.2f}s in {tick} ticks")
        print(f"Avg Time/Tick: {sim_time / tick:.4f}s" if tick > 0 else "N/A")

    # Debugging Filters
    def set_min_level(self, level):
        """Sets the minimum level for debug output."""
        self.min_level = level

    def set_max_verbosity(self, verbosity):
        """Sets the maximum verbosity for debug output."""
        self.max_verbosity = verbosity

    def add_debug_filter(self, filter_type, value):
        """Adds a debug filter by type."""
        if filter_type in self.debug_filters:
            self.debug_filters[filter_type].append(value)

    def remove_debug_filter(self, filter_type, value):
        """Removes a debug filter by type."""
        if filter_type in self.debug_filters:
            self.debug_filters[filter_type].remove(value)

    def reset_debug_filters(self, filter_type=None):
        """Resets all or specific debug filters."""
        if filter_type:
            self.debug_filters[filter_type] = []
        else:
            for key in self.debug_filters:
                self.debug_filters[key] = []
