class AbsorberExample(matter.procs.p2ps.stationary):
    """
    ABSORBEREXAMPLE: Example implementation of a P2P processor
    The actual logic behind the absorption behavior is not based on any
    specific physical system. It demonstrates the use of P2P processors.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, fLinearDrivingForceParameter=1e-3):
        """
        Initialize the AbsorberExample P2P.

        :param oStore: Store object in V-HAB
        :param sName: Name of this P2P
        :param sPhaseIn: Phase or string ('StoreName.ExMeName') for the input phase
        :param sPhaseOut: Phase or string ('StoreName.ExMeName') for the output phase
        :param fLinearDrivingForceParameter: Parameter for the adsorption rate (default 1e-3 s)
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)
        self.arLoadingRatio = None
        self.fLinearDrivingForceParameter = fLinearDrivingForceParameter

    def update(self):
        """
        Update method executed during the simulation.
        """

        # Get the partial pressures of the input phase
        afPP = self.oIn.oPhase.afPP

        # Store a reference to the adsorber phase for easier access
        oAdsorberPhase = self.oOut.oPhase

        # Calculate the equilibrium loading of the filter
        afEquilibriumLoading = self.oMT.calculateEquilibriumLoading(
            oAdsorberPhase.afMass, afPP, oAdsorberPhase.fTemperature
        )

        # Calculate the current loading
        afLoading = oAdsorberPhase.afMass / sum(oAdsorberPhase.afMass[self.oMT.abAbsorber])

        # Calculate the ratio between actual loading and equilibrium loading
        self.arLoadingRatio = afLoading / afEquilibriumLoading

        # Calculate adsorption flowrates using the linear driving force approach
        afAdsorptionFlowrates = self.fLinearDrivingForceParameter * (afEquilibriumLoading - afLoading)

        # Ensure no negative flowrates (no desorption handled here)
        afAdsorptionFlowrates[afAdsorptionFlowrates < 0] = 0

        # Sum of the adsorption flowrates
        fFlowRate = sum(afAdsorptionFlowrates)

        # Calculate the partial mass ratios
        if fFlowRate != 0:
            arExtractPartials = afAdsorptionFlowrates / fFlowRate
        else:
            arExtractPartials = [0] * self.oMT.iSubstances

        # Set the flowrate and partial mass ratios for this P2P
        self.setMatterProperties(fFlowRate, arExtractPartials)
