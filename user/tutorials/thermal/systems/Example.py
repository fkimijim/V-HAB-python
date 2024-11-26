class Example(vsys):
    """
    Example
    Example simulation for a thermal system in V-HAB.
    This system showcases the combination of matter and thermal domains and the different thermal heat transfer mechanisms.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 1)

        self.fPipeLength = 1.5
        self.fPipeDiameter = 0.005
        self.fPressureDifference = 1  # Pressure difference in bar

        # Add subsystem
        tutorials.thermal.subsystems.ExampleSubsystem(self, "SubSystem")

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        # Space store
        self.toStores.Space = matter.Store(self, "Space", float("inf"))
        self.toStores.Space.create_phase("vacuum", "VacuumPhase")

        # Tank 1
        self.toStores.Tank_1 = matter.Store(self, "Tank_1", 1)
        oTank1Gas = self.toStores.Tank_1.create_phase("air", "Tank1Air", 1, 293.15)

        # Tank 2
        self.toStores.Tank_2 = matter.Store(self, "Tank_2", 1)
        oTank2Gas = self.toStores.Tank_2.create_phase(
            "air", "Tank2Air", 1, 323.15, 0.5, (1 + self.fPressureDifference) * 1e5
        )

        # Pipe connecting tanks
        components.matter.Pipe(self, "Pipe", self.fPipeLength, self.fPipeDiameter)
        matter.Branch(self, oTank1Gas, ["Pipe"], oTank2Gas, "Branch")

        # Subsystem connections
        components.matter.Pipe(self, "Pipe1", 1, 0.005)
        components.matter.Pipe(self, "Pipe2", 1, 0.005)
        matter.Branch(self, "SubsystemInput", ["Pipe1"], oTank2Gas)
        matter.Branch(self, "SubsystemOutput", ["Pipe2"], oTank2Gas)
        self.toChildren.SubSystem.setIfFlows("SubsystemInput", "SubsystemOutput")

    def createThermalStructure(self):
        super().createThermalStructure()

        oCapacityTank_1 = self.toStores.Tank_1.toPhases.Tank1Air.oCapacity
        oCapacityTank_2 = self.toStores.Tank_2.toPhases.Tank2Air.oCapacity
        oCapacitySpace = self.toStores.Space.toPhases.VacuumPhase.oCapacity

        # Heat source for Tank 1
        oHeatSource = thermal.HeatSource("Heater", 0)
        oCapacityTank_1.add_heat_source(oHeatSource)

        # Heat source for Tank 2 with constant heat flow of 50 W
        oHeatSource = thermal.HeatSource("Heater", 50)
        oCapacityTank_2.add_heat_source(oHeatSource)

        # Radiative resistance for radiator
        fEpsilon = 0.8
        fSightFactor = 1
        fArea = 0.1
        fRadiativeResistance = 1 / (fEpsilon * fSightFactor * self.oMT.Const.fStefanBoltzmann * fArea)
        thermal.procs.Conductors.Radiative(self, "Radiator_Conductor", fRadiativeResistance)

        # Conductive resistance for piping
        fWallThickness = 0.002
        fPipeMaterialArea = (3.14159 * (self.fPipeDiameter + fWallThickness) ** 2) - (
            3.14159 * self.fPipeDiameter ** 2
        )
        fThermalConductivityCopper = 15
        fConductionResistance = self.fPipeLength / (fPipeMaterialArea * fThermalConductivityCopper)
        thermal.procs.Conductors.Conductive(self, "Material_Conductor", fConductionResistance)
        thermal.procs.Conductors.Conductive(self, "Material_Conductor1", fConductionResistance)
        thermal.procs.Conductors.Conductive(self, "Material_Conductor2", fConductionResistance)

        # Thermal branches
        thermal.Branch(self, oCapacitySpace, ["Radiator_Conductor"], oCapacityTank_2, "Radiator")
        thermal.Branch(self, oCapacityTank_1, ["Material_Conductor"], oCapacityTank_2, "Pipe_Material_Conductor")
        thermal.Branch(self, "Conduction_From_Subsystem", ["Material_Conductor1"], oCapacityTank_2)
        thermal.Branch(self, "Conduction_To_Subsystem", ["Material_Conductor2"], oCapacityTank_2)

        # Connect thermal interfaces for subsystem
        self.toChildren.SubSystem.setIfThermal("Conduction_To_Subsystem", "Conduction_From_Subsystem")

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.Interval.Branch(self.toBranches.Branch)

        tTimeStepProperties = {"rMaxChange": 0.001}
        self.toStores.Tank_1.toPhases[0].oCapacity.set_time_step_properties(tTimeStepProperties)

        self.setThermalSolvers()

    def exec(self, _):
        super().exec()

        # Dynamic heat release in Tank 1
        fHeatFlow = 100 * math.sin(self.oTimer.fTime / 10)
        self.toStores.Tank_1.toPhases.Tank1Air.oCapacity.toHeatSources.Heater.set_heat_flow(fHeatFlow)
