class MLS(matter.procs.p2ps.flow):
    """
    MLS (Molecular sieve) removes 99.975% of the incoming gases.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut):
        """
        Initialize the MLS processor.
        
        :param oStore: The store to which the processor belongs.
        :param sName: Name of the processor.
        :param sPhaseIn: Input phase.
        :param sPhaseOut: Output phase.
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

    def calculateFlowRate(self, afInsideInFlowRate, aarInsideInPartials, *args):
        """
        Calculate the flow rate for the MLS processor.
        
        :param afInsideInFlowRate: Array of input flow rates.
        :param aarInsideInPartials: Array of input partial flow rates.
        """
        afPartialInFlows = (afInsideInFlowRate * aarInsideInPartials).sum(axis=0)

        # Default partial pressures for all substances
        afPP = [1e5] * self.oMT.iSubstances

        # Determine phases of substances based on flows, temperature, and partial pressures
        miPhases = self.oMT.determinePhase(afPartialInFlows, 293, afPP)

        abGas = miPhases == 3  # Identify gaseous substances

        # Special cases: Chloride and formaldehyde are not gases
        abGas[self.oMT.tiN2I["Clminus"]] = 0
        abGas[self.oMT.tiN2I["CH2O"]] = 0

        # Calculate the partial flow rates of gases
        afPartialFlowRatesGases = [0] * self.oMT.iSubstances
        for i in range(len(abGas)):
            if abGas[i]:
                afPartialFlowRatesGases[i] = afPartialInFlows[i]

        # Total gas flow rate
        fFlowRate = sum(afPartialFlowRatesGases)

        if fFlowRate == 0:
            arExtractPartials = [0] * self.oMT.iSubstances
        else:
            arExtractPartials = [flow / fFlowRate for flow in afPartialFlowRatesGases]

        # Set flow rates to 99.975% of the incoming gases
        self.setMatterProperties(fFlowRate * 0.99975, arExtractPartials)

    def update(self):
        """
        Update method for MLS (does nothing in this implementation).
        """
        pass
