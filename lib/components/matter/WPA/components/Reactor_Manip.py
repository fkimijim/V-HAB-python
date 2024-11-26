class Reactor_Manip(matter.manips.substance.flow):
    """
    Models the reactor in V-HAB based on:
    Two-Phase Oxidizing Flow in Volatile Removal Assembly Reactor Under Microgravity Conditions
    written by Boyun Guo, Donald W. Holder, and John T. Tester.
    """
    def __init__(self, sName, oPhase):
        super().__init__(sName, oPhase)

        self.fReactorLength = 1.12  # [m]
        self.fBubbleVelocity = 0.0018  # [m/s] 0.18 cm/s
        self.fBubbleRadius = 0.139 / 2  # [m]
        self.rSphericityOxygenBubbles = 0.5  # small_diameter/large_diameter
        self.fOxidationRate = -5.15 * 10**-4  # [kg/m^2]
        self.fResidenceTime = 0  # the time the water stays in the reactor
        self.afFlowRates = [0] * self.oPhase.oMT.iSubstances

        self.arStochiometricO2Ratio = [0] * self.oMT.iSubstances
        self.arStochiometricCO2Ratio = [0] * self.oMT.iSubstances
        self.arStochiometricH2ORatio = [0] * self.oMT.iSubstances
        self.arStochiometricN2Ratio = [0] * self.oMT.iSubstances

        self.abVolatile = [False] * self.oMT.iSubstances

        # Define stoichiometric ratios
        # C2H6O + 3 O2 -> 2 CO2 + 3 H2O
        self.arStochiometricO2Ratio[self.oMT.tiN2I["C2H6O"]] = 3
        self.arStochiometricCO2Ratio[self.oMT.tiN2I["C2H6O"]] = 2
        self.arStochiometricH2ORatio[self.oMT.tiN2I["C2H6O"]] = 3

        # CH2O2 + 0.5 O2 -> CO2 + H2O
        self.arStochiometricO2Ratio[self.oMT.tiN2I["CH2O2"]] = 0.5
        self.arStochiometricCO2Ratio[self.oMT.tiN2I["CH2O2"]] = 1
        self.arStochiometricH2ORatio[self.oMT.tiN2I["CH2O2"]] = 1

        # Additional stoichiometric reactions here...

        # Mark volatiles based on defined stoichiometric ratios
        for i, ratio in enumerate(self.arStochiometricO2Ratio):
            if ratio != 0:
                self.abVolatile[i] = True

        # Calculate residence time
        self.fResidenceTime = (self.oPhase.oStore.fVolume * 1000) / self.oPhase.oStore.oContainer.fFlowRate

    def calculateConversionRate(self, afInFlowRates, aarInPartials, *_):
        """
        Calculate the conversion rate of volatiles in the reactor.

        :param afInFlowRates: Array of input flow rates.
        :param aarInPartials: Array of input partial flow rates.
        """
        # Calculate partial inflows
        afPartialInFlows = [sum(flow * partial for flow, partial in zip(afInFlowRates, col))
                            for col in zip(*aarInPartials)]
        afPartialInFlows = [max(0, flow) for flow in afPartialInFlows]  # Ensure no negative values

        # Calculate the amount of organics to remove
        afOrganicsToRemove = [flow * self.fResidenceTime for i, flow in enumerate(afPartialInFlows) if self.abVolatile[i]]

        if all(flow == 0 for flow in afOrganicsToRemove):
            self.afFlowRates = [0] * self.oMT.iSubstances
        else:
            Density_O2 = 4.2817311450828  # [kg/m^3] Density of O2 at reactor conditions

            # Oxygen utilization factor (Equation 3)
            rOxygenUtilization = 1 - math.exp(
                ((3 * self.fOxidationRate * self.rSphericityOxygenBubbles) /
                 (self.fBubbleRadius * Density_O2 * self.fBubbleVelocity)) * self.fReactorLength)

            # Oxygen injection rate
            fOxygenInjection = (self.oPhase.oStore.toProcsP2P.ReactorOxygen_P2P.fFlowRate *
                                self.oPhase.oStore.toProcsP2P.ReactorOxygen_P2P.arPartialMass[self.oMT.tiN2I["O2"]])

            if fOxygenInjection == 0:
                self.afFlowRates = [0] * self.oMT.iSubstances
            else:
                # Oxygen mass consumption potential (Equation 5)
                fOxygenMassConsumptionPotential = rOxygenUtilization * fOxygenInjection * self.fResidenceTime

                # Calculate removed organics (Equation 6)
                afRemovedOrganics = [
                    fOxygenMassConsumptionPotential *
                    self.oMT.afMolarMass[i] /
                    (self.arStochiometricO2Ratio[i] * self.oMT.afMolarMass[self.oMT.tiN2I["O2"]])
                    for i in range(len(self.abVolatile)) if self.abVolatile[i]
                ]

                # Removal efficiencies
                arRemovalEfficiencies = [1] * self.oMT.iSubstances
                for i in range(len(afOrganicsToRemove)):
                    if afOrganicsToRemove[i] > 0:
                        arRemovalEfficiencies[i] = max(0, 1 - afRemovedOrganics[i] / afOrganicsToRemove[i])

                afReactedVolatiles = [flow * eff for flow, eff in zip(afPartialInFlows, arRemovalEfficiencies)]
                afReactedVolatilesMols = [flow / self.oMT.afMolarMass[i] for i, flow in enumerate(afReactedVolatiles)]

                afReactedO2Mols = [mol * self.arStochiometricO2Ratio[i] for i, mol in enumerate(afReactedVolatilesMols)]
                afProducedCO2Mols = [mol * self.arStochiometricCO2Ratio[i] for i, mol in enumerate(afReactedVolatilesMols)]
                afProducedH2OMols = [mol * self.arStochiometricH2ORatio[i] for i, mol in enumerate(afReactedVolatilesMols)]
                afProducedN2Mols = [mol * self.arStochiometricN2Ratio[i] for i, mol in enumerate(afReactedVolatilesMols)]

                fO2Consumption = sum(afReactedO2Mols) * self.oMT.afMolarMass[self.oMT.tiN2I["O2"]]
                fCO2Production = sum(afProducedCO2Mols) * self.oMT.afMolarMass[self.oMT.tiN2I["CO2"]]
                fH2OProduction = sum(afProducedH2OMols) * self.oMT.afMolarMass[self.oMT.tiN2I["H2O"]]
                fN2Production = sum(afProducedN2Mols) * self.oMT.afMolarMass[self.oMT.tiN2I["N2"]]

                self.afFlowRates = [-reacted for reacted in afReactedVolatiles]
                self.afFlowRates[self.oMT.tiN2I["O2"]] = -fO2Consumption
                self.afFlowRates[self.oMT.tiN2I["CO2"]] = fCO2Production
                self.afFlowRates[self.oMT.tiN2I["H2O"]] = fH2OProduction
                self.afFlowRates[self.oMT.tiN2I["N2"]] = fN2Production

        self.update()

    def update(self):
        super().update(self.afFlowRates)
