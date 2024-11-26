class MicrobialCheckValve:
    """
    Represents a microbial check valve in a fluid system. The valve only
    allows fluid to pass in one direction and blocks flow based on
    contamination thresholds.
    """

    def __init__(self, oContainer, sName, bInitialOpen, oOtherValve, abContaminants):
        """
        Initializes the microbial check valve.
        
        :param oContainer: The container to which the valve belongs.
        :param sName: Name of the valve.
        :param bInitialOpen: Boolean indicating if the valve starts open.
        :param oOtherValve: Reference to the other valve.
        :param abContaminants: Boolean array for contaminants to monitor.
        """
        self.oContainer = oContainer
        self.sName = sName
        self.bOpen = bInitialOpen
        self.oOtherValve = oOtherValve
        self.abContaminants = abContaminants
        
        self.fPressureDrop = 0
        self.fFlowThroughPressureDropCoefficient = 0
        self.bAlwaysOpen = False
        self.fTOC = 0
        self.fPPM = 0
        
        self.afCarbonAtomsInMolecule = [0] * oContainer.oMT.iSubstances
        
        for iSubstance in range(oContainer.oMT.iSubstances):
            sSubstance = oContainer.oMT.csI2N[iSubstance]
            tAtmos = oContainer.oMT.extractAtomicTypes(sSubstance)
            if "C" in tAtmos:
                self.afCarbonAtomsInMolecule[iSubstance] = tAtmos["C"]
        
        self.supportSolver("callback", self.solverDeltas)

    def switchAlwaysOpen(self, bAlwaysOpen):
        """
        Sets the valve to always open or disables the always-open mode.
        
        :param bAlwaysOpen: Boolean to enable or disable always-open mode.
        """
        self.bAlwaysOpen = bAlwaysOpen

    def solverDeltas(self, fFlowRate):
        """
        Solver callback to determine the pressure drop based on flow rate.
        
        :param fFlowRate: Flow rate through the valve.
        :return: Calculated pressure drop.
        """
        # Handle iterative solvers to prevent oscillations during convergence
        try:
            if not self.oContainer.oBranch.oHandler.bFinalLoop:
                return self.fPressureDrop
        except AttributeError:
            pass  # Always calculate for non-iterative solvers

        # Handle no flow or reverse flow
        if fFlowRate <= 0:
            self.fPressureDrop = 0
            self.bOpen = True
        elif self.bAlwaysOpen:
            self.fPressureDrop = 0
            self.bOpen = True
        else:
            # Calculate TOC and PPM
            arInFlowMassRatios = self.oContainer.aoFlows[0].arPartialMass
            afPPM = self.oContainer.oMT.calculatePPM(arInFlowMassRatios)
            self.fPPM = sum(afPPM[i] for i, is_contaminant in enumerate(self.abContaminants) if is_contaminant)

            # Calculate TOC in kg Carbon / total mass
            self.fTOC = sum(
                self.afCarbonAtomsInMolecule[i] *
                (arInFlowMassRatios[i] / self.oContainer.oMT.afMolarMass[i]) *
                self.oContainer.oMT.afMolarMass[self.oContainer.oMT.tiN2I["C"]]
                for i in range(len(arInFlowMassRatios))
            )

            # Determine if limits are exceeded
            if self.fTOC > 0.2e-6 or self.fPPM > 16:
                self.fPressureDrop = float("inf")
                self.bOpen = False
            else:
                self.fPressureDrop = 0
                self.bOpen = True

        # Set the state of the other valve
        self.oOtherValve.setOpen(not self.bOpen)

        return self.fPressureDrop

    def supportSolver(self, solver_type, solver_function):
        """
        Registers a solver callback for this valve.
        
        :param solver_type: Type of solver.
        :param solver_function: Callback function for the solver.
        """
        # Placeholder implementation for solver support
        pass
