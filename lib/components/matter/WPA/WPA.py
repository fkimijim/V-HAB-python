class WPA(vsys):
    """
    Model of the Water Processing Assembly (WPA) used on the ISS.
    """
    
    def __init__(self, oParent, sName, fTimeStep=60):
        super().__init__(oParent, sName, fTimeStep)
        eval(self.oRoot.oCfgParams.configCode(self))
        
        self.fFlowRate = 5.8967 / 3600  # Flow rate out of the waste water tank [kg/s]
        self.fVolumetricFlowRate = self.fFlowRate / 998.24  # Convert to volumetric flow rate [m^3/s]
        self.fCheckFillStateIntervall = 60  # Interval to check fill state
        self.abContaminants = []  # Ionic contaminant array
        self.bCurrentlyProcessingWater = False
        self.fPower = 133 + 94 + 14  # Power usage in standby [W]
        self.bContinousWaterProcessingMode = False

        # Number of cells in each bed
        miCells = [5, 5, 3, 5, 3, 3, 2]
        # Initialize the subsystems
        components.matter.WPA.subsystems.MultifiltrationBED(self, 'MultiBED1', miCells, False)
        components.matter.WPA.subsystems.MultifiltrationBED(self, 'MultiBED2', miCells, False)
        components.matter.WPA.subsystems.MultifiltrationBED(self, 'IonBed', miCells, False, True)

    def createMatterStructure(self):
        super().createMatterStructure()

        # Create stores
        matter.store(self, 'WasteWater', 68 / 998)  # 68 kg of water
        matter.store(self, 'LiquidSeperator_1', 2e-6)
        matter.store(self, 'LiquidSeperator_2', 2e-6)
        matter.store(self, 'Delay_Tank', 100)
        matter.store(self, 'Check_Tank', 1e-6)
        matter.store(self, 'Rack_Air', 0.001065 * 0.447 + 1e-6)

        # Create phases
        oWasteWater = self.toStores.WasteWater.createPhase('mixture', 'Water', 'liquid', 0.04 * self.toStores.WasteWater.fVolume, {'H2O': 1}, 293, 1e5)
        oLiquidSeperator1 = self.toStores.LiquidSeperator_1.createPhase('mixture', 'flow', 'Water', 'liquid', 1e-6, {'H2O': 1}, 293, 1e5)
        oCheckTank = self.toStores.Check_Tank.createPhase('mixture', 'flow', 'Water', 'liquid', self.toStores.Check_Tank.fVolume, {'H2O': 1}, 293, 1e5)
        oReactor = self.toStores.Rack_Air.createPhase('mixture', 'flow', 'Water', 'liquid', 0.001065 * 0.447, {'H2O': 0.9995, 'O2': 5e-4}, 402.594, 4.481e5)
        oLiquidSeperator2 = self.toStores.LiquidSeperator_2.createPhase('mixture', 'flow', 'Water', 'liquid', 1e-6, {'H2O': 1}, 293, 1e5)

        # Additional phases
        oRackAir = self.toStores.Rack_Air.createPhase('gas', 'flow', 'Air', 1e-6, {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5)

        # Components
        components.matter.WPA.components.Reactor_Manip('Oxidator', oReactor)
        components.matter.Manips.ManualManipulator(self, 'WasteWaterManip', oWasteWater)
        components.matter.WPA.components.MLS(self.toStores.LiquidSeperator_1, 'LiquidSeperator_1_P2P', oLiquidSeperator1, oRackAir)
        components.matter.WPA.components.MLS(self.toStores.LiquidSeperator_2, 'LiquidSeperator_2_P2P', oLiquidSeperator2, oRackAir)
        components.matter.P2Ps.ManualP2P(self.toStores.Rack_Air, 'ReactorOxygen_P2P', oRackAir, oReactor)
        components.matter.pH_Module.flowManip('pH_Manipulator_CheckTank', oCheckTank)

        # Valves
        oReflowValve = components.matter.valve(self, 'ReflowValve', 0)
        self.abContaminants = self.toChildren.MultiBED1.abContaminants
        components.matter.WPA.components.MicrobialCheckValve(self, 'MicrobialCheckValve', 1, oReflowValve, self.abContaminants)

        # Branches
        matter.branch(self, oWasteWater, {}, 'Inlet', 'Inlet')
        matter.branch(self, oCheckTank, {'MicrobialCheckValve'}, 'Outlet', 'Outlet')

        oInletPhaseMLS1 = self.toChildren.MultiBED1.toChildren.Resin_1.toStores.Resin.toPhases.Water_1
        matter.branch(self, oLiquidSeperator1, {}, oInletPhaseMLS1, 'MLS1_to_MFBed1')

        oOutletPhaseMFBed1 = self.toChildren.MultiBED1.toStores.OrganicRemoval.toPhases.Water
        oInletPhaseMFBed2 = self.toChildren.MultiBED2.toChildren.Resin_1.toStores.Resin.toPhases.Water_1
        matter.branch(self, oOutletPhaseMFBed1, {}, oInletPhaseMFBed2, 'MFBed1_to_MFBed2')

        oOutletPhaseMFBed2 = self.toChildren.MultiBED2.toStores.OrganicRemoval.toPhases.Water
        matter.branch(self, oOutletPhaseMFBed2, {}, oReactor, 'MFBed2_to_Reactor')

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.manual.branch(self.toBranches.WasteWater_to_MLS1)

        if self.bContinousWaterProcessingMode:
            self.toBranches.WasteWater_to_MLS1.oHandler.setFlowRate(self.fFlowRate)

    def exec(self, _):
        super().exec(_)

        if not self.bContinousWaterProcessingMode:
            bActiveMassTransfer = self.toBranches.WasteWater_to_MLS1.oHandler.bMassTransferActive
            if (self.toStores.WasteWater.toPhases.Water.fMass > 0.65 * 68) and not bActiveMassTransfer:
                fMassToTransfer = 0.61 * self.toStores.WasteWater.toPhases.Water.fMass
                fTimeForTransfer = fMassToTransfer / self.fFlowRate

                self.toBranches.WasteWater_to_MLS1.oHandler.setMassTransfer(fMassToTransfer, fTimeForTransfer)
                self.setTimeStep(fTimeForTransfer)

            self.bCurrentlyProcessingWater = self.toBranches.WasteWater_to_MLS1.oHandler.bMassTransferActive

            if self.bCurrentlyProcessingWater:
                afFlowRates = [0] * self.oMT.iSubstances
                afFlowRates[self.oMT.tiN2I.O2] = 0.001e-3
                self.toStores.Rack_Air.toProcsP2P.ReactorOxygen_P2P.setFlowRate(afFlowRates)
                self.fPower = 320 + 94 + 14
            else:
                afFlowRates = [0] * self.oMT.iSubstances
                self.toStores.Rack_Air.toProcsP2P.ReactorOxygen_P2P.setFlowRate(afFlowRates)
                self.setTimeStep(self.fCheckFillStateIntervall)
                self.fPower = 133 + 94 + 14
