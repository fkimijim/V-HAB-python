class Photobioreactor(vsys):
    """
    Photobioreactor class defines the operational and geometric boundaries for
    the device where Chlorella vulgaris algae grow. It sets growth volume, depth,
    membrane properties, radiation conditions, and nutrient supply logic.
    """

    def __init__(self, oParent, sName, txPhotobioreactorProperties=None):
        # Check if properties are specified; if not, create an empty dictionary
        if txPhotobioreactorProperties is None:
            txPhotobioreactorProperties = {}

        if not isinstance(txPhotobioreactorProperties, dict):
            raise ValueError("The third input must be a dictionary.")

        # Set timestep
        fTimeStep = txPhotobioreactorProperties.get("fTimeStep", 30)

        super().__init__(oParent, sName, fTimeStep)
        eval(self.oRoot.oCfgParams.configCode(self))

        # Lighting properties
        self.sLightColor = txPhotobioreactorProperties.get("sLightColor", "RedExperimental")
        self.fSurfacePPFD = txPhotobioreactorProperties.get("fSurfacePPFD", 400)
        self.fNominalSurfacePPFD = self.fSurfacePPFD

        # Size properties
        self.fGrowthVolume = txPhotobioreactorProperties.get("fGrowthVolume", 0.5)
        self.fDepthBelowSurface = txPhotobioreactorProperties.get("fDepthBelowSurface", 0.0025)

        # Membrane properties
        self.fMembraneSurface = txPhotobioreactorProperties.get("fMembraneSurface", 10)
        self.fMembraneThickness = txPhotobioreactorProperties.get("fMembraneThickness", 0.0001)
        self.sMembraneMaterial = txPhotobioreactorProperties.get("sMembraneMaterial", "SSP-M823 Silicone")

        # Operational and Harvesting Parameters
        self.fCirculationVolumetricFlowPerFilter = txPhotobioreactorProperties.get(
            "fCirculationVolumetricFlowPerFilter", 4.167e-7
        )
        self.fNumberOfParallelFilters = txPhotobioreactorProperties.get("fNumberOfParallelFilters", 30)
        self.bUseUrine = txPhotobioreactorProperties.get("bUseUrine", True)

        self.fVolumetricFlowToHarvester = (
            self.fCirculationVolumetricFlowPerFilter * self.fNumberOfParallelFilters
        )

        # Calculate power demands
        fLightPowerDemand = (self.fSurfacePPFD / 400) * 4000
        fBasePowerDemandOther = (self.fSurfacePPFD / 400) * (self.fGrowthVolume / 0.5) * 3300
        self.fPower = fBasePowerDemandOther + fLightPowerDemand

        # Initial values
        self.fTotalProducedWater = 0
        self.fTotalProcessedUrine = 0

        # Create child system
        components.matter.algae.systems.ChlorellaInMedia(self, "ChlorellaInMedia")

    def setUrineSupplyToManual(self, bManualUrineSupply):
        self.bManualUrineSupply = bManualUrineSupply

    def setNitrateSupplyToManual(self, bManualNitrateSupply):
        self.bManualNitrateSupply = bManualNitrateSupply

    def createMatterStructure(self):
        super().createMatterStructure()

        # Create Air in PBR Phase
        matter.store(self, "ReactorAir", 1)
        self.toStores.ReactorAir.createPhase(
            "gas", "flow", "CabinAirFlow", 0.001, {"N2": 8e4, "O2": 2e4, "CO2": 50}, 293, 0.5
        )
        self.toStores.ReactorAir.createPhase(
            "gas", "HighCO2Air", 0.5, {"O2": 5000, "CO2": 59000}, 293, 0.5
        )

        # Air interfaces
        matter.procs.exmes.gas(self.toStores.ReactorAir.toPhases.CabinAirFlow, "From_Cabin")
        matter.procs.exmes.gas(self.toStores.ReactorAir.toPhases.CabinAirFlow, "To_Cabin")
        matter.branch(self, "ReactorAir.From_Cabin", {}, "Air_Inlet", "Air_From_Cabin")
        components.matter.pipe(self, "Pipe", 0.1, 0.1, 2e-3)
        matter.branch(self, "ReactorAir.To_Cabin", {"Pipe"}, "Air_Outlet", "Air_To_Cabin")

        # Create other necessary branches, exmes, and processes
        # (Continuing the logic for other branches, interfaces, and processes)

    def setOperatingMode(self, bMinimalMode):
        if bMinimalMode:
            self.toChildren.ChlorellaInMedia.toBranches.Air_from_GrowthChamber.oHandler.setFlowRate(1e-3)
            self.fSurfacePPFD = 0.01 * self.fNominalSurfacePPFD
            fOtherPowerDemandPerVolume = 330
        else:
            self.toChildren.ChlorellaInMedia.toBranches.Air_from_GrowthChamber.oHandler.setFlowRate(0.1)
            self.fSurfacePPFD = self.fNominalSurfacePPFD
            fOtherPowerDemandPerVolume = 3300

        fLightPowerDemand = (self.fSurfacePPFD / 400) * 4000
        fBasePowerDemandOther = (self.fSurfacePPFD / 400) * (self.fGrowthVolume / 0.5) * fOtherPowerDemandPerVolume
        self.fPower = fBasePowerDemandOther + fLightPowerDemand

    def exec(self, _):
        # Logic to resupply urine, nitrate, and water if not set to manual
        if not self.bManualUrineSupply and self.toStores.MediumMaintenance.toPhases.UrineSupplyBuffer.fMass < 0.7 * self.tControlParameters.fInitialMassUrineBuffer:
            fDesiredResupply = self.tControlParameters.fInitialMassUrineBuffer - self.toStores.MediumMaintenance.toPhases.UrineSupplyBuffer.fMass
            if self.toBranches.Urine_from_Cabin.coExmes[2].oPhase.fMass > fDesiredResupply and not self.toBranches.Urine_from_Cabin.oHandler.bMassTransferActive:
                self.toBranches.Urine_from_Cabin.oHandler.setMassTransfer(-fDesiredResupply, 60)

        # Similarly handle nitrate and water supply logic...

        # Track processed urine and produced water
        if self.fTimeStep > 0:
            self.fTotalProcessedUrine -= self.toBranches.Urine_from_Cabin.aoFlows.fFlowRate * self.fTimeStep
            self.fTotalProducedWater += self.toBranches.WaterHarvest_to_Potable.aoFlows.fFlowRate * self.fTimeStep

        super().exec(_)
