class Example(vsys):
    """
    EXAMPLE: Simulation demonstrating stationary P2P processors in V-HAB 2
    Creates two tanks, one with ~two bars of pressure, one with ~one bar and a filter in between.
    The tanks are connected to the filter with pipes of 50 cm length and 5 mm diameter.
    The filter removes CO2, and H2O based on the material used in the filter and the 
    corresponding calculation from the matter table.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 10)
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        matter.store(self, 'Atmos', 10)
        oAir = self.toStores.Atmos.createPhase(
            'gas', 'Air', 10, {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
        )

        fFilterVolume = 1
        matter.store(self, 'Filter', fFilterVolume)

        oFiltered = matter.phases.mixture(
            self.toStores.Filter, 'FilteredPhase', 'solid', {'Zeolite13x': 1}, 293, 1e5
        )

        oFlow = self.toStores.Filter.createPhase(
            'gas', 'FlowPhase', fFilterVolume - oFiltered.fVolume, {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
        )

        # Creating the P2P processor
        tutorials.p2p.stationary.components.AbsorberExample(self.toStores.Filter, 'filterproc', oFlow, oFiltered)

        components.matter.fan(self, 'Fan', 40000, True)

        components.matter.pipe(self, 'Pipe_1', 0.5, 0.005)
        components.matter.pipe(self, 'Pipe_2', 0.5, 0.005)
        components.matter.pipe(self, 'Pipe_3', 0.5, 0.005)

        matter.branch(self, oAir, ['Pipe_1', 'Fan', 'Pipe_2'], oFlow)
        matter.branch(self, oFlow, ['Pipe_3'], oAir)

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.interval.branch(self.aoBranches[0])
        solver.matter.interval.branch(self.aoBranches[1])

        self.setThermalSolvers()

    def exec(self, _):
        super().exec(_)
