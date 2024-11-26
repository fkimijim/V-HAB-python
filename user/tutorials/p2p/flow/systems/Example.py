class Example(vsys):
    """
    EXAMPLE simulation demonstrating flow P2P processors in V-HAB 2.

    Creates two tanks, one with ~two bars of pressure, one with ~one bar,
    and a filter in between. The tanks are connected to the filter with
    pipes of 50cm length and 5mm diameter. The filter removes CO2 and H2O
    based on the material used in the filter and the corresponding
    calculation from the matter table.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 60)

        # Create the first tank store
        matter.store(self, 'Atmos', 10, False)
        oAir1 = self.toStores.Atmos.createPhase(
            'gas', 'Air', 10, {'N2': 1.6e5, 'O2': 4e4, 'CO2': 1000}, 303, 0.5
        )

        # Create the second tank store
        matter.store(self, 'Atmos2', 10)
        oAir2 = self.toStores.Atmos2.createPhase(
            'gas', 'Air', 10, {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
        )

        # Create the filter store with flow and filtered phases
        fFilterVolume = 1
        matter.store(self, 'Filter', fFilterVolume)
        oFlow = self.toStores.Filter.createPhase(
            'gas', 'flow', 'FlowPhase', 1e-6, {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
        )
        oFiltered = matter.phases.mixture(
            self.toStores.Filter, 'FilteredPhase', 'solid', {'Zeolite13x': 1}, 293, 1e5
        )

        # Create the P2P processor
        tutorials.p2p.flow.components.AbsorberExampleFlow(
            self.toStores.Filter, 'filterproc', oFlow, oFiltered
        )

        # Create the pipes
        components.matter.pipe(self, 'Pipe_1', 0.5, 0.01)
        components.matter.pipe(self, 'Pipe_2', 0.5, 0.01)

        # Create branches connecting the components
        matter.branch(self, oAir1, ['Pipe_1'], oFlow)
        matter.branch(self, oFlow, ['Pipe_2'], oAir2)

    def createSolverStructure(self):
        super().createSolverStructure()

        # Define the solver structure for the branches
        solver.matter_multibranch.iterative.branch(self.aoBranches, 'complex')

        # Set thermal solvers
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execution method, inherited from vsys.
        """
        super().exec(_)
