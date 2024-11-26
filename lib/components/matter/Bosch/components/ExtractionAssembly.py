class ExtractionAssembly:
    """
    General Extraction Assembly used for H2, CO2, and H2O.
    
    Assumptions:
        - 60% of H2 is recovered.
        - 80% of CO2 is recovered.
        - 100% of H2O is recovered.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sSubstance, rEfficiency):
        """
        Constructor for ExtractionAssembly.
        
        :param oStore: The storage object.
        :param sName: Name of the assembly.
        :param sPhaseIn: Phase where the substance flows in.
        :param sPhaseOut: Phase where the substance flows out.
        :param sSubstance: The substance to be extracted (e.g., 'H2', 'CO2').
        :param rEfficiency: The recovery efficiency (e.g., 0.6 for 60%).
        """
        self.oStore = oStore
        self.sName = sName
        self.sPhaseIn = sPhaseIn
        self.sPhaseOut = sPhaseOut
        self.sSubstance = sSubstance
        self.rEfficiency = rEfficiency

        # Initialize extraction partials: 0 for all substances except the target substance
        self.arExtractPartials = [0] * oStore.oMT.iSubstances
        self.arExtractPartials[oStore.oMT.tiN2I[sSubstance]] = 1

    def calculateFlowRate(self, afInFlowRates, aarInPartials, *_):
        """
        Calculates the flow rate based on incoming flow rates and recovery efficiency.
        
        :param afInFlowRates: Array of incoming flow rates [kg/s].
        :param aarInPartials: Array of incoming partial flows.
        """
        # Compute partial inflows for each substance
        afPartialInFlows = [sum(afInFlowRates[i] * aarInPartials[i][j] for i in range(len(afInFlowRates)))
                            for j in range(len(aarInPartials[0]))]

        # If no substance is flowing in, set flow rate to 0
        if sum(afPartialInFlows) == 0:
            self.setMatterProperties(0, self.arExtractPartials)
            return

        # Calculate flow rate based on recovery efficiency and substance inflow
        fFlowRate = self.rEfficiency * afPartialInFlows[self.oStore.oMT.tiN2I[self.sSubstance]]

        # Set the flow rate and extraction partials
        self.setMatterProperties(fFlowRate, self.arExtractPartials)

    def setMatterProperties(self, fFlowRate, arExtractPartials):
        """
        Sets the properties for matter flow.

        :param fFlowRate: The calculated flow rate [kg/s].
        :param arExtractPartials: Array of extraction partials.
        """
        # Implement the logic to update matter flow properties in the system
        pass

    def update(self):
        """
        Update method for the ExtractionAssembly.
        """
        pass
