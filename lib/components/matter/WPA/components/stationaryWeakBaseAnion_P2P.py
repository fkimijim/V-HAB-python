class StationaryWeakBaseAnion_P2P(matter.procs.p2ps.stationary, components.matter.WPA.components.baseWeakBaseAnion_P2P):
    """
    Represents a stationary weak base anion P2P process.
    Combines the functionality of the stationary P2P and the baseWeakBaseAnion_P2P components.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, oDesorptionP2P):
        """
        Constructor for the StationaryWeakBaseAnion_P2P class.

        :param oStore: Reference to the store this P2P belongs to.
        :param sName: Name of the P2P processor.
        :param sPhaseIn: Name of the input phase.
        :param sPhaseOut: Name of the output phase.
        :param oDesorptionP2P: Reference to the desorption P2P processor.
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)
        components.matter.WPA.components.baseWeakBaseAnion_P2P.__init__(self, oStore, oDesorptionP2P)

    def update(self):
        """
        Updates the flow rates for adsorption and desorption processes.
        """
        afInFlowRates, mrInPartials = self.getInFlows()

        # Calculate the current inflows
        afPartialInFlows = (afInFlowRates * mrInPartials).sum(axis=0)
        afPartialInFlows[afPartialInFlows < 0] = 0

        afPartialFlowRates = self.calculateExchangeRates(afPartialInFlows)

        afDesorptionFlowRates = [0] * self.oMT.iSubstances
        afAdsorptionFlowRates = [0] * self.oMT.iSubstances

        # Determine adsorption and desorption flow rates
        for i, rate in enumerate(afPartialFlowRates):
            if rate > 0:
                afAdsorptionFlowRates[i] = rate
            elif rate < 0:
                afDesorptionFlowRates[i] = rate

        # Limit desorption rates if no mass is available
        for i, mass in enumerate(self.oOut.oPhase.afMass):
            if mass < 1e-12:
                afDesorptionFlowRates[i] = 0

        # Calculate desorption flow rate and partials
        fDesorptionFlowRate = sum(afDesorptionFlowRates)
        if fDesorptionFlowRate == 0:
            arExtractPartialsDesorption = [0] * self.oMT.iSubstances
        else:
            arExtractPartialsDesorption = [
                rate / fDesorptionFlowRate for rate in afDesorptionFlowRates
            ]

        # Calculate adsorption flow rate and partials
        fAdsorptionFlowRate = sum(afAdsorptionFlowRates)
        if fAdsorptionFlowRate == 0:
            arExtractPartialsAdsorption = [0] * self.oMT.iSubstances
        else:
            arExtractPartialsAdsorption = [
                rate / fAdsorptionFlowRate for rate in afAdsorptionFlowRates
            ]

        # Set matter properties for adsorption
        if (
            fAdsorptionFlowRate != self.fFlowRate
            or not all(
                x == y
                for x, y in zip(arExtractPartialsAdsorption, self.arPartialMass)
            )
        ):
            self.setMatterProperties(fAdsorptionFlowRate, arExtractPartialsAdsorption)

        # Set matter properties for desorption
        if (
            fDesorptionFlowRate != self.oDesorptionP2P.fFlowRate
            or not all(
                x == y
                for x, y in zip(arExtractPartialsDesorption, self.oDesorptionP2P.arPartialMass)
            )
        ):
            self.oDesorptionP2P.setMatterProperties(
                fDesorptionFlowRate, arExtractPartialsDesorption
            )
