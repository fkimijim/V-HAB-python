import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.procs.f2f import f2f

f2f = f2f()

class Heater(f2f):
    """
    HEATER: A dummy heater model.
    """

    def __init__(self, oMT, sName, fPower=0, rEfficiency=1):
        """
        Initialize the heater.

        :param oMT: Matter table or parent system.
        :param sName: Name of the heater.
        :param fPower: Heater power in Watts (default: 0).
        :param rEfficiency: Heater efficiency as a ratio (default: 1).
        """
        super().__init__(oMT, sName)

        self.fPower = fPower
        self.rEfficiency = rEfficiency
        self.fHeatFlow = self.fPower * self.rEfficiency

        # Define solver compatibility
        self.supportSolver("hydraulic", 1, 0)
        self.supportSolver("callback", self.solverDeltas)
        self.supportSolver("manual", True, self.updateManualSolver)

    def updateManualSolver(self):
        """
        Update for manual solver. Currently does nothing.
        """
        pass

    def solverDeltas(self, *_):
        """
        Return the pressure delta, which is always 0 for this heater.
        """
        return 0

    def updateThermal(self):
        """
        Update the thermal properties of the heater.
        """
        self.fHeatFlow = self.fPower * self.rEfficiency

    def setPower(self, fPower):
        """
        Set the power of the heater and update the heat flow.

        :param fPower: New power in Watts.
        """
        self.fPower = fPower
        self.fHeatFlow = self.fPower * self.rEfficiency
