class Example(vsys):
    """
    Example liquid flow simulation for V-HAB 2.0
    Two tanks, connected by two pipes with a pump in between. 
    The flow rate setpoint for the pump is changed every 100 seconds.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.

        Args:
            oParent: The parent object of this system.
            sName: The name of the system.
        """
        super().__init__(oParent, sName, 60)
        self.iCells = 10

    def create_matter_structure(self):
        """
        Create the matter structure for the simulation.
        """
        super().create_matter_structure()

        # Create water tanks
        matter.store(self, "WaterTank_1", 2)
        matter.store(self, "WaterTank_2", 2)

        fDensityH2O = self.oMT.calculate_density("liquid", {"H2O": 100}, 293, 101325)

        oWaterPhase1 = matter.phases.mixture(
            self.toStores.WaterTank_1,
            "Water_Phase",
            "liquid",
            {"H2O": fDensityH2O * 0.1},
            293.15,
            101325,
        )

        oWaterPhase2 = matter.phases.mixture(
            self.toStores.WaterTank_2,
            "Water_Phase",
            "liquid",
            {"H2O": fDensityH2O * 0.1},
            293.15,
            101325,
        )

        self.toStores.WaterTank_1.create_phase("air", 2 - oWaterPhase1.fVolume, 293.15, 0.5, 1e5)
        oAir2 = self.toStores.WaterTank_2.create_phase("air", 2 - oWaterPhase2.fVolume, 293.15, 0.5, 1.1e5)

        self.toStores.WaterTank_1.add_standard_volume_manipulators()

        matter.manips.volume.StoreVolumeCalculation.compressible_medium(
            f"{oAir2.sName}_CompressibleManip", oAir2
        )
        matter.manips.volume.StoreVolumeCalculation.compressible_medium(
            f"{oWaterPhase2.sName}_CompressibleManip", oWaterPhase2
        )

        matter.store(self, "AirTank_1", 2)
        matter.store(self, "AirTank_2", 2)

        oAir1 = self.toStores.AirTank_1.create_phase(
            "gas", "AirPhase", 2, {"N2": 8e4, "O2": 2e4, "CO2": 500}, 293.15, 0.5
        )
        oAir2 = self.toStores.AirTank_2.create_phase(
            "gas", "AirPhase", 2, {"N2": 1.1 * 8e4, "O2": 1.1 * 2e4, "CO2": 1.1 * 500}, 293.15, 0.5
        )

        fFlowVolume = 1e-4
        matter.store(self, "FlowPath", fFlowVolume)

        # Adding flow nodes for water and air
        coFlowNodeAir = []
        coFlowNodeWater = []
        for iCell in range(1, self.iCells + 1):
            coFlowNodeAir.append(
                self.toStores.FlowPath.create_phase(
                    "gas",
                    "flow",
                    f"AirCell_{iCell}",
                    0.5 * fFlowVolume / self.iCells,
                    {"N2": 8e4, "O2": 2e4, "CO2": 500},
                    293.15,
                    0.5,
                )
            )
            coFlowNodeWater.append(
                self.toStores.FlowPath.create_phase(
                    "mixture",
                    "flow",
                    f"WaterCell_{iCell}",
                    "liquid",
                    0.5 * fFlowVolume / self.iCells,
                    {"H2O": 1},
                    293.15,
                    1e5,
                )
            )
            matter.procs.exmes.gas(coFlowNodeAir[-1], f"P2P_Air{iCell}")
            matter.procs.exmes.mixture(coFlowNodeWater[-1], f"P2P_Water{iCell}")

            tests.mixture_flow.components.Adsorber(
                self.toStores.FlowPath,
                f"Adsorber_{iCell}",
                f"{coFlowNodeAir[-1].sName}.P2P_Air{iCell}",
                f"{coFlowNodeWater[-1].sName}.P2P_Water{iCell}",
            )

        # Adding pipes and branches
        for iCell in range(1, self.iCells):
            components.matter.pipe(self, f"AirPipe_{iCell}", 0.1, 0.05, 2e-3)
            components.matter.pipe(self, f"WaterPipe_{iCell}", 0.1, 0.05, 2e-3)

            matter.branch(
                self,
                coFlowNodeAir[iCell - 1],
                [f"AirPipe_{iCell}"],
                coFlowNodeAir[iCell],
                f"AirFlowBranch_{iCell}",
            )
            matter.branch(
                self,
                coFlowNodeWater[iCell - 1],
                [f"WaterPipe_{iCell}"],
                coFlowNodeWater[iCell],
                f"WaterFlowBranch_{iCell}",
            )

        # Add inflow and outflow branches
        components.matter.pipe(self, f"AirPipe_{self.iCells}", 0.1, 0.05, 2e-3)
        matter.branch(self, oAir1, [], coFlowNodeAir[0], "AirFlowBranchInlet")
        matter.branch(self, coFlowNodeAir[-1], [f"AirPipe_{self.iCells}"], oAir2, f"AirFlowBranch_{self.iCells}")

        # Reflow pipe and branch for air
        components.matter.pipe(self, "AirPipe_Reflow", 1, 0.03, 2e-3)
        matter.branch(self, oAir2, ["AirPipe_Reflow"], oAir1, "AirReflow")

        components.matter.pipe(self, f"WaterPipe_{self.iCells}", 0.1, 0.05, 2e-3)
        matter.branch(self, oWaterPhase1, [], coFlowNodeWater[0], "WaterFlowBranchInlet")
        matter.branch(self, coFlowNodeWater[-1], [f"WaterPipe_{self.iCells}"], oWaterPhase2, f"WaterFlowBranch_{self.iCells}")

        components.matter.pipe(self, "WaterPipe_Reflow", 1, 0.01, 2e-3)
        matter.branch(self, oWaterPhase2, ["WaterPipe_Reflow"], oWaterPhase1, "WaterReflow")

    def create_solver_structure(self):
        """
        Create solver structure for the simulation.
        """
        super().create_solver_structure()

        solver.matter.manual.branch(self.toBranches.AirFlowBranchInlet)
        solver.matter.manual.branch(self.toBranches.WaterFlowBranchInlet)

        self.toBranches.AirFlowBranchInlet.oHandler.set_flow_rate(0.1)
        self.toBranches.WaterFlowBranchInlet.oHandler.set_flow_rate(0.1)

        aoAirFlowBranches = [
            self.toBranches[f"AirFlowBranch_{iCell}"] for iCell in range(1, self.iCells + 1)
        ]
        aoAirFlowBranches.append(self.toBranches.AirReflow)

        aoWaterFlowBranches = [
            self.toBranches[f"WaterFlowBranch_{iCell}"] for iCell in range(1, self.iCells + 1)
        ]
        aoWaterFlowBranches.append(self.toBranches.WaterReflow)

        solver.matter_multibranch.iterative.branch(aoAirFlowBranches + aoWaterFlowBranches)

        tTimeStepProperties = {"rMaxChange": 0.001}
        self.toStores.WaterTank_1.toPhases.Water_Phase.set_time_step_properties(tTimeStepProperties)
        self.toStores.WaterTank_2.toPhases.Water_Phase.set_time_step_properties(tTimeStepProperties)
        self.toStores.AirTank_1.toPhases.AirPhase.set_time_step_properties(tTimeStepProperties)
        self.toStores.AirTank_2.toPhases.AirPhase.set_time_step_properties(tTimeStepProperties)

        self.set_thermal_solvers()

    def exec(self, *args):
        """
        Execute the system logic.
        """
        super().exec(*args)
