class Example(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0
    Two tanks filled with gas at different temperatures and pressures
    with a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.
        Calls the parent constructor with execution interval set to 30 seconds.
        """
        super().__init__(oParent, sName, 30)

    def create_matter_structure(self):
        """
        Creates all simulation objects in the matter domain.
        """
        super().create_matter_structure()

        # Creating a store, volume 10 m^3
        self.create_store("Tank_1", 10)

        fMolH3PO4 = 10

        # Adding a phase to the store 'Tank_1', 10 m^3 water with H3PO4
        oTank1 = self.toStores["Tank_1"].create_phase(
            "liquid",
            "Water",
            {"H2O": 998, "H3PO4": fMolH3PO4 * self.oMT.afMolarMass[self.oMT.tiN2I["H3PO4"]]},
            293,
            1e5,
        )

        components.matter.pH_Module.stationaryManip("GrowthMediumChanges_Manip", oTank1)

        self.create_store("Tank_2", 1000)

        fMolNaOH = 8 * fMolH3PO4
        fMassNaOH = fMolNaOH * self.oMT.afMolarMass[self.oMT.tiN2I["NaOH"]]

        oTank2 = self.toStores["Tank_2"].create_phase(
            "liquid",
            "boundary",
            "Water",
            self.toStores["Tank_2"].fVolume,
            {
                "H2O": 1994 / (1994 + fMassNaOH),
                "NaOH": fMassNaOH / (1994 + fMassNaOH),
            },
            293,
            1e5,
        )

        # Adding a pipe to connect the tanks
        components.matter.pipe(self, "Pipe", 1.5, 0.005)

        # Creating the flowpath (branch) between the components
        self.create_branch(oTank2, ["Pipe"], oTank1, "Branch")

    def create_thermal_structure(self):
        """
        Creates all simulation objects in the thermal domain.
        """
        super().create_thermal_structure()

        # For this simple model, no additional thermal objects are needed.
        # Thermal solvers will be automatically created by set_thermal_solvers.

    def create_solver_structure(self):
        """
        Creates all solver objects required for a simulation.
        """
        super().create_solver_structure()

        tTimeStepProperties = {
            "arMaxChange": [0.01] * self.oMT.iSubstances,
            "rMaxChange": 0.005,
        }
        self.toStores["Tank_1"].toPhases["Water"].set_time_step_properties(tTimeStepProperties)

        # Creating a manual solver object for the branch
        solver.matter.manual.branch(self.toBranches["Branch"])

        # Set a fixed flow rate for the branch
        self.toBranches["Branch"].oHandler.set_flow_rate(0.1)

        # Call thermal solvers for temperature changes in the system
        self.set_thermal_solvers()

    def exec(self, _):
        """
        Execute function for this system.
        Used to change the system state dynamically during simulation.
        """
        super().exec()
