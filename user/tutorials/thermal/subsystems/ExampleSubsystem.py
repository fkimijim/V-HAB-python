class ExampleSubsystem(vsys):
    """
    ExampleSubsystem
    A subsystem containing a filter and a pipe.
    This example shows a vsys child representing a subsystem of a larger system.
    It has a filter that removes H2O and CO2 and also provides thermal interfaces to the parent system.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName)
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        fFilterVolume = 1
        self.toStores.Filter = matter.Store(self, "Filter", fFilterVolume)

        oFiltered = matter.phases.Mixture(
            self.toStores.Filter,
            "FilteredPhase",
            "solid",
            {"Zeolite13x": 1},
            293,
            1e5
        )

        oFlow = self.toStores.Filter.create_phase(
            "gas",
            "FlowPhase",
            fFilterVolume - oFiltered.fVolume,
            {"N2": 8e4, "O2": 2e4, "CO2": 500},
            293,
            0.5
        )

        tutorials.p2p.stationary.components.AbsorberExample(
            self.toStores.Filter,
            "filterproc",
            oFlow,
            oFiltered
        )

        matter.Branch(self, oFlow, [], "Inlet", "Inlet")
        matter.Branch(self, oFlow, [], "Outlet", "Outlet")

    def createThermalStructure(self):
        super().createThermalStructure()

        oCapacityFlow = self.toStores.Filter.toPhases.FlowPhase.oCapacity
        oCapacityFiltered = self.toStores.Filter.toPhases.FilteredPhase.oCapacity

        # Define conductors for interface branches
        fWallThickness = 0.002  # 2mm wall thickness
        fPipeDiameter = 0.0005
        fPipeMaterialArea = (3.14159 * (fPipeDiameter + fWallThickness)**2) - (3.14159 * fPipeDiameter**2)
        fPipeLength = 0.5
        fThermalConductivityCopper = 15
        fMaterialConductivity = (fPipeMaterialArea * fThermalConductivityCopper) / fPipeLength

        thermal.procs.Conductors.Conductive(self, "Material_Conductor1", fMaterialConductivity)
        thermal.procs.Conductors.Conductive(self, "Material_Conductor2", fMaterialConductivity)

        thermal.Branch(
            self,
            oCapacityFlow,
            ["Material_Conductor1"],
            "Inlet_Conduction",
            "Pipe_Material_Conductor_In"
        )
        thermal.Branch(
            self,
            oCapacityFlow,
            ["Material_Conductor2"],
            "Outlet_Conduction",
            "Pipe_Material_Conductor_Out"
        )

        # Add convective conductor
        fLength = 1
        fBroadness = 0.1
        fFlowArea = fBroadness * 0.1

        tutorials.thermal.components.ConvectionFilter(
            self,
            "Convective_Conductor",
            fLength,
            fBroadness,
            fFlowArea,
            self.toBranches.Inlet,
            1
        )

        thermal.Branch(
            self,
            oCapacityFlow,
            ["Convective_Conductor"],
            oCapacityFiltered,
            "Convective_Branch"
        )

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.Interval.Branch(self.aoBranches[0])
        solver.matter.Interval.Branch(self.aoBranches[1])

        self.setThermalSolvers()

    def setIfFlows(self, sInlet, sOutlet):
        self.connectIF("Inlet", sInlet)
        self.connectIF("Outlet", sOutlet)

    def setIfThermal(self, sInlet, sOutlet):
        """
        Sets thermal interfaces for the subsystem.
        Similar to setIfFlows but uses connectThermalIF instead of connectIF.
        """
        self.connectThermalIF("Inlet_Conduction", sInlet)
        self.connectThermalIF("Outlet_Conduction", sOutlet)

    def exec(self, _):
        super().exec()
