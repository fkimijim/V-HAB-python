import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "base")))

import Branch
import Flow

BaseBranch = Branch()
MatterFlow = Flow()

class MatterBranch(BaseBranch):
    """
    MatterBranch: Base class for matter branches.
    Defines properties and methods required for all matter branches.
    """

    # Constant property to identify the object type
    sObjectType = 'branch'

    def __init__(self, oContainer, xLeft, csProcs, xRight, sCustomName=None):
        """
        Initializes a new matter branch object to transport matter between phases.

        Args:
            oContainer (object): The vsys where the branch is located.
            xLeft (str/object): Left side interface of the branch.
            csProcs (list[str]): List of names of F2F processors.
            xRight (str/object): Right side interface of the branch.
            sCustomName (str, optional): Custom name for the branch.
        """
        super().__init__(oContainer, xLeft, csProcs, xRight, sCustomName, 'matter')

        self.aoFlows = []
        self.aoFlowProcs = []
        self.iFlows = 0
        self.iFlowProcs = 0
        self.fFlowRate = 0
        self.afFlowRates = [1.0] * 10
        self.bTriggerSetFlowRateCallbackBound = False
        self.iIfFlow = None
        self.oThermalBranch = None

        self.oContainer.addBranch(self)
        self.iFlows = len(self.aoFlows)
        self.iFlowProcs = len(self.aoFlowProcs)

    def createProcs(self, csProcs):
        """
        Creates flow objects between the processors.

        Args:
            csProcs (list[str]): List of F2F processor names.
        """
        for i, sProc in enumerate(csProcs):
            if sProc not in self.oContainer.toProcsF2F:
                raise ValueError(f"F2F processor {sProc} not found in system!")

            if not self.abIf[0] or i != 0:
                self.oContainer.toProcsF2F[sProc].addFlow(self.aoFlows[-1])

            oFlow = MatterFlow(self)
            self.aoFlows.append(oFlow)

            if i == 0:
                self.aoFlowProcs = [self.oContainer.toProcsF2F[sProc].addFlow(oFlow, 2)]
            else:
                self.aoFlowProcs.append(self.oContainer.toProcsF2F[sProc].addFlow(oFlow, 2))

    def setOutdated(self):
        """
        Marks the branch as outdated, triggering recalculations for flow rate.
        """
        if not self.bOutdated or self.oTimer.fTime > self.oHandler.fLastUpdate:
            self.bOutdated = True
            self.trigger('outdated')

    def setIfLength(self, iLength):
        """
        Sets the total number of elements in the interface branch.

        Args:
            iLength (int): Number of elements.
        """
        self.iIfFlow = iLength

    def setFlows(self, aoFlows, aoFlowProcs=None):
        """
        Sets the flows and processors for the branch.

        Args:
            aoFlows (list): List of flow objects.
            aoFlowProcs (list, optional): List of flow processor objects.
        """
        self.aoFlows = aoFlows
        self.iFlows = len(aoFlows)
        if aoFlowProcs is not None:
            self.aoFlowProcs = aoFlowProcs
            self.iFlowProcs = len(aoFlowProcs)

    def getInEXME(self):
        """
        Returns the current EXME from which mass flows into the branch.

        Returns:
            object: EXME object.
        """
        if self.fFlowRate == 0:
            iWhichExme = 1 if self.coExmes[0].oPhase.fPressure >= self.coExmes[1].oPhase.fPressure else 2

            for proc in self.aoFlowProcs:
                if isinstance(proc, ComponentsMatterValve) and not proc.bOpen:
                    return self.coExmes[0]

        else:
            iWhichExme = 1 if self.fFlowRate >= 0 else 2

        return self.coExmes[iWhichExme - 1]

    def bind(self, sType, callback):
        """
        Binds a callback to an event.

        Args:
            sType (str): Type of event.
            callback (callable): Callback function.
        """
        super().bind(sType, callback)
        if sType == 'setFlowRate':
            self.bTriggerSetFlowRateCallbackBound = True

    def setThermalBranch(self, oThermalBranch):
        """
        Sets the thermal branch for the matter branch.

        Args:
            oThermalBranch (object): Thermal branch object.
        """
        self.oThermalBranch = oThermalBranch

    def setFlowRate(self, fFlowRate, afPressureDrops=None):
        """
        Sets the flow rate for the branch and all flow objects.

        Args:
            fFlowRate (float): New flow rate in kg/s.
            afPressureDrops (list, optional): Pressure drops from F2F processors.
        """
        if self.abIf[0]:
            raise ValueError("Cannot set flow rate on a branch with a left-side interface.")

        for exme in self.coExmes:
            exme.oPhase.registerMassupdate()

        self.afFlowRates = self.afFlowRates[1:] + [fFlowRate]

        if sum(self.afFlowRates) < 1e-10:  # Precision threshold
            fFlowRate = 0
            afPressureDrops = [0] * self.iFlowProcs

        self.fFlowRate = fFlowRate
        self.bOutdated = False

        if afPressureDrops is None or any(x is None for x in afPressureDrops):
            afPressureDrops = [0] * self.iFlowProcs

        self.hSetFlowData(self.aoFlows, self.getInEXME(), fFlowRate, afPressureDrops)

        if self.bTriggerSetFlowRateCallbackBound:
            self.trigger('setFlowRate')

    def seal(self):
        """
        Seals the branch, preventing further modifications.
        """
        if self.bSealed:
            raise ValueError("Branch already sealed.")

        for i, flow in enumerate(self.aoFlows):
            if self.abIf[1] and self.iIfFlow == i + 1:
                self.hSetFlowData, self.hRemoveIfProc = flow.seal(True)
            elif i == 0:
                self.hSetFlowData = flow.seal(False, self)
            else:
                flow.seal(False, self)

        for proc in self.aoFlowProcs:
            proc.seal(self)

        self.hGetBranchData = None
        self.bSealed = True
