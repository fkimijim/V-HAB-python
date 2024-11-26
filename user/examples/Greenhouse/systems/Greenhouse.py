class Greenhouse:
    def __init__(self, oParent, sName):
        self.oParent = oParent
        self.sName = sName
        self.fCO2 = 330  # PPM
        self.bTurnedNutrientsOff = False
        self.txPlants = {}
        self.fMaxTimeStep = 3600
        self.fDayModuleCounter = 0
        self.mfPlantLightEnergy = []
        self.tfPlantControlParameters = {}

        self.txPlants["iAssumedPreviousPlantGrowthDays"] = 0
        self.txPlants["csPlants"] = ['Sweetpotato', 'Whitepotato', 'Rice', 'Drybean', 'Soybean', 'Tomato',
                                     'Peanut', 'Lettuce', 'Wheat', 'Wheat_I', 'Whitepotato_I', 'Soybean_I']
        self.txPlants["mfPlantArea"] = [20] * len(self.txPlants["csPlants"])
        self.txPlants["mfHarvestTime"] = [85, 132, 85, 85, 97, 85, 104, 28, 70, 85, 138, 97]
        self.txPlants["miSubcultures"] = [1] * len(self.txPlants["csPlants"])
        self.txPlants["mfPhotoperiod"] = [12, 12, 12, 18, 12, 12, 12, 16, 20, 20, 12, 12]
        self.txPlants["mfPPFD"] = [650, 650, 764, 370, 650, 625, 625, 295, 1330, 690, 860, 650]
        self.txPlants["mfEmergeTime"] = [0] * len(self.txPlants["csPlants"])

        iLengthOfMission = 180  # days
        self.tInput = {}

        for iPlant in range(len(self.txPlants["csPlants"])):
            mfFirstSowTimeInit = [x for x in range(0, self.txPlants["mfHarvestTime"][iPlant],
                                                   self.txPlants["mfHarvestTime"][iPlant] // self.txPlants["miSubcultures"][iPlant])]
            mfFirstSowTimeInit = [x - self.txPlants["iAssumedPreviousPlantGrowthDays"] for x in mfFirstSowTimeInit]
            mfFirstSowTimeInit = [x for x in mfFirstSowTimeInit if x >= 0]

            mfPlantTimeInit = [0 if x < 0 else x % self.txPlants["mfHarvestTime"][iPlant] for x in mfFirstSowTimeInit]

            for iSubculture in range(1, self.txPlants["miSubcultures"][iPlant] + 1):
                sName = f"{self.txPlants['csPlants'][iPlant]}_{iSubculture}"
                sPlantSpecies = self.txPlants["csPlants"][iPlant].split('_')[0]
                self.tInput[(iPlant, iSubculture)] = {
                    "sName": sName,
                    "sPlantSpecies": sPlantSpecies,
                    "fGrowthArea": self.txPlants["mfPlantArea"][iPlant],
                    "fHarvestTime": self.txPlants["mfHarvestTime"][iPlant],
                    "fEmergeTime": self.txPlants["mfEmergeTime"][iPlant],
                    "fPPFD": self.txPlants["mfPPFD"][iPlant],
                    "fPhotoperiod": self.txPlants["mfPhotoperiod"][iPlant],
                    "iConsecutiveGenerations": 1 + (iLengthOfMission // self.txPlants["mfHarvestTime"][iPlant])
                }

    def create_matter_structure(self):
        fTemperature = 293
        rRelativeHumidity = 0.7
        fTotalPressure = 101325
        fCO2_ppm = 1000

        # Atmosphere
        self.Atmosphere = {
            "Temperature": fTemperature,
            "RelativeHumidity": rRelativeHumidity,
            "TotalPressure": fTotalPressure,
            "CO2_ppm": fCO2_ppm
        }

        # Nutrient Supply
        fN_Mol_Concentration = 1  # mol/m^3
        fN_Mass = fN_Mol_Concentration * 0.1 * 62  # Approximate NO3 molar mass
        fWaterMass = 0.1 * 998  # Water density in kg/m^3
        rNRatio = fN_Mass / (fN_Mass + fWaterMass)
        self.NutrientSupply = {
            "H2O": 1 - rNRatio,
            "NO3": rNRatio
        }

        # Biomass
        self.Biomass = {
            "Inedible": 0.5,
            "Edible": 0.5
        }

    def create_solver_structure(self):
        self.Solvers = {"complex": "matter_multibranch.iterative.branch"}
        self.TimeStepProperties = {"fMaxStep": self.fMaxTimeStep}
        self.ThermalSolvers = {}

    def calculate_co2_concentration(self):
        fCO2 = (self.Atmosphere["CO2_ppm"] * self.Atmosphere["TotalPressure"] /
                (self.Atmosphere["TotalPressure"] * 1e6))
        return fCO2

    def exec(self):
        # Example control logic for plant nutrient supply
        if not self.bTurnedNutrientsOff:
            if self.oTimer.fTime > 80 * 3600 * 24:  # After 80 days
                if self.NutrientSupply["NO3"] == 0:
                    self.bTurnedNutrientsOff = True
                else:
                    self.NutrientSupply["NO3"] = 0

        if self.oTimer.fTime % 86400 < self.fDayModuleCounter:
            self.oTimer.synchronize_callbacks()
        self.fDayModuleCounter = self.oTimer.fTime % 86400
