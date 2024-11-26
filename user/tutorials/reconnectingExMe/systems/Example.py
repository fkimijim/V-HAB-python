class Example(vsys):
    """
    Simple system showing ExMe reconfiguration.
    This example uses three stores with different temperature and
    pressure conditions to show how to reconnect ExMes during a
    simulation. The way the branches are connected will be changed at
    tick 1000 in the simulation.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, -1)

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        # Creating stores and phases
        matter.store(self, 'Store1', 10, False)
        oAir1 = self.toStores.Store1.createPhase(
            'gas', 'Air', 10, {'N2': 1e5, 'O2': 0, 'CO2': 0}, 293, 0
        )

        matter.store(self, 'Store2', 10)
        oAir2 = self.toStores.Store2.createPhase(
            'gas', 'Air', 10, {'N2': 0, 'O2': 10e5, 'CO2': 0}, 303, 0
        )

        matter.store(self, 'Store3', 10)
        self.toStores.Store3.createPhase(
            'gas', 'Air', 10, {'N2': 0, 'O2': 0, 'CO2': 10e5}, 283, 0.5
        )

        # Creating pipe component
        components.matter.pipe(self, 'Pipe', 1, 0.005)

        # Creating branch
        matter.branch(self, oAir2, ['Pipe'], oAir1, 'AirExchange')

    def createSolverStructure(self):
        super().createSolverStructure()

        # Setting up the solver for the branch
        solver.matter.interval.branch(self.aoBranches[0])

        # Setting thermal solvers
        self.setThermalSolvers()

    def exec(self, _):
        super().exec()

        # Reconnect ExMe to a different phase at tick 1000
        if self.oTimer.iTick == 1000:
            self.toBranches.AirExchange.coExmes[0].reconnectExMe(self.toStores.Store3.toPhases.Air)
