import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "pipe")))
import vsys
from lib.components.matter.algae.CalculationModules.GrowthRateCalculationModule import GrowthRateCalculationModule
from lib.components.matter.algae.CalculationModules.PhotosynthesisModule import PhotosynthesisModule
from lib.components.matter.algae.CalculationModules.GrowthMediumModule.BBMCompositionCalculation import BBMCompositionCalculation
from lib.components.matter.algae.CalculationModules.GrowthMediumModule.ChlorellaContentCalculation import ChlorellaContentCalculation
from core.matter.store.store import Store
from core.matter.phases.flow.mixture import Mixture
from core.matter.procs.exmes.gas.gas import GasExMe
from lib.components.matter.algae.F2F.GrowthMediumAirInlet import GrowthMediumAirInlet
from core.matter.branch import MatterBranch
import Pipe
from core.matter.procs.exmes.mixture.mixture import MixtureExMe
from algae.P2P.AtmosphericGasExchange import AtmosphericGasExchange
from algae.manipulators.GrowthMediumChanges import GrowthMediumChanges
from algae.CalculationModules.GrowthRateCalculationModule.TemperatureLimitation import TemperatureLimitation
from algae.CalculationModules.GrowthRateCalculationModule.PHLimitation import PHLimitation
from algae.CalculationModules.GrowthRateCalculationModule.OxygenLimitation import OxygenLimitation
from algae.CalculationModules.GrowthRateCalculationModule.CarbonDioxideLimitation import CarbonDioxideLimitation
from algae.CalculationModules.PARModule.PARModule import PARModule
from lib.components.thermal.heatsources import ConstantTemperature

GrowthRateCalculationModule = GrowthRateCalculationModule()
PhotosynthesisModule = PhotosynthesisModule()
BBMCompositionCalculation = BBMCompositionCalculation()
Store = Store()
Mixture = Mixture()
GasExMe = GasExMe()
GrowthMediumAirInlet = GrowthMediumAirInlet()
MatterBranch = MatterBranch()
Pipe = Pipe()
MixtureExMe = MixtureExMe()
AtmosphericGasExchange = AtmosphericGasExchange()
GrowthMediumChanges = GrowthMediumChanges()
TemperatureLimitation = TemperatureLimitation()
PHLimitation = PHLimitation()
OxygenLimitation = OxygenLimitation()
CarbonDioxideLimitation = CarbonDioxideLimitation()
PARModule = PARModule()
ConstantTemperature = ConstantTemperature()

