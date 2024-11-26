class ThermalObserver:
    """
    A simple observer to count and report thermal components (branches and capacities)
    in a simulation model.
    """

    def __init__(self, simulation):
        """
        Initialize the ThermalObserver.

        Args:
            simulation (object): Reference to the simulation infrastructure.
        """
        self.simulation = simulation
        simulation.bind("init_post", self.on_init_post)

    def on_init_post(self):
        """
        Executes after the simulation initialization to count and report
        thermal branches and capacities.
        """
        root_system = self.simulation.root_system
        capacities, branches = self.count_capacities_and_branches(root_system)

        # Determine singular/plural forms for output
        branch_plural = "" if branches == 1 else "es"
        capacity_plural = "y" if capacities == 1 else "ies"

        print(f"Model contains {branches} Thermal Branch{branch_plural} and {capacities} Capacit{capacity_plural}.")

    def count_capacities_and_branches(self, system):
        """
        Recursively counts thermal branches and capacities in the system.

        Args:
            system (object): The current system to analyze.

        Returns:
            tuple: Total capacities and branches in the system.
        """
        capacities = system.thermal_capacities
        branches = system.thermal_branches

        # Recursively count components in subsystems
        for child in system.children:
            child_capacities, child_branches = self.count_capacities_and_branches(child)
            capacities += child_capacities
            branches += child_branches

        return capacities, branches
