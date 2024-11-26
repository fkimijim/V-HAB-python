import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from component import Component

component = Component()

class resistor(component):
    """
    Simple model of an electrical resistor.
    This model simplifies the creation of circuit diagrams containing resistors,
    without considering complex dependencies like voltage, current, or temperature.
    """

    def __init__(self, oCircuit, sName, fResistance):
        """
        Constructor for the resistor class.

        Parameters:
        - oCircuit: Reference to the parent circuit.
        - sName: Name of the resistor.
        - fResistance: Resistance in Ohms.
        """
        # Call the parent constructor
        super().__init__(oCircuit, sName)

        # Set the resistance property
        self.fResistance = fResistance  # Resistance in [Ohm]
        self.fCurrent = 0  # Current in [A]
        self.fPower = 0  # Power in [W]
        self.fVoltageDrop = 0  # Voltage drop across the resistor in [V]

    def seal(self, oBranch):
        """
        Seals this resistor so nothing can be changed later on.

        Parameters:
        - oBranch: The branch object to which the resistor is connected.
        """
        if self.bSealed:
            raise ValueError("seal: Already sealed!")

        # Set the branch property for calculations in update()
        self.oBranch = oBranch

        # Mark as sealed
        self.bSealed = True

    def update(self):
        """
        Calculates the voltage drop and power across this resistor.
        """
        # Get the current from the branch, calculate the voltage drop,
        # and then calculate the dissipated power.
        self.fCurrent = abs(self.oBranch.fCurrent)
        self.fVoltageDrop = self.fResistance * self.fCurrent
        self.fPower = self.fCurrent * self.fVoltageDrop
