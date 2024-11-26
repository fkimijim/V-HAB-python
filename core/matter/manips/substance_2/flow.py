from abc import ABC, abstractmethod
import numpy as np

class FlowManipulator(ABC):
    """
    Abstract base class for flow manipulators, used inside flow phases to calculate mass transformations.
    """

    def __init__(self, sName, oPhase):
        """
        Constructor for FlowManipulator.
        Inputs:
        - sName: Name for this manipulator.
        - oPhase: Phase object in which this manipulator is located.
        """
        # Initialize the parent class (substance manipulator).
        super().__init__(sName, oPhase)

        # Initialize partial flows for multi-solver.
        self.afPartialFlowsMultiSolver = np.zeros(self.oMT.iSubstances)

        # Ensure that the manipulator is associated with a flow phase.
        if not self.oPhase.bFlow:
            raise ValueError(
                f"The flow manipulator {self.sName} is not located in a flow phase. "
                "For normal phases, use stationary manipulators!"
            )

    @abstractmethod
    def calculateConversionRate(self, afInFlowRates, aarInPartials, mrInCompoundMass):
        """
        Abstract method to calculate the conversion rate.
        This method is called by the multi-branch solver, which also calculates the inflow rates and partials.

        Inputs:
        - afInFlowRates: Vector containing the total mass flow rates entering the flow phase (in kg/s).
        - aarInPartials: Matrix containing the corresponding partial mass ratios of the inflow rates.
        - mrInCompoundMass: Matrix containing the compound mass ratios for the inflow rates.

        Example:
        Use the following to calculate the total partial inflows in kg/s:
        afPartialInFlows = np.sum((afInFlowRates[:, None] * aarInPartials), axis=0)
        """
        pass
