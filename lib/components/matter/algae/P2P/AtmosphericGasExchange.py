class AtmosphericGasExchange:
    """
    AtmosphericGasExchange calculates the rate of solution into and volatility out of water 
    for CO2 or O2 using Henry's Law. Includes calculations for membrane transport if applicable.
    """

    def __init__(self, oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P, sSubstance):
        """
        Constructor for AtmosphericGasExchange.

        :param oStore: Store containing phases for gas and medium.
        :param sName: Name of the process.
        :param sExmePhaseIntoP2P: Phase from which substance enters the P2P.
        :param sExmePhaseOutofP2P: Phase to which substance exits the P2P.
        :param sSubstance: Substance to calculate exchange for ('CO2' or 'O2').
        """
        self.oStore = oStore
        self.sName = sName
        self.sExmePhaseIntoP2P = sExmePhaseIntoP2P
        self.sExmePhaseOutofP2P = sExmePhaseOutofP2P
        self.sSubstance = sSubstance

        self.arExtractPartials = [0] * oStore.oMT.iSubstances
        self.arExtractPartials[oStore.oMT.tiN2I[sSubstance]] = 1
        self.fLastExec = 0  # [s]

        # Membrane-related properties
        parent = oStore.oContainer.oParent
        self.sMembraneMaterial = parent.sMembraneMaterial
        self.fMembraneArea = parent.fMembraneSurface  # [m2]
        self.fMembraneThickness = parent.fMembraneThickness  # [m]

        # Set Henry's Law constants and membrane properties based on substance
        if sSubstance == 'CO2':
            self.fNormalHenryConstant = 3.3e-4  # [mol/(m3*Pa)]
            self.fTemperatureDependence = 2300  # [K]
            self.fPrefixFlowFactor = 1  # Positive for CO2
            self.fMembranePermeability = (
                8.438e-13 if self.sMembraneMaterial == 'SSP-M823 Silicone' else 6.292e-13
            )  # [mol*m/(m2*s*Pa)]
        elif sSubstance == 'O2':
            self.fNormalHenryConstant = 1.3e-5  # [mol/(m3*Pa)]
            self.fTemperatureDependence = 1500  # [K]
            self.fPrefixFlowFactor = -1  # Negative for O2
            self.fMembranePermeability = (
                1.563e-13 if self.sMembraneMaterial == 'SSP-M823 Silicone' else 2.488e-13
            )  # [mol*m/(m2*s*Pa)]

    def update(self):
        """
        Update function for calculating gas exchange based on Henry's Law
        and membrane transport if applicable.
        """
        # Retrieve phase parameters for gas and liquid
        growth_medium = self.oStore.toPhases.GrowthMedium
        air_in_chamber = self.oStore.toPhases.AirInGrowthChamber

        self.fTemperatureOfMedium = growth_medium.fTemperature  # [K]
        self.fCurrentMolesOfSubstanceInMedium = (
            growth_medium.afMass[self.oStore.oMT.tiN2I[self.sSubstance]] /
            self.oStore.oMT.ttxMatter[self.sSubstance].fMolarMass
        )  # [mol]
        self.fPartialPressureOfSubstanceInAir = air_in_chamber.afPP[self.oStore.oMT.tiN2I[self.sSubstance]]  # [Pa]

        # Calculate current Henry's Law constant
        self.fCurrentHenryConstant = self.fNormalHenryConstant * \
            (self.fTemperatureDependence *
             ((1 / self.fTemperatureOfMedium) - (1 / 298.15)))  # [mol/(m3*Pa)]

        # Calculate concentrations and target values
        water_mass = growth_medium.afMass[self.oStore.oMT.tiN2I['H2O']]
        medium_density = self.oStore.oContainer.fCurrentGrowthMediumDensity

        self.fCurrentSubstanceInWaterConcentration = (
            self.fCurrentMolesOfSubstanceInMedium / (water_mass / medium_density)
        )  # [mol/m3]
        self.fTargetSubstanceInWaterConcentration = (
            self.fCurrentHenryConstant * self.fPartialPressureOfSubstanceInAir
        )  # [mol/m3]

        self.fTargetMolesOfSubstanceInMedium = self.fTargetSubstanceInWaterConcentration * (water_mass / 1000)  # [mol]

        # Time since last execution
        fElapsedTime = self.oStore.oTimer.fTime - self.fLastExec  # [s]

        if self.sMembraneMaterial == 'none':
            # Without membrane
            self.fMoleDifference = self.fTargetMolesOfSubstanceInMedium - self.fCurrentMolesOfSubstanceInMedium  # [mol]
            self.fMassDifference = (
                self.fMoleDifference * self.oStore.oMT.ttxMatter[self.sSubstance].fMolarMass
            )  # [kg]

            if fElapsedTime <= 0:
                return

            fFlowRate = self.fMassDifference / fElapsedTime  # [kg/s]
        else:
            # With membrane
            self.fEquivalentPartialPressure = (
                self.fCurrentSubstanceInWaterConcentration / self.fCurrentHenryConstant
            )  # [Pa]
            self.fPressureGradient = (
                self.fPartialPressureOfSubstanceInAir - self.fEquivalentPartialPressure
            )  # [Pa]

            self.fMaximumTransportRate = (
                self.fMembranePermeability * self.fPressureGradient * self.fMembraneArea /
                self.fMembraneThickness
            )  # [mol/s]

            fFlowRate = (
                self.fMaximumTransportRate * self.oStore.oMT.ttxMatter[self.sSubstance].fMolarMass
            )  # [kg/s]

        # Set flow rate and update last execution time
        self.setMatterProperties(fFlowRate, self.arExtractPartials)
        self.fLastExec = self.oStore.oTimer.fTime

        # Calculate flow factor
        photosynthesis_flow = abs(
            growth_medium.toManips.substance.afPartialFlowRatesFromPhotosynthesis[
                self.oStore.oMT.tiN2I[self.sSubstance]
            ]
        )

        if photosynthesis_flow > 0:
            self.fFlowFactor = (
                self.fPrefixFlowFactor * self.fMaximumTransportRate *
                self.oStore.oMT.ttxMatter[self.sSubstance].fMolarMass / photosynthesis_flow
            )  # [-]
        else:
            self.fFlowFactor = 0  # [-]

    def setMatterProperties(self, fFlowRate, arExtractPartials):
        """
        Set the properties for matter flow.

        :param fFlowRate: Flow rate [kg/s].
        :param arExtractPartials: Array of extraction partials.
        """
        # Implement the logic to set matter properties here
        pass
