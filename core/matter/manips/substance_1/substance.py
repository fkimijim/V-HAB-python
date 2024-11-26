from abc import ABC, abstractmethod
import numpy as np

class SubstanceManipulator(ABC):
    """
    Abstract base class for substance manipulators.
    Allows the model to change one substance into another, modeling chemical reactions.
    For example, electrolysis: 2 * H2O -> 2 * H2 + O2.
    """

    def __init__(self, sName, oPhase):
        """
        Constructor for SubstanceManipulator.
        Inputs:
        - sName: Name for this manipulator.
        - oPhase: Phase object in which this manipulator is located.
        """
        self.sName = sName
        self.oPhase = oPhase

        # Initialize properties
        self.afPartialFlows = np.zeros(oPhase.oMT.iSubstances)  # Partial mass flow rates [kg/s]
        self.aarFlowsToCompound = np.zeros((oPhase.oMT.iSubstances, oPhase.oMT.iSubstances))  # Mass ratios for compounds
        self.fLastExec = 0  # Last execution time [s]
        self.fTotalError = 0  # Total mass error [kg]

        # Register post-tick update
        self.hBindPostTickUpdate = oPhase.oMT.oTimer.registerPostTick(
            self.update, "matter", "substanceManips"
        )

    @abstractmethod
    def update(self, afPartialFlows, aarFlowsToCompound=None):
        """
        Update function to set the partial flow rates and compound mass ratios.
        Inputs:
        - afPartialFlows: Vector of partial mass changes for each substance [kg/s].
        - aarFlowsToCompound: Matrix defining the mass ratios for compounds.

        Note:
        This method should only be called by the timer in the post-tick phase.
        """
        # Check for NaN or Inf values in flow rates
        if np.any(np.isnan(afPartialFlows)) or np.any(np.isinf(afPartialFlows)):
            raise ValueError(f"Error in manipulator {self.sName}. Some flow rates are NaN or Inf.")

        # Calculate elapsed time since last update
        fElapsedTime = self.oPhase.oMT.oTimer.fTime - self.fLastExec
        if fElapsedTime > 0:
            # Calculate total error in kg
            fError = np.sum(self.afPartialFlows)
            self.fTotalError += fError * fElapsedTime
            self.fLastExec = self.oPhase.oMT.oTimer.fTime

        # Update flow rates
        self.afPartialFlows = afPartialFlows

        if aarFlowsToCompound is not None:
            self.aarFlowsToCompound = aarFlowsToCompound

            # Validate that mass ratios sum to 1 for compound substances
            compound_indices = self.oPhase.oMT.abCompound
            flow_positive = self.afPartialFlows > 0
            if (
                np.any(np.abs(self.afPartialFlows[compound_indices]) > 10**-self.oPhase.oMT.oTimer.iPrecision)
                and np.any(np.abs(np.sum(aarFlowsToCompound[flow_positive & compound_indices, :], axis=1) - 1) > 1e-8)
            ):
                raise ValueError("Compound mass ratios do not sum to 1 within allowed tolerance.")
        else:
            if np.any(self.afPartialFlows[self.oPhase.oMT.abCompound] > 0):
                raise ValueError(
                    f"A compound mass is created in manipulator {self.sName}, but aarFlowsToCompound is not defined!"
                )
            self.aarFlowsToCompound = np.zeros(
                (self.oPhase.oMT.iSubstances, self.oPhase.oMT.iSubstances)
            )
