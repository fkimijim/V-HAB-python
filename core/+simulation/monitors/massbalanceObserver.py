class MassBalanceObserver:
    """
    Tracks mass transfers and identifies mass balance errors in a simulation.
    """

    def __init__(self, simulation, accuracy=0, max_mass_diff=float("inf"), set_breakpoints=False):
        """
        Initialize the MassBalanceObserver.

        Args:
            simulation (object): Reference to the simulation infrastructure.
            accuracy (float): Minimum mass balance error to report.
            max_mass_diff (float): Maximum allowable mass difference before stopping the simulation.
            set_breakpoints (bool): Whether to set breakpoints on errors.
        """
        self.simulation = simulation
        self.accuracy = accuracy
        self.max_mass_diff = max_mass_diff
        self.set_breakpoints = set_breakpoints
        self.mass_error_helper = []

        # Bind to simulation step events
        simulation.bind("step_post", self.on_step_post)

    def on_step_post(self):
        """
        Performs mass balance checks after each simulation step.
        """
        timer = self.simulation.timer
        phases = self.simulation.matter_observer.phases
        flows = self.simulation.matter_observer.flows
        time_step = timer.calculate_next_time_step()

        # Check flows for balance
        for flow in flows:
            in_flow = flow.in_terminal
            out_flow = flow.out_terminal

            mass_balance_errors = (
                in_flow.sign * in_flow.flow_rate * in_flow.partial_mass
                + out_flow.sign * out_flow.flow_rate * out_flow.partial_mass
            )

            if abs(sum(in_flow.partial_mass) - 1) > self.accuracy:
                self.report_flow_error(in_flow, out_flow)

            if any(abs(mass_balance_errors) > self.accuracy):
                self.report_balance_issue(flow, mass_balance_errors)

        # Check phases for manipulator effects
        for phase in phases:
            manipulator = phase.manipulator
            if manipulator:
                self.check_manipulator(phase, manipulator)

        # Check total mass balance
        total_mass_error = self.calculate_total_mass_error(phases)
        if total_mass_error > self.max_mass_diff:
            print(f"Mass balance exceeded: {total_mass_error}")
            if self.set_breakpoints:
                breakpoint()

    def report_flow_error(self, in_flow, out_flow):
        """
        Reports partial mass vector errors in flows.
        """
        print(
            f"Mass vector error between {in_flow.phase.name} and {out_flow.phase.name} "
            f"in flow {in_flow.flow.name or 'Unnamed Flow'}."
        )

    def report_balance_issue(self, flow, mass_balance_errors):
        """
        Reports a specific mass balance issue in a flow.
        """
        substances = self.simulation.matter_table.substances
        errors = [
            f"{substances[i]}: {mass_balance_errors[i]:.4e} kg/s"
            for i in range(len(substances))
            if abs(mass_balance_errors[i]) > self.accuracy
        ]
        print(f"Mass balance error in flow {flow.name}: {', '.join(errors)}")

    def check_manipulator(self, phase, manipulator):
        """
        Checks for manipulator-induced mass balance errors in a phase.
        """
        error = sum(manipulator.partial_flows)
        if abs(error) > self.accuracy:
            print(
                f"Manipulator {manipulator.name} in phase {phase.name} caused "
                f"mass error: {error:.4e} kg/s"
            )

    def calculate_total_mass_error(self, phases):
        """
        Calculates the total mass balance error across all phases.
        """
        total_initial_mass = sum(phase.initial_mass for phase in phases)
        total_current_mass = sum(phase.current_mass for phase in phases)
        return abs(total_initial_mass - total_current_mass)
