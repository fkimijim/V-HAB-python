from abc import ABC
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "substance_1")))
from substance_1 import SubstanceManipulator

class StationaryManipulator(SubstanceManipulator, ABC):
    """
    Stationary manipulator that can be used in normal phases to calculate mass transformations.
    """

    def __init__(self, sName, oPhase):
        """
        Constructor for the StationaryManipulator class.
        
        Parameters:
        - sName: str, Name of the manipulator.
        - oPhase: Phase, Phase object in which this manipulator is located.
        """
        # Initialize the parent class (substance manipulator).
        super().__init__(sName, oPhase)

        # Ensure the manipulator is not in a flow phase.
        if self.oPhase.bFlow:
            raise ValueError(
                f"The stationary manipulator {self.sName} is located in a flow phase. "
                "For flow phases, use flow manipulators!"
            )
