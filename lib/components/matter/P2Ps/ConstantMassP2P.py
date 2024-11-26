class ConstantMassP2P(matter.procs.p2ps.stationary):
    """
    This P2P is designed to keep the mass of the specified substances on
    its input side constant with regard to the mass value initially present.
    The constant mass can also be overwritten by using the `setSubstances`
    function to reset to the current values in the `In` phase for the newly
    defined substances.
    """

    def __init__(self, oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut, csSubstances, iDirection):
        super().__init__(oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut)
        
        # Transform substances to indices for performance
        self.aiSubstances = [self.oMT.tiN2I[substance] for substance in csSubstances]
        
        self.afConstantMass = [0] * self.oMT.iSubstances
        for idx in self.aiSubstances:
            self.afConstantMass[idx] = self.oIn.oPhase.afMass[idx]
        
        self.iDirection = iDirection
        self.afFlowRates = [0] * self.oMT.iSubstances
        self.fLastExec = 0
        
        self.hBindPostTickInternalUpdate = self.oTimer.registerPostTick(
            self.calculateFlowRates, 'matter', 'pre_multibranch_solver'
        )
        
        if self.iDirection == 1:
            self.oIn.oPhase.bind('massupdate_post', self.bindInternalUpdate)
        else:
            self.oOut.oPhase.bind('massupdate_post', self.bindInternalUpdate)

        if self.iDirection == 1:
            oPhase = self.oIn.oPhase
        else:
            oPhase = self.oOut.oPhase

        self.iPhaseExmeNumber = None
        for iExme, exme in enumerate(oPhase.coProcsEXME, start=1):
            if exme.oFlow == self:
                self.iPhaseExmeNumber = iExme
                break

        self.bInternalUpdateRegistered = False

    def setSubstances(self, csSubstances):
        """
        Update the substances to maintain constant mass.
        """
        self.aiSubstances = [self.oMT.tiN2I[substance] for substance in csSubstances]
        self.afConstantMass = [0] * self.oMT.iSubstances
        for idx in self.aiSubstances:
            self.afConstantMass[idx] = self.oIn.oPhase.afMass[idx]

    def bindInternalUpdate(self, _):
        """
        Register internal update for the post-tick phase.
        """
        if not self.bInternalUpdateRegistered:
            self.hBindPostTickInternalUpdate()
            self.bInternalUpdateRegistered = True

    def calculateFlowRates(self):
        """
        Calculate the flow rates needed to maintain the constant mass for
        the specified substances.
        """
        oPhase = self.oIn.oPhase if self.iDirection == 1 else self.oOut.oPhase
        
        afCurrentFlowRates = [0] * self.oMT.iSubstances
        for iExme, exme in enumerate(oPhase.coProcsEXME, start=1):
            if iExme != self.iPhaseExmeNumber:
                afCurrentFlowRates = [
                    current + exme.iSign * exme.oFlow.fFlowRate * exme.oFlow.arPartialMass[idx]
                    for idx, current in enumerate(afCurrentFlowRates)
                ]

        self.afFlowRates = [0] * self.oMT.iSubstances
        for idx in self.aiSubstances:
            self.afFlowRates[idx] = -afCurrentFlowRates[idx]

        if (
            self.oIn.oPhase.fLastMassUpdate == self.oTimer.fTime and
            self.oOut.oPhase.fLastMassUpdate == self.oTimer.fTime
        ):
            self.update()
        else:
            self.oIn.oPhase.registerMassupdate()
            self.oOut.oPhase.registerMassupdate()

        self.bInternalUpdateRegistered = False

    def update(self, _=None):
        """
        Update the flow rates in the P2P processor.
        """
        fFlowRate = sum(self.afFlowRates)
        if fFlowRate == 0:
            arPartialFlowRates = [0] * self.oMT.iSubstances
        else:
            arPartialFlowRates = [rate / fFlowRate for rate in self.afFlowRates]

        super().update(fFlowRate, arPartialFlowRates)
