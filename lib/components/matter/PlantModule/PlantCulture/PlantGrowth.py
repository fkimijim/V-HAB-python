def PlantGrowth(self, fSimTime):
    """
    Simulate plant growth for a given simulation time.

    :param fSimTime: Simulation time
    """
    # Retrieve necessary parameters
    fDensityAtmosphere = self.oAtmosphere.fDensity
    fPressureAtmosphere = self.oAtmosphere.fMass * self.oAtmosphere.fMassToPressure
    fRelativeHumidityAtmosphere = min(self.oAtmosphere.rRelHumidity, 1)
    fHeatCapacityAtmosphere = self.oAtmosphere.oCapacity.fSpecificHeatCapacity
    fCO2 = self.fCO2

    # Calculate density of liquid water
    tH2O = {
        "sSubstance": "H2O",
        "sProperty": "Density",
        "sFirstDepName": "Pressure",
        "fFirstDepValue": self.oAtmosphere.fPressure,
        "sSecondDepName": "Temperature",
        "fSecondDepValue": self.oAtmosphere.fTemperature,
        "sPhaseType": "liquid"
    }
    fDensityH2O = self.oMT.findProperty(tH2O)

    # Growth logic for current generation
    if self.iInternalGeneration <= self.txInput.iConsecutiveGenerations:
        if self.fInternalTime < self.txInput.fHarvestTime * 86400 and self.iState == 1:
            # Calculate internal time
            self.fInternalTime = fSimTime - self.fSowTime

            # Check CO2 level and calculate MMEC rates
            if 330 <= fCO2 <= 1300:
                self.tfMMECRates = self.CalculateMMECRates(
                    self.fInternalTime, fPressureAtmosphere, fDensityAtmosphere,
                    fRelativeHumidityAtmosphere, fHeatCapacityAtmosphere, fDensityH2O, fCO2
                )
            elif fCO2 > 1300:
                self.tfMMECRates = self.CalculateMMECRates(
                    self.fInternalTime, fPressureAtmosphere, fDensityAtmosphere,
                    fRelativeHumidityAtmosphere, fHeatCapacityAtmosphere, fDensityH2O,
                    self.txPlantParameters.fCO2_Ref_Max
                )
            elif 150 < fCO2 < 330:
                self.tfMMECRates = self.CalculateMMECRates(
                    self.fInternalTime, fPressureAtmosphere, fDensityAtmosphere,
                    fRelativeHumidityAtmosphere, fHeatCapacityAtmosphere, fDensityH2O,
                    self.txPlantParameters.fCO2_Ref_Min
                )
            else:
                # Set all MMEC rates to zero
                self.tfMMECRates = {k: 0 for k in ["fWC", "fTR", "fOC", "fOP", "fCO2C", "fCO2P", "fNC", "fCGR"]}

            # Calculate culture mass transfer rates
            self.tfGasExchangeRates["fO2ExchangeRate"] = (self.tfMMECRates["fOP"] - self.tfMMECRates["fOC"]) * self.txInput.fGrowthArea
            self.tfGasExchangeRates["fCO2ExchangeRate"] = (self.tfMMECRates["fCO2P"] - self.tfMMECRates["fCO2C"]) * self.txInput.fGrowthArea
            self.tfGasExchangeRates["fTranspirationRate"] = self.tfMMECRates["fTR"] * self.txInput.fGrowthArea
            self.fWaterConsumptionRate = self.tfMMECRates["fWC"] * self.txInput.fGrowthArea
            self.fNutrientConsumptionRate = self.tfMMECRates["fNC"] * self.txInput.fGrowthArea

            # Biomass growth
            if self.fInternalTime >= self.txPlantParameters.fT_E * 86400:
                self.tfBiomassGrowthRates["fGrowthRateEdible"] = (
                    self.tfMMECRates["fCGR"] * self.txInput.fGrowthArea * self.txPlantParameters.fXFRT
                ) * (self.txPlantParameters.fFBWF_Edible + 1)
                self.tfBiomassGrowthRates["fGrowthRateInedible"] = (
                    self.tfMMECRates["fCGR"] * self.txInput.fGrowthArea * (1 - self.txPlantParameters.fXFRT)
                ) * (self.txPlantParameters.fFBWF_Inedible + 1)
            else:
                self.tfBiomassGrowthRates["fGrowthRateEdible"] = 0
                self.tfBiomassGrowthRates["fGrowthRateInedible"] = self.tfMMECRates["fWCGR"] * self.txInput.fGrowthArea

            # Update water consumption rate for mass balance
            self.fWaterConsumptionRate += (
                self.tfBiomassGrowthRates["fGrowthRateEdible"] + self.tfBiomassGrowthRates["fGrowthRateInedible"]
            )
        else:
            # Transition to harvest state
            if self.iState == 1:
                self.iState = 2
                self.tfMMECRates = {k: 0 for k in self.tfMMECRates}
                self.fWaterConsumptionRate = 0
                self.fNutrientConsumptionRate = 0
                self.tfGasExchangeRates = {k: 0 for k in self.tfGasExchangeRates}
                self.tfBiomassGrowthRates = {k: 0 for k in self.tfBiomassGrowthRates}
            else:
                self.fWaterConsumptionRate = 0
                self.fNutrientConsumptionRate = 0
                self.tfGasExchangeRates = {k: 0 for k in self.tfGasExchangeRates}
                self.tfBiomassGrowthRates = {k: 0 for k in self.tfBiomassGrowthRates}

    # Nutrient uptake mechanism based on Michaelis-Menten kinetics
    oPlantPhase = self.toStores.Plant_Culture.toPhases.Plants
    fPlantYield_equivalent = (oPlantPhase.fMass / self.txInput.fGrowthArea) * self.txPlantParameters.fDRY_Fraction

    # Michaelis-Menten constants
    fK_m = 0.2
    fI_max = 1.25e-4

    # Calculate nutrient uptake rates
    fWaterFlow = -self.toBranches.WaterSupply_In.fFlowRate
    rNO3 = self.toBranches.WaterSupply_In.aoFlows[0].arPartialMass[self.oMT.tiN2I["NO3"]]
    fDensity = self.toBranches.WaterSupply_In.aoFlows[0].getDensity()
    fNO3Flow = fWaterFlow * rNO3

    fSolutionNO3MolarFlow = fNO3Flow / self.oMT.afMolarMass[self.oMT.tiN2I["NO3"]]
    fSolutionConcentration_NO3 = 0 if fWaterFlow == 0 else fSolutionNO3MolarFlow / (fWaterFlow / fDensity)

    fMolarUptakeStorage_NO3 = (fI_max * fSolutionConcentration_NO3) / (fK_m + fSolutionConcentration_NO3)
    fMassUptakeStorage_NO3 = (
        fMolarUptakeStorage_NO3
        * self.oMT.afMolarMass[self.oMT.tiN2I["NO3"]]
        * ((oPlantPhase.fMass * self.txPlantParameters.fDRY_Fraction) + 1e-3)
    )

    # Remaining nutrient uptake logic...
    # The rest of the method continues as per the logic in the MATLAB script
