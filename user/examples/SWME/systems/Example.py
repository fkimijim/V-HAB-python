class Example(vsys):
    """
    EXAMPLE Example system to demonstrate the use of the SWME component.

    This system contains two tanks and a subsystem in between. The subsystem 
    represents the Spacesuit Water Membrane Evaporator (SWME) component, 
    which is used for spacesuit cooling.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 0.1)

        # Inlet water flow in [kg/s]
        self.fFlowRate = 91 / 3600

        # Initial inlet water temperature in [K]
        self.fInitialTemperature = 288.15

        # Setting parameters if they were set by a simulation runner
        eval(self.oRoot.oCfgParams.configCode(self))

        # Creating the SWME
        components.matter.SWME(self, 'SWME', self.fInitialTemperature)

    def create_matter_structure(self):
        """
        Create the matter structure for the simulation.
        """
        super().create_matter_structure()

        # Creating the inlet water feed tank
        matter.store(self, 'InletTank', 10)

        # Adding a liquid water phase to the inlet tank
        oWaterInlet = matter.phases.liquid(
            self.toStores.InletTank,          # Store in which the phase is located
            'WaterInlet',                     # Phase name
            {'H2O': 2000},                    # Phase contents
            self.fInitialTemperature,         # Phase temperature
            28300                             # Phase pressure
        )

        # Creating the outlet water feed tank
        matter.store(self, 'OutletTank', 10)

        # Adding an empty phase to the outlet tank
        oWaterOutlet = matter.phases.liquid(
            self.toStores.OutletTank,         # Store in which the phase is located
            'WaterOutlet',                    # Phase name
            {'H2O': 0},                       # Phase contents
            self.fInitialTemperature,         # Phase temperature
            28300                             # Phase pressure
        )

        # Creating an empty tank where the vapor flows to
        matter.store(self, 'EnvironmentTank', 10)

        # Adding an empty phase to the environment tank
        oEnvironment = matter.phases.boundary.gas(
            self.toStores.EnvironmentTank,    # Store in which the phase is located
            'EnvironmentPhase',               # Phase name
            {'H2O': 0},                       # Phase contents
            10,                               # Phase volume
            293,                              # Phase temperature
            0                                 # Phase pressure
        )

        # Two standard pipes connecting the SWME to the super system
        components.matter.pipe(self, 'Pipe_Inlet', 0.01, 0.0127)
        components.matter.pipe(self, 'Pipe_Outlet', 0.01, 0.0127)

        # Creating the flowpath between the components
        matter.branch(self, 'SWME_Inlet', ['Pipe_Inlet'], oWaterInlet, 'InletBranch')
        matter.branch(self, 'SWME_Outlet', ['Pipe_Outlet'], oWaterOutlet, 'OutletBranch')
        matter.branch(self, 'SWME_Vapor', [], oEnvironment, 'VaporBranch')

        self.toChildren.SWME.setInterfaces('SWME_Inlet', 'SWME_Outlet', 'SWME_Vapor')
        self.toChildren.SWME.setEnvironmentReference(oEnvironment)

    def create_thermal_structure(self):
        """
        Create the thermal structure for the simulation.
        """
        super().create_thermal_structure()

        # Automatic creation of thermal domain objects related to advective heat transfer
        self.set_thermal_solvers()

    def create_solver_structure(self):
        """
        Create the solver structure for the simulation.
        """
        super().create_solver_structure()

        # Manually setting the inlet flow rate
        self.toChildren.SWME.toBranches.InletBranch.oHandler.setFlowRate(-1 * self.fFlowRate)

        # Enable thermal solvers for temperature changes
        self.set_thermal_solvers()

    def exec(self, *args):
        """
        Execute the simulation step.
        """
        super().exec(*args)
