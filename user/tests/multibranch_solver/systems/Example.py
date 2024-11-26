class Example(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0
    Two tanks filled with gas at different pressures and a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.
        """
        super().__init__(oParent, sName, 100)

        # Properties
        self.fPipeLength = 0.5
        self.fPipeDiameter = 0.01  # for 3/5 mm overflow of warnings
        self.oManual = None

        # Execute configuration code
        eval(self.oRoot.oCfgParams.configCode(self))

    def create_matter_structure(self):
        """
        Creates the matter structure for the simulation.
        """
        super().create_matter_structure()

        # Create Vacuum store
        matter.store(self, 'Vacuum', 1)
        self.toStores.Vacuum.create_phase('air', 1)
        matter.procs.exmes.gas(self.toStores.Vacuum.aoPhases[0], 'Port_1')
        matter.procs.exmes.gas(self.toStores.Vacuum.aoPhases[0], 'Port_2')

        # Create Store
        matter.store(self, 'Store', 1)
        self.toStores.Store.create_phase('air', self.toStores.Store.fVolume)
        matter.procs.exmes.gas(self.toStores.Store.aoPhases[0], 'Port_Out')

        # Create Valve_1
        matter.store(self, 'Valve_1', 1e-6)
        cParams = matter.helper.phase.create.air(self, self.toStores.Valve_1.fVolume)
        matter.phases.flow.gas(self.toStores.Valve_1, 'flow', *cParams)
        matter.procs.exmes.gas(self.toStores.Valve_1.aoPhases[0], 'In')
        matter.procs.exmes.gas(self.toStores.Valve_1.aoPhases[0], 'Out')

        # Create Filter
        matter.store(self, 'Filter', 1e-1)
        cParams = matter.helper.phase.create.air(self, self.toStores.Filter.fVolume)
        matter.phases.flow.gas(self.toStores.Filter, 'flow', *cParams)
        matter.procs.exmes.gas(self.toStores.Filter.aoPhases[0], 'In')
        matter.procs.exmes.gas(self.toStores.Filter.aoPhases[0], 'Out')
        matter.procs.exmes.gas(self.toStores.Filter.aoPhases[0], 'Filtered')

        # Create Valve_2
        matter.store(self, 'Valve_2', 1e-6)
        cParams = matter.helper.phase.create.air(self, self.toStores.Valve_2.fVolume)
        matter.phases.flow.gas(self.toStores.Valve_2, 'flow', *cParams)
        matter.procs.exmes.gas(self.toStores.Valve_2.aoPhases[0], 'In')
        matter.procs.exmes.gas(self.toStores.Valve_2.aoPhases[0], 'Out')

        # Create Pipes
        fRoughness = 0
        pipe_names = [
            'Pipe_Store_Valve1_1', 'Pipe_Store_Valve1_2',
            'Pipe_Valve1_Filter_1', 'Pipe_Valve1_Filter_2',
            'Pipe_Filter_Valve2_1', 'Pipe_Filter_Valve2_2',
            'Pipe_Valve2_Store_1', 'Pipe_Valve2_Store_2'
        ]
        for pipe_name in pipe_names:
            components.matter.pipe(self, pipe_name, self.fPipeLength, self.fPipeDiameter, fRoughness)

        # Create Branches
        matter.branch(self, 'Store.Port_Out', ['Pipe_Store_Valve1_1', 'Pipe_Store_Valve1_2'], 'Valve_1.In')
        matter.branch(self, 'Valve_1.Out', ['Pipe_Valve1_Filter_1', 'Pipe_Valve1_Filter_2'], 'Filter.In')
        matter.branch(self, 'Filter.Out', ['Pipe_Filter_Valve2_1', 'Pipe_Filter_Valve2_2'], 'Valve_2.In')
        matter.branch(self, 'Valve_2.Out', ['Pipe_Valve2_Store_1', 'Pipe_Valve2_Store_2'], 'Vacuum.Port_2')
        matter.branch(self, 'Filter.Filtered', [], 'Vacuum.Port_1')

    def create_solver_structure(self):
        """
        Creates the solver structure for the simulation.
        """
        super().create_solver_structure()

        # Set timestep properties
        tProps = {'rMaxChange': 0.01}
        self.toStores.Store.aoPhases[0].set_time_step_properties(tProps)
        self.toStores.Vacuum.aoPhases[0].set_time_step_properties(tProps)

        # Configure solvers
        solver.matter_multibranch.iterative.branch(self.aoBranches[:4])
        self.oManual = solver.matter.manual.branch(self.aoBranches[4])
        self.oManual.set_flow_rate(0.01)

        self.set_thermal_solvers()

    def exec(self, _):
        """
        Executes the system's behavior during simulation ticks.
        """
        super().exec()
        # Placeholder for dynamic flow rate adjustments
        # Uncomment and implement logic for real-time flow rate control.
        # Example:
        # if self.oTimer.fTime == 540:
        #     self.oManual.set_flow_rate(0.02)
