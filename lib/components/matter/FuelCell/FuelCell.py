import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
import math
from core.vsys import BaseSystem
from core.matter.store.store import Store
from lib.components.matter.P2Ps.ManualP2P import ManualP2P
from components.FuelCellReaction import FuelCellReaction
from core.thermal.heatsource import HeatSource

FuelCellReaction = FuelCellReaction()
vsys = BaseSystem()
Store = Store()
ManualP2P = ManualP2P()
HeatSource = HeatSource()

class FuelCell(vsys):
    """
    PEM-Fuel cell built with 2 gas channels and a membrane in between.
    """

    def __init__(self, oParent, sName, fTimeStep, txInput):
        """
        Initializes the FuelCell class.

        Parameters:
        - oParent: Parent object.
        - sName: Name of the fuel cell system.
        - fTimeStep: Simulation time step.
        - txInput: Configuration parameters including:
          - iCells: Number of cells in the stack (required).
          - fMembraneArea: Area of one cell membrane in m^2 (optional).
          - fMembraneThickness: Thickness of one cell membrane in m (optional).
          - fMaxCurrentDensity: Max current density in A/m^2 (optional).
          - rMaxReactingH2: Max reacting ratio for H2 (optional).
          - rMaxReactingO2: Max reacting ratio for O2 (optional).
          - fPower: Electrical power of the fuel cell in W (optional).
        """
        super().__init__(oParent, sName, fTimeStep)

        # Default values
        self.iCells = 30
        self.fMembraneArea = 250 / 10000
        self.fMembraneThickness = 2e-6
        self.fMaxCurrentDensity = 4000
        self.rEfficiency = 1
        self.fStackCurrent = 0
        self.fStackVoltage = None
        self.fPower = 0
        self.fStackZeroPotential = 1.23
        self.rMaxReactingH2 = 0.5
        self.rMaxReactingO2 = 0.5
        self.fInitialH2 = None
        self.fInitialO2 = None

        # Update with txInput values
        csValidFields = ['iCells', 'fMembraneArea', 'fMembraneThickness',
                         'fMaxCurrentDensity', 'rMaxReactingH2', 'rMaxReactingO2', 'fPower']
        for key, value in txInput.items():
            if key in csValidFields:
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid input {key} for the Fuel Cell")

        self.fStackVoltage = self.iCells * 1.23

        # Evaluate configuration if applicable
        if hasattr(self, "oRoot") and hasattr(self.oRoot, "oCfgParams"):
            eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        fInitialTemperature = 293.15
        fLoopVolume = 0.00025 * self.iCells * self.fMembraneArea / 0.025

        # Creating phases and stores
        self.toStores = {
            'FuelCell': Store(self, 'FuelCell', 0.4 * self.iCells * self.fMembraneArea + 0.1 + 2 * fLoopVolume + 4e-6),
            'H2_WaterSeparation': Store(self, 'H2_WaterSeparation', 0.01334 * self.iCells * self.fMembraneArea + 1e-6),
            'O2_WaterSeparation': Store(self, 'O2_WaterSeparation', 0.01334 * self.iCells * self.fMembraneArea + 1e-6)
        }

        # Hydrogen channels and loops
        oH2_Loop = self.toStores['FuelCell'].createPhase('gas', 'H2_Loop', fLoopVolume, {'H2': 3e5}, fInitialTemperature, 0.8)
        self.fInitialH2 = oH2_Loop.afMass[self.oMT.tiN2I['H2']]

        # Oxygen channels and loops
        oO2_Loop = self.toStores['FuelCell'].createPhase('gas', 'O2_Loop', fLoopVolume, {'O2': 3e5}, fInitialTemperature, 0.8)
        self.fInitialO2 = oO2_Loop.afMass[self.oMT.tiN2I['O2']]

        # Other phases like cooling system and membrane
        # Add pipes, fans, and branches similarly

        # Add the Fuel Cell Reaction manipulator
        FuelCellReaction('FuelCellReaction', oH2_Loop)

        # Add P2Ps for H2, O2, and membrane
        ManualP2P(self.toStores['FuelCell'], 'H2_to_Membrane', oH2_Loop, oO2_Loop)

    def createThermalStructure(self):
        super().createThermalStructure()
        oFuelCellHeatSource = HeatSource('FuelCell_HeatSource', 0)
        self.toStores['FuelCell'].toPhases['CoolingSystem'].oCapacity.addHeatSource(oFuelCellHeatSource)

    def calculate_voltage(self):
        """
        Calculate the voltage of the fuel cell based on the input parameters.
        """
        fTemperature = self.toStores['FuelCell'].toPhases['CoolingSystem'].fTemperature
        fMaxCurrent = self.fMaxCurrentDensity * self.fMembraneArea
        self.fStackCurrent = self.fPower / self.fStackVoltage

        if self.fStackCurrent > fMaxCurrent:
            self.fStackCurrent = fMaxCurrent
            self.fPower = self.fStackCurrent * self.fStackVoltage

        # Gibbs and activation calculations
        fGibbsLinearization = 0.00085
        fWaterContent = 14
        fActivationCoefficient = 0.4
        fDiffusionCoefficient = 0.8
        fMembraneResistance = self.fMembraneThickness / (
            self.fMembraneArea * (0.005139 * fWaterContent + 0.00326) * 
            math.exp(1267 * (1 / 303 - 1 / fTemperature))
        )

        fPressure_H2 = self.toStores['FuelCell'].toPhases['H2_Channel'].afPP[self.oMT.tiN2I['H2']]
        fPressure_O2 = self.toStores['FuelCell'].toPhases['O2_Channel'].afPP[self.oMT.tiN2I['O2']]

        if self.oTimer.iTick > 5 and self.fStackCurrent > 0:
            fNewVoltage = self.iCells * (
                1.23 - fGibbsLinearization * (fTemperature - 298) +
                self.oMT.Const.fUniversalGas * fTemperature / (2 * self.oMT.Const.fFaraday) *
                math.log(fPressure_H2 * math.sqrt(fPressure_O2)) -
                fMembraneResistance * self.fStackCurrent
            )
        else:
            fNewVoltage = self.fStackVoltage

        self.fStackVoltage = fNewVoltage
        self.rEfficiency = self.fStackVoltage / self.iCells / self.fStackZeroPotential

    def setPower(self, fPower):
        """
        Set the power for the fuel cell and recalculate voltage.
        """
        self.fPower = fPower
        self.calculate_voltage()
