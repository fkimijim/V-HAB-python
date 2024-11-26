class SWMEStore(matter.store):
    """
    SWMEStore: A matter store with a liquid water and water vapor phase,
    connected through the X50Membrane P2P processor.
    """

    def __init__(self, oContainer, sName):
        # Parsing the overall SWME vapor volume from the parent system
        fSWMEVaporVolume = oContainer.fSWMEVaporVolume

        # Defining volume available for the liquid phase inside the hollow fibers
        fSWMELiquidVolume = (
            3.14159265359 *
            (oContainer.fFiberInnerDiameter / 2) ** 2 *
            oContainer.fFiberExposedLength *
            oContainer.iNumberOfFibers
        )

        fSWMEVolume = fSWMEVaporVolume + fSWMELiquidVolume

        # Calling the parent class constructor
        super().__init__(oContainer, sName, fSWMEVolume)

        # Creating the input struct for the findProperty() method
        tParameters = {
            "sSubstance": "H2O",
            "sProperty": "Density",
            "sFirstDepName": "Temperature",
            "fFirstDepValue": oContainer.fInitialTemperature,
            "sPhaseType": "liquid",
            "sSecondDepName": "Pressure",
            "fSecondDepValue": 28300,
            "bUseIsobaricData": True,
        }

        fWaterDensity = self.oMT.findProperty(tParameters)

        fWaterMass = fWaterDensity * fSWMELiquidVolume

        # Creating liquid water phase inside the hollow fibers of the X50 membrane
        oLiquidHoFiPhase = matter.phases.liquid(
            self,  # Store where the phase is located
            "FlowPhase",  # Phase name
            {"H2O": fWaterMass},  # Phase contents
            oContainer.fInitialTemperature,  # Phase temperature
            28300,  # Phase pressure
        )

        # Calculating the mass of water to put in the SWME volume
        # so it is in equilibrium with the hollow fibers at initial temperature
        fVaporPressure = self.oMT.calculateVaporPressure(oContainer.fInitialTemperature, "H2O")

        # Updating the input struct for the gas phase
        tParameters["sPhaseType"] = "gas"
        tParameters["fSecondDepValue"] = fVaporPressure

        # Calculating the vapor density
        fVaporDensity = self.oMT.findProperty(tParameters)

        # Calculating the water vapor mass
        fVaporMass = fVaporDensity * fSWMEVaporVolume

        # Creating the vapor phase in the SWME around the hollow fibers
        oVaporSWME = matter.phases.gas(
            self,  # Store in which the phase is located
            "VaporPhase",  # Phase name
            {"H2O": fVaporMass},  # Phase contents
            fSWMEVaporVolume,  # Phase volume
            oContainer.fInitialTemperature,  # Phase temperature
        )

        # Creating exmes for the vapor phase
        matter.procs.exmes.gas(oVaporSWME, "VaporIn")  # Vapor exiting the X50 membrane
        matter.procs.exmes.gas(oVaporSWME, "VaporOut")  # Vapor exiting to the backpressure valve

        # Creating exmes for the liquid water phase
        matter.procs.exmes.liquid(oLiquidHoFiPhase, "WaterIn")  # Water entering the SWME
        matter.procs.exmes.liquid(oLiquidHoFiPhase, "WaterOut")  # Water exiting the SWME
        matter.procs.exmes.liquid(oLiquidHoFiPhase, "WaterToVapor")  # Water evaporating through the membrane

        # Calculating the total membrane area
        fAreaPerFiber = (
            oContainer.fFiberExposedLength * 2 * 3.14159265359 * (oContainer.fFiberInnerDiameter / 2)
        )
        fMembraneArea = fAreaPerFiber * oContainer.iNumberOfFibers

        # Creating P2P processor for the vapor flux through the membrane
        X50Membrane(
            self,
            "X50Membrane",
            "FlowPhase.WaterToVapor",
            "VaporPhase.VaporIn",
            fMembraneArea,
        )
