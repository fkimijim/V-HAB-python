import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.vsys import BaseSystem

vsys = BaseSystem()

class Human(vsys):
    """
    Human model subsystem
    """

    def __init__(
        self, 
        oParent, 
        sName, 
        bMale, 
        fAge, 
        fHumanMass, 
        fHumanHeight, 
        txCrewPlaner, 
        iNumberOfHumans=1, 
        trInitialFoodComposition=None
    ):
        super().__init__(oParent, sName, 2 * 60)

        eval(self.oRoot.oCfgParams.configCode(self))

        self.iNumberOfHumans = iNumberOfHumans
        self.txCrewPlaner = txCrewPlaner
        self.trInitialFoodComposition = trInitialFoodComposition or {
            "Fat": 0.3,
            "Protein": 0.2,
            "Carbohydrate": 0.5,
        }

        self.fFecesSolidProduction = (0.032 / 86400) * self.iNumberOfHumans

        # Nutritional energy content
        self.tfEnergyContent = {
            "Fat": self.oMT.afNutritionalEnergy[self.oMT.tiN2I["C16H32O2"]],
            "Protein": self.oMT.afNutritionalEnergy[self.oMT.tiN2I["C4H5ON"]],
            "Carbohydrate": self.oMT.afNutritionalEnergy[self.oMT.tiN2I["C6H12O6"]],
        }

        # Basic energy demand calculation
        self.fBasicFoodEnergyDemand = self.calculate_energy_demand(
            bMale, fAge, fHumanMass, fHumanHeight
        )

        self.fVO2_max = self.calculate_vo2_max(bMale, fAge)
        self.fHumanMass = self.iNumberOfHumans * fHumanMass
        self.fHumanHeight = fHumanHeight

        # States
        self.csStates = [
            "sleep",
            "nominal",
            "exercise015",
            "exercise1530",
            "recovery015",
            "recovery1530",
            "recovery3045",
            "recovery4560",
        ]

        # Initialize human metabolic values
        self.initialize_metabolic_values()

    def calculate_energy_demand(self, bMale, fAge, fHumanMass, fHumanHeight):
        """
        Calculate the basic energy demand for a human.
        """
        if bMale:
            return (
                self.iNumberOfHumans
                * 10**6
                * (622 - 9.53 * fAge + 1 * (15.9 * fHumanMass + 539.6 * fHumanHeight))
                / (0.238853 * 10**3)
            )
        else:
            return (
                self.iNumberOfHumans
                * 10**6
                * (354 - 6.91 * fAge + 1 * (9.36 * fHumanMass + 726 * fHumanHeight))
                / (0.238853 * 10**3)
            )

    def calculate_vo2_max(self, bMale, fAge):
        """
        Calculate VO2_max based on age and gender.
        """
        if bMale:
            if fAge < 30:
                return 51.4
            elif fAge < 40:
                return 50.4
            elif fAge < 50:
                return 48.2
            elif fAge < 60:
                return 45.3
            else:
                return 42.5
        else:
            if fAge < 30:
                return 44.2
            elif fAge < 40:
                return 41.0
            elif fAge < 50:
                return 39.5
            elif fAge < 60:
                return 35.2
            else:
                return 35.2

    def initialize_metabolic_values(self):
        """
        Initialize metabolic values for various human states.
        """
        self.tHumanMetabolicValues = {
            "sleep": {
                "fDryHeat": 224 * 1000 / 3600,
                "fWaterVapor": 6.3e-4 / 60,
                "fSweat": 0,
                "fO2Consumption": 3.6e-4 / 60,
                "fCO2Production": 4.55e-4 / 60,
            },
            "nominal": {
                "fDryHeat": 329 * 1000 / 3600,
                "fWaterVapor": 11.77e-4 / 60,
                "fSweat": 0,
                "fO2Consumption": 5.68e-4 / 60,
                "fCO2Production": 7.2e-4 / 60,
            },
            "exercise015": {
                "fDryHeat": 514 * 1000 / 3600,
                "fWaterVapor": 46.16e-4 / 60,
                "fSweat": 1.56e-4 / 60,
                "fO2Consumption": 39.40e-4 / 60,
                "fCO2Production": 49.85e-4 / 60,
            },
            "exercise1530": {
                "fDryHeat": 624 * 1000 / 3600,
                "fWaterVapor": 128.42e-4 / 60,
                "fSweat": 33.52e-4 / 60,
                "fO2Consumption": 39.40e-4 / 60,
                "fCO2Production": 49.85e-4 / 60,
            },
            # Additional states omitted for brevity
        }

    def createMatterStructure(self):
        """
        Create the matter structure for the human subsystem.
        """
        super().createMatterStructure()

        fHumanTemperature = 298.15  # 25°C
        tfMassesFeces = {"Feces": 0.1}
        tfMassesUrine = {"Urine": 1.6}
        tfMassesStomach = {"Human_Tissue": 2}

        # Creating stores
        self.create_human_store(fHumanTemperature, tfMassesFeces, tfMassesUrine, tfMassesStomach)

    def create_human_store(self, fHumanTemperature, tfMassesFeces, tfMassesUrine, tfMassesStomach):
        """
        Initialize the human-related stores and phases.
        """
        # Placeholder for human store logic, similar to the original MATLAB function.
        pass

    def setState(self, iState):
        """
        Update the human state and metabolic values.
        """
        self.iState = iState
        self.fStateStartTime = self.oTimer.fTime

        afHumidityP2PFlowRates = [0] * self.oMT.iSubstances
        afHumidityP2PFlowRates[self.oMT.tiN2I["H2O"]] = (
            self.tHumanMetabolicValues[self.csStates[iState + 1]]["fWaterVapor"]
            + self.tHumanMetabolicValues[self.csStates[iState + 1]]["fSweat"]
        )
        self.toStores.Human.toProcsP2P.CrewHumidityProduction.setFlowRate(
            self.iNumberOfHumans * afHumidityP2PFlowRates
        )

    def exec(self):
        """
        Execution logic for the human subsystem.
        """
        super().exec()
        # Detailed simulation logic adapted from MATLAB
        pass
