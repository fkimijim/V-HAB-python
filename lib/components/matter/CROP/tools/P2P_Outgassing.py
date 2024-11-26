import CO2_Outgassing, NH3_Outgassing

class P2P_Outgassing:
    """
    This P2P processor determines the theoretical mass of a gas component in the gas
    phase above a solution at equilibrium, influenced by the gas concentration inside the
    solution. If there is a discrepancy between the calculated mass value
    and the current actual mass concentration in the gas phase, the P2P adjusts
    the flow rate between solution and gas phase.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sSubstance):
        self.oStore = oStore
        self.sName = sName
        self.sPhaseIn = sPhaseIn
        self.sPhaseOut = sPhaseOut
        self.sSubstance = sSubstance
        self.fLastExecp2p = 0

        # Initialize the extracting percentage of the gas
        self.arExtractPartials = [0] * self.oStore.oMT.iSubstances
        self.arExtractPartials[self.oStore.oMT.tiN2I[self.sSubstance]] = 1

        self.oTankSolution = self.oStore.oContainer.toStores["CROP_Tank"].toPhases["TankSolution"]
        self.opH_Manip = self.oStore.oContainer.toStores["CROP_Tank"].toPhases["Aeration"].toManips["substance"]

    def update(self):
        # Current temperature of the solution
        fCurrentTemp = self.sPhaseIn.fTemperature

        # Current concentration of OH_minus in the solution
        fCurrentOH = 10 ** -(14 - self.opH_Manip.fpH)

        # Current concentration of NH3 in the solution in mol/L
        fCurrentNH3aq = self.sPhaseIn.afMass[self.oStore.oMT.tiN2I["NH3"]] / (
            self.oStore.oMT.afMolarMass[self.oStore.oMT.tiN2I["NH3"]] * self.sPhaseIn.fVolume
        )

        # Current concentration of NH4 in the solution in mol/L
        fCurrentNH4aq = self.sPhaseIn.afMass[self.oStore.oMT.tiN2I["NH4"]] / (
            self.oStore.oMT.afMolarMass[self.oStore.oMT.tiN2I["NH4"]] * self.sPhaseIn.fVolume
        )

        # Depending on the gas, calculate theoretical gas concentration
        if self.sSubstance == "NH3":
            fCO2_gas_concentration, fH_cc_CO2 = CO2_Outgassing(
                fCurrentTemp, self.sPhaseOut.afPP[self.oStore.oMT.tiN2I["NH3"]]
            )
            fgas_concentration_mol = NH3_Outgassing(
                fCurrentTemp, fCurrentOH, fCurrentNH3aq, fCurrentNH4aq, fCO2_gas_concentration, fH_cc_CO2
            )
        elif self.sSubstance == "CO2":
            fgas_concentration_mol, _ = CO2_Outgassing(
                fCurrentTemp, self.sPhaseOut.afPP[self.oStore.oMT.tiN2I["CO2"]]
            )

        # Convert molar concentration to mass
        fgas_mass = (
            fgas_concentration_mol
            * self.oStore.oMT.afMolarMass[self.oStore.oMT.tiN2I[self.sSubstance]]
            * self.sPhaseIn.fVolume
        )

        # Calculate the current gas mass in the gas phase
        fPhaseGasMass = self.sPhaseOut.afMass[self.oStore.oMT.tiN2I[self.sSubstance]]
        fCurrentPhaseMassChange = (
            self.sPhaseIn.afCurrentTotalInOuts[self.oStore.oMT.tiN2I[self.sSubstance]] - self.fFlowRate
        )

        # P2P flow rate from liquid to gas
        fFlowRate = (fPhaseGasMass - fgas_mass) / (2 * self.oStore.oContainer.fTimeStep)

        if fFlowRate > 0:
            if fFlowRate < -fCurrentPhaseMassChange:
                fFlowRate = 0
            else:
                fFlowRate += fCurrentPhaseMassChange

        # Extract the substance from the input phase according to the mass flow rate
        self.setMatterProperties(fFlowRate, self.arExtractPartials)

        # Record the last execution time
        self.fLastExecp2p = self.oStore.oTimer.fTime

    def setMatterProperties(self, fFlowRate, arExtractPartials):
        """
        Sets the matter properties for the flow rate and partials.
        This is a placeholder for the actual implementation in the matter system.
        """
        pass
