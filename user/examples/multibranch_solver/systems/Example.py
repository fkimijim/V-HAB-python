class Example(vsys):
    """
    Example simulation for a fan-driven looped gas flow in Python.
    This simulation includes:
    - 5 tanks connected in a loop
    - Parallel flow paths with valve control
    - Fans and check valves to prevent backflow
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 100)

    def create_matter_structure(self):
        """
        Create the matter structure for the simulation.
        """
        super().create_matter_structure()

        # Create tanks and gas phases
        self.toStores = {}
        self.toStores['Tank_1'] = matter.store(self, 'Tank_1', 1)
        oGasPhase1 = self.toStores['Tank_1'].create_phase('air', 1)

        self.toStores['Tank_2'] = matter.store(self, 'Tank_2', 1)
        oGasPhase2 = self.toStores['Tank_2'].create_phase('air', 'flow', 1)

        self.toStores['Tank_3'] = matter.store(self, 'Tank_3', 1)
        oGasPhase3 = self.toStores['Tank_3'].create_phase('air', 'flow', 1)

        self.toStores['Tank_4'] = matter.store(self, 'Tank_4', 1)
        oGasPhase4 = self.toStores['Tank_4'].create_phase('air', 1)

        self.toStores['Tank_5'] = matter.store(self, 'Tank_5', 1)
        oGasPhase5 = self.toStores['Tank_5'].create_phase('air', 1)

        # Add fan
        oFan = components.matter.Fan(self, 'Fan', 57500)
        oFan.fPowerFactor = 0

        # Add pipes
        fRoughness = 2e-3
        components.matter.Pipe(self, 'Pipe_1', 1, 0.02, fRoughness)
        components.matter.Pipe(self, 'Pipe_2', 1, 0.02, fRoughness)
        components.matter.Pipe(self, 'Pipe_3', 1, 0.02, fRoughness)
        components.matter.Pipe(self, 'Pipe_4', 1, 0.02, fRoughness)
        components.matter.Pipe(self, 'Pipe_5', 1, 0.02, fRoughness)

        # Add valves and check valves
        components.matter.Valve(self, 'Valve_1', True)
        components.matter.Valve(self, 'Valve_2', False)
        components.matter.CheckValve(self, 'CheckValve_1')
        components.matter.CheckValve(self, 'CheckValve_2')

        # Create branches
        matter.Branch(self, oGasPhase1, ['Pipe_1'], oGasPhase2)
        matter.Branch(self, oGasPhase2, ['Fan'], oGasPhase3)

        # Parallel flow paths
        matter.Branch(self, oGasPhase3, ['Pipe_2', 'Valve_1'], oGasPhase4)
        matter.Branch(self, oGasPhase4, ['Pipe_3', 'CheckValve_1'], oGasPhase1)
        matter.Branch(self, oGasPhase3, ['Pipe_4', 'Valve_2'], oGasPhase5)
        matter.Branch(self, oGasPhase5, ['Pipe_5', 'CheckValve_2'], oGasPhase1)

    def create_solver_structure(self):
        """
        Create solver structure for the simulation.
        """
        super().create_solver_structure()

        # Set up multi-branch solver
        solver.matter_multibranch.IterativeBranch(self.aoBranches)

        # Set thermal solvers
        self.set_thermal_solvers()

    def exec(self, _):
        """
        Execute function for the system.
        Handles valve control logic based on simulation time.
        """
        super().exec(_)

        # Valve control logic
        if self.oTimer.fTime > 1200 and not self.toProcsF2F['Valve_1'].bOpen:
            self.toProcsF2F['Valve_1'].set_open(True)
            self.toProcsF2F['Valve_2'].set_open(True)
        elif self.oTimer.fTime > 600 and not self.toProcsF2F['Valve_2'].bOpen:
            self.toProcsF2F['Valve_1'].set_open(False)
            self.toProcsF2F['Valve_2'].set_open(True)
