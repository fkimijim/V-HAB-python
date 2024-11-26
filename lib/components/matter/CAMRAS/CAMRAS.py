import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from core.vsys import BaseSystem
from core.matter.procs.exmes.gas.gas import GasExMe
from core.matter.procs.exmes.mixture.mixture import MixtureExMe
from lib.components.matter.CAMRAS.components.Filter import Filter
from core.matter.branch import Branch
from lib.components.thermal.heatsources.ConstantTemperature import ConstantTemperature

BaseSystem = BaseSystem()
GasExMe = GasExMe()
MixtureExMe = MixtureExMe()
Filter = Filter()
Branch = Branch()
ConstantTemperature = ConstantTemperature()

class CAMRAS(BaseSystem):
    """
    CAMRAS (CO2 and Moisture Removal Amine Swingbed) system model for CO2 reduction on the ORION spacecraft.
    """

    def __init__(self, oParent, sName, fTimeStep, fVolumetricFlowrateMain, sCase):
        """
        Initialize the CAMRAS system.

        :param oParent: Parent system.
        :param sName: Name of the CAMRAS system.
        :param fTimeStep: Simulation time step.
        :param fVolumetricFlowrateMain: Main volumetric flow rate.
        :param sCase: Crew state ('nominal', 'exercise', 'sleep').
        """
        super().__init__(oParent, sName, fTimeStep)
        
        self.iCycleActive = 2
        self.fPressureCompensationTime = 2  # [s]
        self.fVacuumTime = 20  # [s]
        self.fFlowrateMain = 0  # [kg/s]
        self.fVolumetricFlowrateMain = fVolumetricFlowrateMain
        self.fMassToVacuum = 0
        self.fMassToEqualize = 0
        self.fCycleTime = 6.5 * 60  # [s]
        self.tCAMRASFilterAtmosphere = None
        self.oAtmosphere = None
        self.fInitialTimeStep = fTimeStep
        self.iCounter = 0
        self.sCase = sCase
        self.fInternalTime = 0
        self.bUpdateCase = False
        self.fTimeCycleChange = 0
        self.fTime = 0
        self.iOn = 0
        self.iOff = 0
        self.iCounterOff = 0

    def createMatterStructure(self):
        """
        Create the matter structure for CAMRAS.
        """
        super().createMatterStructure()
        
        # Define CAMRAS filter atmosphere properties
        self.tCAMRASFilterAtmosphere = {
            "fTemperature": 293.15,  # [K]
            "fRelHumidity": 0.4,
            "fPressure": 101325,  # [Pa]
            "fCO2Percent": 0.0038,
        }

        # Define adsorbent properties
        fAdsorbentMassCAMRAS = 1.75  # [kg]
        arMass = [0] * self.oMT.iSubstances
        arMass[self.oMT.tiN2I["Zeolite5A"]] = 1
        fDensity5A = self.oMT.calculateDensity(
            "solid",
            arMass,
            self.tCAMRASFilterAtmosphere["fTemperature"],
            [self.tCAMRASFilterAtmosphere["fPressure"]] * self.oMT.iSubstances,
        )
        fSolidVolume = fAdsorbentMassCAMRAS / fDensity5A
        fGasVolume = 0.006399  # [m³]

        # Create Filter A
        self._create_filter(
            "Filter_A",
            fGasVolume,
            fSolidVolume,
            self.tCAMRASFilterAtmosphere,
            "A",
        )
        
        # Create Filter B
        self._create_filter(
            "Filter_B",
            fGasVolume,
            fSolidVolume,
            self.tCAMRASFilterAtmosphere,
            "B",
        )
        
        # Connect branches for subsystem flow paths
        self._connect_branches()

    def _create_filter(self, sName, fGasVolume, fSolidVolume, tAtmosphere, suffix):
        """
        Create a filter (A or B) with the specified parameters.

        :param sName: Name of the filter.
        :param fGasVolume: Gas volume for the filter.
        :param fSolidVolume: Solid volume for the adsorbent.
        :param tAtmosphere: Atmosphere properties.
        :param suffix: Filter suffix ('A' or 'B').
        """
        self.createStore(sName, fGasVolume + fSolidVolume)

        # Input phase
        oInput = self.toStores[sName].createPhase(
            "gas",
            "PhaseIn",
            fGasVolume,
            {"N2": 8e4, "O2": 2e4, "CO2": 500},
            tAtmosphere["fTemperature"],
            tAtmosphere["fRelHumidity"],
        )

        # Filtered phases for H2O and CO2
        oFilteredH2O = self.toStores[sName].createPhase(
            "mixture",
            "FilteredPhaseH2O",
            "solid",
            fSolidVolume / 2,
            {"Zeolite5A": 1},
            tAtmosphere["fTemperature"],
            tAtmosphere["fPressure"],
        )
        oFilteredCO2 = self.toStores[sName].createPhase(
            "mixture",
            "FilteredPhaseCO2",
            "solid",
            fSolidVolume / 2,
            {"Zeolite5A": 1},
            tAtmosphere["fTemperature"],
            tAtmosphere["fPressure"],
        )

        # Ports
        self._create_ports(oInput, oFilteredH2O, oFilteredCO2, suffix)

    def _create_ports(self, oInput, oFilteredH2O, oFilteredCO2, suffix):
        """
        Create ports for a filter.

        :param oInput: Input phase.
        :param oFilteredH2O: Filtered H2O phase.
        :param oFilteredCO2: Filtered CO2 phase.
        :param suffix: Filter suffix ('A' or 'B').
        """
        GasExMe(oInput, "Flow_In")
        GasExMe(oInput, "Flow_Out")
        GasExMe(oInput, "AdsorbedH2O")
        GasExMe(oInput, "AdsorbedCO2")
        GasExMe(oInput, f"PressureCompensationPort{suffix}")
        GasExMe(oInput, "Flow_Out_Vacuum")
        GasExMe(oInput, "Flow_Out_Desorb")
        MixtureExMe(oFilteredH2O, "filterportH2O")
        MixtureExMe(oFilteredCO2, "filterportCO2")

        # Create filters for H2O and CO2
        Filter(
            self.toStores[f"Filter_{suffix}"],
            f"Filter{suffix}H2O",
            "PhaseIn.AdsorbedH2O",
            f"FilteredPhaseH2O.filterportH2O",
            "H2O",
            self.fCycleTime,
            self.fVacuumTime,
            self.fPressureCompensationTime,
            self.sCase,
        )
        Filter(
            self.toStores[f"Filter_{suffix}"],
            f"Filter{suffix}CO2",
            "PhaseIn.AdsorbedCO2",
            f"FilteredPhaseCO2.filterportCO2",
            "CO2",
            self.fCycleTime,
            self.fVacuumTime,
            self.fPressureCompensationTime,
            self.sCase,
        )

    def _connect_branches(self):
        """
        Connect branches for the subsystem flow paths.
        """
        # Cycle one branches
        Branch(
            self,
            "Filter_A.Flow_In",
            {},
            "CAMRAS_Air_In_C1",
            "CAMRAS_Air_In_C1",
        )
        Branch(
            self,
            "Filter_B.Flow_Out_Desorb",
            {},
            "CAMRAS_to_Vaccum_B_Desorb",
            "Filter_B_Desorb",
        )
        Branch(
            self,
            "Filter_B.Flow_Out_Vacuum",
            {},
            "CAMRAS_to_Vaccum_B",
            "Filter_B_Vacuum",
        )
        Branch(
            self,
            "Filter_A.Flow_Out",
            {},
            "CAMRAS_Air_Out_C1",
            "CAMRAS_Air_Out_C1",
        )

        # Cycle two branches
        Branch(
            self,
            "Filter_B.Flow_In",
            {},
            "CAMRAS_Air_In_C2",
            "CAMRAS_Air_In_C2",
        )
        Branch(
            self,
            "Filter_A.Flow_Out_Desorb",
            {},
            "CAMRAS_to_Vaccum_A_Desorb",
            "Filter_A_Desorb",
        )
        Branch(
            self,
            "Filter_A.Flow_Out_Vacuum",
            {},
            "CAMRAS_to_Vaccum_A",
            "Filter_A_Vacuum",
        )
        Branch(
            self,
            "Filter_B.Flow_Out",
            {},
            "CAMRAS_Air_Out_C2",
            "CAMRAS_Air_Out_C2",
        )

        # Pressure compensation
        Branch(
            self,
            "Filter_A.PressureCompensationPortA",
            {},
            "Filter_B.PressureCompensationPortB",
            "PressureCompensation",
        )

    def createThermalStructure(self):
        """
        Create the thermal structure for CAMRAS.
        """
        super().createThermalStructure()
        oHeatSourceA = ConstantTemperature(
            "FilterA_ConstantTemperature"
        )
        self.toStores["Filter_A"].toPhases["PhaseIn"].oCapacity.addHeatSource(oHeatSourceA)
        oHeatSourceB = ConstantTemperature(
            "FilterB_ConstantTemperature"
        )
        self.toStores["Filter_B"].toPhases["PhaseIn"].oCapacity.addHeatSource(oHeatSourceB)

    def createSolverStructure(self):
        """
        Create the solver structure for CAMRAS.
        """
        super().createSolverStructure()
        # Define solver branches
        solver.matter.manual.branch(self.toBranches["CAMRAS_Air_In_C1"])
        solver.matter.manual.branch(self.toBranches["Filter_B_Vacuum"])
        solver.matter.residual.branch(self.toBranches["Filter_B_Desorb"])
        solver.matter.residual.branch(self.toBranches["CAMRAS_Air_Out_C1"])

        solver.matter.manual.branch(self.toBranches["CAMRAS_Air_In_C2"])
        solver.matter.manual.branch(self.toBranches["Filter_A_Vacuum"])
        solver.matter.residual.branch(self.toBranches["Filter_A_Desorb"])
        solver.matter.residual.branch(self.toBranches["CAMRAS_Air_Out_C2"])

        solver.matter.manual.branch(self.toBranches["PressureCompensation"])

        self.setThermalSolvers()

    def exec(self):
        """
        Execute the CAMRAS logic.
        """
        super().exec()
        self.update()

    def update(self):
        """
        Update the CAMRAS system based on the current cycle state.
        """
        # Logic for system execution based on active cycle and subsystem states
        pass
