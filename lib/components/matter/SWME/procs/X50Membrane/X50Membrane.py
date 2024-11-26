class X50Membrane(matter.procs.p2ps.stationary):
    """
    X50Membrane: A model of the water evaporation through a membrane.
    This class calculates water vapor flow through a hollow fiber membrane,
    considering temperatures and heat capacities of water and water vapor.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, fMembraneArea):
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

        # Static properties
        self.fPressureDropCoefficient = 1.021
        self.fMembraneTortuosity = 2.74
        self.fMembraneThickness = 40e-6  # [m]
        self.fMembranePorosity = 0.4
        self.fPoreDiameter = 0.04e-6  # [m]
        self.fReferencePressure = 800  # [Pa]

        # Dynamic properties
        self.fWaterVaporFlowRate = 0
        self.fHeatRejection = 0
        self.fHeatRejectionSimple = 0
        self.fMeanTemperature = None
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I['H2O']] = 1
        self.fSWMEInletTemperature = 0
        self.fSWMEOutletTemperature = 0

        # Derived properties
        self.fMeanMolecularFreePathCalculationFactor = (
            self.oMT.Const.fBoltzmann /
            (self.oMT.ttxMatter['H2O'].fAverageMolecularDiameter ** 2 * (2 ** 0.5) * 3.14159265359)
        )
        self.fMembraneCoefficientCalculationFactor = (
            (1.064 * (self.fPoreDiameter / 2) * self.fMembranePorosity) /
            (self.fMembraneTortuosity * self.fMembraneThickness) *
            (self.oMT.ttxMatter['H2O'].fMolarMass / self.oMT.Const.fUniversalGas) ** 0.5
        )
        self.fMembraneArea = fMembraneArea
        self.oTemperatureProcessor = None
        self.oHeatSource = None

    def setTemperatureProcessor(self, oProcessor):
        """Set the temperature processor for the membrane."""
        self.oTemperatureProcessor = oProcessor

    def setHeatSource(self, oHeatSource):
        """Set the heat source for the membrane."""
        self.oHeatSource = oHeatSource

    def update(self):
        """Update the membrane calculations."""
        # Getting current water temperatures
        fWaterTemperatureInlet = self.oIn.oPhase.toProcsEXME.WaterIn.oFlow.fTemperature
        fWaterTemperatureOutlet = self.oIn.oPhase.fTemperature

        self.fSWMEInletTemperature = fWaterTemperatureInlet
        self.fSWMEOutletTemperature = fWaterTemperatureOutlet

        # Calculating the mean temperature
        self.fMeanTemperature = 0.5 * (fWaterTemperatureInlet + fWaterTemperatureOutlet)

        # Calculating vapor pressure inside the SWME
        fVaporPressure = self.fPressureDropCoefficient * self.oOut.oPhase.fPressure

        # Liquid water properties
        tLiquidParameters = {
            'sSubstance': 'H2O',
            'sProperty': 'Heat Capacity',
            'sFirstDepName': 'Temperature',
            'fFirstDepValue': self.fMeanTemperature,
            'sPhaseType': 'liquid',
            'bUseIsobaricData': True
        }
        fLiquidSpecificHeatCapacity = self.oMT.findProperty(tLiquidParameters)

        # Saturation vapor pressure
        fSaturationVaporPressure = self.oMT.calculateVaporPressure(self.fMeanTemperature, 'H2O')

        # Membrane coefficient
        fMembraneCoefficient = self.fMembraneCoefficientCalculationFactor / (self.fMeanTemperature ** 0.5)

        # Calculate water vapor flow rate
        if fVaporPressure < fSaturationVaporPressure:
            self.fWaterVaporFlowRate = (
                fMembraneCoefficient *
                (fSaturationVaporPressure - fVaporPressure) *
                self.fMembraneArea
            )
        else:
            self.fWaterVaporFlowRate = 0

        # Rounding to avoid oscillations
        self.fWaterVaporFlowRate = tools.round.prec(self.fWaterVaporFlowRate, self.oTimer.iPrecision)

        # Input flow rate into SWME
        fSWMEInputFlowRate = abs(self.oIn.oPhase.toProcsEXME.WaterIn.oFlow.fFlowRate)

        # Set mass flow through membrane
        self.setMatterProperties(self.fWaterVaporFlowRate, self.arExtractPartials)

        # Evaporation enthalpy and heat rejection
        fEvaporationEnthalpy = self.calculateEvaporationEnthalpy(self.fMeanTemperature)
        self.fHeatRejection = self.fWaterVaporFlowRate * fEvaporationEnthalpy
        self.oHeatSource.setHeatFlow(-self.fHeatRejection)

        # Simplified heat rejection
        self.fHeatRejectionSimple = fSWMEInputFlowRate * fLiquidSpecificHeatCapacity * (fWaterTemperatureInlet - fWaterTemperatureOutlet)

        # Update the back-pressure valve in parent system
        self.oStore.oContainer.updateBPVFlow(fVaporPressure)

        # Set last update time
        self.fLastUpdate = self.oStore.oTimer.fTime