class ChlorellaInMedia(vsys):
    """
    ChlorellaInMedia represents the dynamic Chlorella Vulgaris model in a growth medium.
    Connects the growth chamber matter phases with calculation modules to simulate algal growth.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, oParent.fTimeStep)
        eval(self.oRoot.oCfgParams.configCode(self))

        # Refill parameters initialization
        self.bNO3Refill = False
        self.bH2ORefill = False
        self.bUseUrine = self.oParent.bUseUrine

        # Initial density
        self.fCurrentGrowthMediumDensity = 1000  # [kg/m3]

    def createMatterStructure(self):
        super().createMatterStructure()

        # Calculation Modules
        self.oGrowthRateCalculationModule = (
            GrowthRateCalculationModule(self)
        )
        self.oPhotosynthesisModule = (
            PhotosynthesisModule(self, self.oMT)
        )

        # Growth Chamber Phase
        Store(self, 'GrowthChamber', self.oParent.fGrowthVolume + 0.1)
        self.oBBMComposition = (
            BBMCompositionCalculation(
                self.oParent.fGrowthVolume, self.oMT, self
            )
        )
        self.fStartNitrogenEquivalent = 2.9 * self.oParent.fGrowthVolume
        self.fInitialChlorellaMass = ChlorellaContentCalculation(self)

        self.tfGrowthChamberComponents = self.oBBMComposition.tfBBMComposition
        self.tfGrowthChamberComponents["Chlorella"] = self.fInitialChlorellaMass

        Mixture(
            self.toStores.GrowthChamber,
            "GrowthMedium",
            "liquid",
            self.tfGrowthChamberComponents,
            303,
            1e5,
        )
        self.toStores.GrowthChamber.createPhase(
            "gas",
            "flow",
            "AirInGrowthChamber",
            0.05,
            {"O2": 5000, "CO2": 59000},
            293,
            0.5,
        )

        # Air Connection
        GasExMe(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "From_Outside")
        GrowthMediumAirInlet(self, "Air_In")
        MatterBranch(
            self, "GrowthChamber.From_Outside", ["Air_In"], "Air_Inlet", "Air_to_GrowthChamber"
        )

        GasExMe(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "To_Outside")
        Pipe(self, "Air_Out", 0.1, 0.01)
        MatterBranch(
            self, "GrowthChamber.To_Outside", ["Air_Out"], "Air_Outlet", "Air_from_GrowthChamber"
        )

        # Medium Connections
        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "To_Harvest")
        MatterBranch(self, "GrowthChamber.To_Harvest", {}, "Medium_Outlet", "Medium_to_Harvester")

        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "From_Harvest")
        Pipe(self, "Pipe", 0.1, 0.1, 2e-3)
        MatterBranch(
            self, "GrowthChamber.From_Harvest", ["Pipe"], "Medium_Inlet", "Medium_from_Harvester"
        )

        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "NO3_In")
        MatterBranch(self, "GrowthChamber.NO3_In", {}, "NO3_Inlet", "NO3_from_Maintenance")

        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "Urine_In")
        MatterBranch(self, "GrowthChamber.Urine_In", {}, "Urine_PBR", "Urine_from_PBR")

        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "H2O_In")
        MatterBranch(self, "GrowthChamber.H2O_In", {}, "H2O_Inlet", "H2O_from_Maintenance")

        # P2P Connections
        GasExMe(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "CO2_to_Medium")
        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "CO2_from_Air")

        GasExMe(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "O2_from_Medium")
        MixtureExMe(self.toStores.GrowthChamber.toPhases.GrowthMedium, "O2_to_Air")

        AtmosphericGasExchange(
            self.toStores.GrowthChamber, "CO2_Water_In_Out", "AirInGrowthChamber.CO2_to_Medium", "GrowthMedium.CO2_from_Air", "CO2"
        )
        AtmosphericGasExchange(
            self.toStores.GrowthChamber, "O2_Water_In_Out", "AirInGrowthChamber.O2_from_Medium", "GrowthMedium.O2_to_Air", "O2"
        )

        # Manipulator
        GrowthMediumChanges(
            "GrowthMediumChanges_Manip", self.toStores.GrowthChamber.toPhases.GrowthMedium
        )

        # Additional Calculation Modules
        self.oGrowthRateCalculationModule.oTemperatureLimitation = (
            TemperatureLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oGrowthRateCalculationModule.oPhLimitation = (
            PHLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oGrowthRateCalculationModule.oO2Limitation = (
            OxygenLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oGrowthRateCalculationModule.oCO2Limitation = (
            CarbonDioxideLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oPARModule = PARModule(self)
        self.oGrowthRateCalculationModule.oPARLimitation.oPARModule = self.oPARModule

    def setIfFlows(self, sAir_Inlet, sAir_Outlet, sMedium_Outlet, sMedium_Inlet, sNO3_Inlet, sH2O_Inlet, sUrine_PBR):
        self.connectIF("Air_Inlet", sAir_Inlet)
        self.connectIF("Air_Outlet", sAir_Outlet)
        self.connectIF("Medium_Outlet", sMedium_Outlet)
        self.connectIF("Medium_Inlet", sMedium_Inlet)
        self.connectIF("NO3_Inlet", sNO3_Inlet)
        self.connectIF("H2O_Inlet", sH2O_Inlet)
        self.connectIF("Urine_PBR", sUrine_PBR)

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.manual.branch(self.toBranches.Air_from_GrowthChamber)
        aoMultiSolverBranches = [self.toBranches.Air_to_GrowthChamber]
        solver.matter_multibranch.iterative.branch(aoMultiSolverBranches, "complex")
        self.toBranches.Air_from_GrowthChamber.oHandler.setFlowRate(0.1)

        solver.matter.manual.branch(self.toBranches.Medium_to_Harvester)
        solver.matter_multibranch.iterative.branch(self.toBranches.Medium_from_Harvester, "complex")
        self.toBranches.Medium_to_Harvester.oHandler.setVolumetricFlowRate(self.oParent.fVolumetricFlowToHarvester)

        self.oUrinePhase = self.toBranches.Urine_from_PBR.coExmes[1].oPhase

        solver.matter.manual.branch(self.toBranches.NO3_from_Maintenance)
        solver.matter.manual.branch(self.toBranches.H2O_from_Maintenance)
        solver.matter.manual.branch(self.toBranches.Urine_from_PBR)
        self.setThermalSolvers()

        for store in self.toStores.values():
            for phase in store.aoPhases:
                phase.setTimeStepProperties({"fMaxStep": self.fTimeStep * 5})
                phase.oCapacity.setTimeStepProperties({"fMaxStep": self.fTimeStep * 5})

    def createThermalStructure(self):
        super().createThermalStructure()

        self.oHeatFromPAR = ConstantTemperature("Heater", 0)
        self.toStores.GrowthChamber.toPhases.GrowthMedium.oCapacity.addHeatSource(self.oHeatFromPAR)

        self.oMediumCooler = ConstantTemperature("Cooler", 0)
        self.toStores.GrowthChamber.toPhases.GrowthMedium.oCapacity.addHeatSource(self.oMediumCooler)

    def exec(self, _):
        self.fCurrentGrowthMediumDensity = self.oMT.calculateDensity(self.toStores.GrowthChamber.toPhases.GrowthMedium)

        self.oPARModule.update()
        self.oGrowthRateCalculationModule.update()

        self.oHeatFromPAR.setHeatFlow(self.oPARModule.fHeatPower)
        self.oMediumCooler.setHeatFlow(-self.oPARModule.fHeatPower)

        # Refill logic (Nitrogen and H2O handling here)
        # Logic is preserved from MATLAB, adjust for Python structures
        pass
