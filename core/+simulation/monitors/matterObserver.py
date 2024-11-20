class MatterObserver:
    """
    Tracks and logs mass balance and mass loss in a simulation system.
    """

    def __init__(self, simulation, mass_log_interval=100, verbose=True):
        """
        Initialize the MatterObserver.

        Args:
            simulation (object): Reference to the simulation infrastructure.
            mass_log_interval (int): Interval for logging mass data.
            verbose (bool): Enables detailed logging.
        """
        self.simulation = simulation
        self.mass_log_interval = mass_log_interval
        self.verbose = verbose

        # Initialize logging arrays
        self.total_mass_log = []
        self.generated_mass_log = []

        # References to system components
        self.phases = []
        self.branches = []
        self.flows = []

        # Final mass balance statistics
        self.generated_mass = 0
        self.total_mass_balance = 0

        # Bind to simulation events
        simulation.bind("step_post", self.on_step_post)
        simulation.bind("init_post", self.on_init_post)
        simulation.bind("finish", self.display_matter_balance)
        simulation.bind("pause", self.display_matter_balance)

    def on_step_post(self):
        """
        Logs mass data periodically during the simulation.
        """
        timer = self.simulation.timer
        if timer.tick % self.mass_log_interval == 0:
            # Calculate total and generated mass
            total_mass = sum(phase.mass for phase in self.phases if not phase.is_boundary)
            generated_mass = sum(phase.generated_mass for phase in self.phases)

            # Log mass data
            self.total_mass_log.append(total_mass)
            self.generated_mass_log.append(generated_mass)

    def on_init_post(self):
        """
        Gathers references to all phases and branches after initialization.
        """
        root_system = self.simulation.root_system
        self.phases, self.branches = self.collect_phases_and_branches(root_system)
        self.flows = [flow for branch in self.branches for flow in branch.flows]

        print(f"Model contains {len(self.branches)} branches and {len(self.phases)} phases.")

    def collect_phases_and_branches(self, system, phases=None, branches=None):
        """
        Recursively collects phases and branches from the system.

        Args:
            system (object): Current system being inspected.
            phases (list): Accumulated phases.
            branches (list): Accumulated branches.

        Returns:
            tuple: Updated lists of phases and branches.
        """
        if phases is None:
            phases = []
        if branches is None:
            branches = []

        # Collect phases and branches from the current system
        phases.extend(system.phases)
        branches.extend(system.branches)

        # Recursively collect from child systems
        for child in system.children:
            self.collect_phases_and_branches(child, phases, branches)

        return phases, branches

    def display_matter_balance(self, event=None):
        """
        Calculates and displays the overall mass balance and mass loss.
        """
        total_mass_start = self.total_mass_log[0] if self.total_mass_log else 0
        total_mass_end = self.total_mass_log[-1] if self.total_mass_log else 0
        self.generated_mass = sum(self.generated_mass_log)
        self.total_mass_balance = total_mass_end - total_mass_start

        print("+----------------------- MATTER BALANCE -----------------------+")
        print(f"| Generated Mass: {self.generated_mass:.2f} kg")
        print(f"| Total Mass Balance: {self.total_mass_balance:.2f} kg")
        if self.verbose:
            print("| Generated mass refers to corrections for exceeded phase mass.")
            print("| Mass balance shows the net difference between start and end.")
        print("+-------------------------------------------------------------+")
