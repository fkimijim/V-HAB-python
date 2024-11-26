import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.p2ps.flow import flow

flow = flow()

class Filter(flow):
    """
    A p2p processor implementation for absorption behavior.
    This class demonstrates filtering a specific substance from a flow.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sSubstance, fCapacity, fCharacteristics=1):
        """
        Initializes the filter object.

        Parameters:
        - oStore: The matter store to which this filter belongs.
        - sName: Name of the filter.
        - sPhaseIn: Input phase name.
        - sPhaseOut: Output phase name.
        - sSubstance: Substance to absorb.
        - fCapacity: Maximum absorption capacity in kg.
        - fCharacteristics: Exponent for absorption characteristics (default: 1).
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

        self.sSubstance = sSubstance
        self.fCapacity = fCapacity
        self.fCharacteristics = fCharacteristics
        self.fMaxAbsorption = 1e-9
        self.rLoad = 0

        # Initialize the extraction partials vector
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I[self.sSubstance]] = 1

    def calculateFlowRate(self, afFlowRate, mrPartials):
        """
        Calculates the flow rate of the substance being filtered.

        Parameters:
        - afFlowRate: Array of input flow rates.
        - mrPartials: Array of partial mass fractions for each substance.

        Returns:
        - fFlowRate: The calculated flow rate for the substance.
        - arExtractPartials: The extraction partials vector.
        """
        arExtractPartials = self.arExtractPartials
        iSpecies = self.oMT.tiN2I[self.sSubstance]

        # Determine the loading ratio of the filter
        self.rLoad = self.oOut.oPhase.afMass[iSpecies] / self.fCapacity if self.fCapacity > 0 else 1

        if not afFlowRate or sum(afFlowRate) == 0:
            # No flow, return zero flow rate
            return 0, arExtractPartials

        # Compute the flow rates for the target species
        afFlowRate = [flow * mrPartials[i][iSpecies] for i, flow in enumerate(afFlowRate)]

        # Calculate the adsorption rate based on the load and characteristics
        rAdsorp = (1 - self.rLoad**self.fCharacteristics) if self.fCharacteristics > 0 else 1

        # Total flow rate for the substance being filtered
        fFlowRate = rAdsorp * sum(afFlowRate)

        # Debug output (if enabled)
        if not base.oDebug.bOff:
            self.out(1, 1, "calc-fr", f"p2p calc flowrate of {self.sName}, ads rate {rAdsorp} is: {fFlowRate:.34f}")
            self.out(1, 2, "calc-fr", f"{afFlowRate}")

        return fFlowRate, arExtractPartials

    def update(self):
        """
        Updates the filter's flow rate based on current conditions.
        """
        if not base.oDebug.bOff:
            self.out(1, 1, "set-fr", f"p2p update flowrate of {self.sName}")

        # Get input flows and partial fractions
        afFlowRate, aarPartials = self.getInFlows()

        # Calculate the new flow rate for the filtered substance
        fFlowRate, _ = self.calculateFlowRate(afFlowRate, aarPartials)

        # Set the new flow rate
        self.setMatterProperties(fFlowRate, self.arExtractPartials)
