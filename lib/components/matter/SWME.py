import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.vsys import BaseSystem
from lib.components.matter.SWME import SWMEStore
from pipe import Pipe
from core.base.branch import Branch
from core.thermal.heatsource import HeatSource

vsys = BaseSystem()
SWMEStore = SWMEStore()
Pipe = Pipe()
Branch = Branch()
HeatSource = HeatSource()

class SWME(vsys):
    """
    SWME: Space Suit Water Membrane Evaporator model for the xEMU.

    This class models the SWME store containing a flow phase, a vapor phase,
    and the X50Membrane P2P. It includes methods to update the back pressure
    valve (BPV) flow and position based on conditions during the simulation.
    """

    # Properties that don't change during simulation
    fSWMEVaporVolume = 0.0010212418  # [m^3]
    iNumberOfFibers = 27900  # Number of hollow fibers
    fFiberInnerDiameter = 220e-6  # [m]
    fFiberExposedLength = 0.11938  # [m]
    iValveMaximumSteps = 4200  # Maximum valve steps

    def __init__(self, oParent, sName, fInitialTemperature):
        """
        Constructor for the SWME class.

        Args:
            oParent: Parent system object.
            sName: Name of the SWME system.
            fInitialTemperature: Initial water temperature in Kelvin.
        """
        super().__init__(oParent, sName, 0.2)  # Fixed time step of 0.2 seconds
        self.fInitialTemperature = fInitialTemperature
        self.oEnvironment = None  # Reference to the environment phase
        self.iBPVCurrentSteps = 0
        self.fVaporFlowRate = 0
        self.fValveCurrentArea = 0
        self.fTemperatureSetPoint = 283.15  # Default setpoint (10°C or 50°F)

    def createMatterStructure(self):
        super().createMatterStructure()

        # Creating the SWME Store
        SWMEStore(self, "SWMEStore")

        # Pipes connecting SWME to the supersystem
        Pipe(self, "Pipe_1", 0.01, 0.0127)
        Pipe(self, "Pipe_2", 0.01, 0.0127)

        # Inlet and outlet branches with interfaces
        self.toBranches.InletBranch = Branch(self, "SWMEStore.WaterIn", ["Pipe_1"], "Inlet")
        self.toBranches.OutletBranch = Branch(self, "SWMEStore.WaterOut", ["Pipe_2"], "Outlet")

        # Branch to the environment with interface
        self.toBranches.EnvironmentBranch = Branch(self, "SWMEStore.VaporOut", [], "Environment")

    def createThermalStructure(self):
        super().createThermalStructure()

        # Heat source for evaporation heat transfer
        oHeatSource = HeatSource("HeatOfEvaporation")
        self.toStores.SWMEStore.toPhases.FlowPhase.oCapacity.addHeatSource(oHeatSource)

        # Assigning heat source to X50Membrane
        self.toStores.SWMEStore.toProcsP2P.X50Membrane.setHeatSource(oHeatSource)

    def createSolverStructure(self):
        super().createSolverStructure()

        # Solvers for branches
        ManualSolver(self.toBranches.InletBranch)
        ManualSolver(self.toBranches.OutletBranch)
        ManualSolver(self.toBranches.EnvironmentBranch)

        # Binding outlet solver to inlet branch's 'outdated' event
        self.toBranches.InletBranch.bind(
            "outdated",
            lambda _: self.toBranches.OutletBranch.oHandler.setFlowRate(
                -1 * self.toBranches.InletBranch.fFlowRate - self.toStores.SWMEStore.toProcsP2P.X50Membrane.fWaterVaporFlowRate
            ),
        )

        # Configuring time step properties for VaporPhase
        self.toStores.SWMEStore.toPhases.VaporPhase.setTimeStepProperties({"fMaxStep": 0.5})

        self.setThermalSolvers()

    def setInterfaces(self, sInlet, sOutlet, sVapor):
        self.connectIF("Inlet", sInlet)
        self.connectIF("Outlet", sOutlet)
        self.connectIF("Environment", sVapor)

    def setTemperatureSetPoint(self, fTemperatureSetPoint):
        self.fTemperatureSetPoint = fTemperatureSetPoint

    def updateBPVFlow(self, fPressureInternal=None):
        if fPressureInternal is None:
            fPressureInternal = (
                self.toStores.SWMEStore.toPhases.VaporPhase.fMassToPressure
                * self.toStores.SWMEStore.toPhases.VaporPhase.fMass
            )

        fVaporDensity = self.toStores.SWMEStore.toPhases.VaporPhase.fDensity

        # Calculate valve open area based on step position
        if self.iBPVCurrentSteps < 756:
            self.fValveCurrentArea = 0
        else:
            iSteps = self.iBPVCurrentSteps
            self.fValveCurrentArea = (
                3.7983e-24 * iSteps**6
                - 5.0117e-20 * iSteps**5
                + 2.4377e-16 * iSteps**4
                - 5.5101e-13 * iSteps**3
                + 6.6882e-10 * iSteps**2
                - 3.9027e-07 * iSteps
                + 8.477e-05
            )

        if self.iBPVCurrentSteps != 0:
            fC1 = ((8 * fPressureInternal) / (math.pi * fVaporDensity)) ** 0.5
            fKappa = self.oMT.calculateAdiabaticIndex(self.toStores.SWMEStore.toPhases.VaporPhase)

            fCriticalPressure = fPressureInternal * (2 / (1 + fKappa)) ** (fKappa / (fKappa - 1))
            rPressure = self.oEnvironment.fPressure / fPressureInternal if self.oEnvironment.fPressure > fCriticalPressure else 0

            fPsi = (
                ((fKappa / (fKappa - 1)) * ((rPressure ** (2 / fKappa)) - (rPressure ** ((1 + fKappa) / fKappa)))) ** 0.5
                if rPressure > 0
                else (0.5 * fKappa * ((2 / (1 + fKappa)) ** ((fKappa + 1) / (fKappa - 1)))) ** 0.5
            )

            self.fVaporFlowRate = (0.86 * self.fValveCurrentArea * 4 * fPressureInternal * fPsi) / (fC1 * math.pi**0.5)
        else:
            self.fVaporFlowRate = 0

        self.fVaporFlowRate = round(self.fVaporFlowRate, self.oTimer.iPrecision)

        # Update branch flow rate
        self.toBranches.EnvironmentBranch.oHandler.setFlowRate(self.fVaporFlowRate)
        self.toBranches.InletBranch.setOutdated()

    def updateBPVPosition(self):
        fCurrentOutletWaterTemperature = self.toStores.SWMEStore.toPhases.FlowPhase.fTemperature

        if fCurrentOutletWaterTemperature == 0:
            return

        fDeltaTemperature = fCurrentOutletWaterTemperature - self.fTemperatureSetPoint

        if abs(fDeltaTemperature) <= 0.28:
            return

        fDeltaSteps = 58.8 * fDeltaTemperature / 1.8
        self.iBPVCurrentSteps += fDeltaSteps

        # Enforce valve step boundaries
        if self.iBPVCurrentSteps < 0:
            self.iBPVCurrentSteps = 0
        elif self.iBPVCurrentSteps > self.iValveMaximumSteps:
            self.iBPVCurrentSteps = self.iValveMaximumSteps

        self.updateBPVFlow()

    def setEnvironmentReference(self, oPhase):
        self.oEnvironment = oPhase

    def exec(self, _):
        super().exec(_)
        self.updateBPVPosition()
