import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "p2p")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "base")))
from p2p.p2p import P2P
import branch

MatterProcsP2P = P2P()
SolverMatterMultiBranchIterativeBranch = branch()

class FlowP2P(MatterProcsP2P):
    """
    FlowP2P: A P2P processor for flow phases.

    This class models a P2P where the flow rate depends on the flow rates 
    passing through the connected phases. The flow rate is solved 
    iteratively alongside the branch flow rates in a multi-branch solver.
    """

    # Constant property to indicate whether this is a stationary P2P
    bStationary = False

    def __init__(self, oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut):
        """
        Initializes the FlowP2P class.

        Args:
            oStore (object): The store object where the P2P is located.
            sName (str): Name of the processor.
            sPhaseAndPortIn (str): Input phase and EXME in "phase.exme" notation.
            sPhaseAndPortOut (str): Output phase and EXME in "phase.exme" notation.
        """
        super().__init__(oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut)

        if not self.oIn.oPhase.bFlow and not self.oOut.oPhase.bFlow:
            raise ValueError(
                f"The flow P2P {self.sName} does not have a flow phase as either input or output. "
                "One side of the P2P must be a flow phase! For normal phases, use stationary P2Ps."
            )

    def findSolver(self):
        """
        Finds the solver associated with the connected phases.

        Returns:
            object: Solver instance associated with the P2P.
        """
        csExmes = self.oIn.oPhase.toProcsEXME.keys()
        for exme in csExmes:
            exmeObj = self.oIn.oPhase.toProcsEXME[exme]
            if not exmeObj.bFlowIsAProcP2P:
                handler = exmeObj.oFlow.oBranch.oHandler
                if isinstance(handler, SolverMatterMultiBranchIterativeBranch):
                    return handler

        csExmes = self.oOut.oPhase.toProcsEXME.keys()
        for exme in csExmes:
            exmeObj = self.oOut.oPhase.toProcsEXME[exme]
            if not exmeObj.bFlowIsAProcP2P:
                handler = exmeObj.oFlow.oBranch.oHandler
                if isinstance(handler, SolverMatterMultiBranchIterativeBranch):
                    return handler

    def limitFlows(self, afInFlows, abLimitFlows):
        """
        Limits the flows through the P2P based on the specified constraints.

        Args:
            afInFlows (list[float]): Array of incoming flows in kg/s.
            abLimitFlows (list[bool]): Boolean array indicating limited flows.
        """
        afPartialFlows = [self.fFlowRate * partial for partial in self.arPartialMass]

        if self.fFlowRate >= 0:
            for i, limit in enumerate(abLimitFlows):
                if limit:
                    afPartialFlows[i] = afInFlows[i]
        else:
            for i, limit in enumerate(abLimitFlows):
                if limit:
                    afPartialFlows[i] = -afInFlows[i]

        fFlowRate = sum(afPartialFlows)
        if fFlowRate != 0:
            arPartials = [flow / fFlowRate for flow in afPartialFlows]
        else:
            arPartials = [0] * len(self.oMT.iSubstances)

        self.setMatterProperties(fFlowRate, arPartials)

    def calculateFlowRate(self, afInsideInFlowRate, aarInsideInPartials, afOutsideInFlowRate, aarOutsideInPartials):
        """
        Abstract method to calculate the flow rate.

        This method must be implemented by subclasses. It calculates the 
        flow rate based on the inflow rates and partials for both connected 
        phases.

        Args:
            afInsideInFlowRate (list[float]): Total mass flow rates entering the inside phase.
            aarInsideInPartials (list[list[float]]): Partial mass ratios of inflows for the inside phase.
            afOutsideInFlowRate (list[float]): Total mass flow rates entering the outside phase.
            aarOutsideInPartials (list[list[float]]): Partial mass ratios of inflows for the outside phase.
        """
        raise NotImplementedError("Subclasses must implement the calculateFlowRate method.")
