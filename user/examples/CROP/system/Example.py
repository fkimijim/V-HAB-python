class Example(vsys):
    """
    EXAMPLE simulation for a CROP filter in V-HAB 2.0.
    """

    def __init__(self, oParent, sName):
        """
        Constructor function for Example class.
        """
        super().__init__(oParent, sName, 300)

        # Different urine concentrations for the CROP system
        self.mfUrineConcentrations = [3.5, 7, 20, 40, 60, 80, 100] / 100

        for iCROP in range(len(self.mfUrineConcentrations)):
            components.matter.CROP.CROP(self, f"CROP_{iCROP+1}")

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        """
        Creates the matter structure for the simulation.
        """
        super().createMatterStructure()

        matter.store(self, "Atmosphere", 1e6)
        oEnvironment = self.toStores.Atmosphere.createPhase(
            "gas", "boundary", "Environment", 1e6,
            {"N2": 8e4, "O2": 2e4, "CO2": 400, "NH3": 1}, 293, 0.5
        )

        # Create a store for the CROP system output
        matter.store(self, "CROP_Solution_Storage", 100)
        oSolutionPhase = matter.phases.liquid(
            self.toStores.CROP_Solution_Storage,
            "Solution", {"H2O": 0.1}, 295, 101325
        )

        matter.store(self, "CalciteSupply", 1)
        oCalciteSupply = self.toStores.CalciteSupply.createPhase(
            "mixture", "boundary", "CalciteSupply", "liquid",
            self.toStores.CalciteSupply.fVolume, {"CaCO3": 1}, 293, 1e5
        )

        fWaterMass = 1000
        fVolume = 1000 / 998.2

        # Urine concentrations for 100% urine
        tfConcentration = {
            "CH4N2O": 15 / 60.06,
            "NH3": 0,
            "NH4": 1.55 / 53.49,
            "Cl": 1.55 / 53.49 + 4.83 / 58.44 + 0.29 / 74.55 + 2 * 0.47 / 203.3,
            "NO2": 0,
            "NO3": 0,
            "C6H5O7": 0.65 / 293.1,
            "Na": 3 * 0.65 / 293.1 + 4.83 / 58.44 + 2 * 2.37 / 142.04,
            "SO4": 2.37 / 142.04,
            "HPO4": 4.12 / 174.18,
            "K": 2 * 4.12 / 174.18 + 0.29 / 74.55,
            "Mg": 0.47 / 203.3,
            "Ca": 0.5 / 147.01,
            "CO3": 0
        }

        afMolMass = self.oMT.afMolarMass
        tiN2I = self.oMT.tiN2I

        for i, concentration in enumerate(self.mfUrineConcentrations):
            store_name = f"UrineStorage_{i+1}"
            oStore = matter.store(self, store_name, 20)
            oUrinePhase = matter.phases.mixture(
                oStore, "Urine", "liquid",
                {
                    "H2O": fWaterMass,
                    "CH4N2O": concentration * tfConcentration["CH4N2O"] * 1000 * fVolume * afMolMass[tiN2I["CH4N2O"]],
                    "NH3": concentration * tfConcentration["NH3"] * 1000 * fVolume * afMolMass[tiN2I["NH3"]],
                    "NH4": concentration * tfConcentration["NH4"] * 1000 * fVolume * afMolMass[tiN2I["NH4"]],
                    "NO2": concentration * tfConcentration["NO2"] * 1000 * fVolume * afMolMass[tiN2I["NO2"]],
                    "NO3": concentration * tfConcentration["NO3"] * 1000 * fVolume * afMolMass[tiN2I["NO3"]],
                    "Ca2plus": concentration * tfConcentration["Ca"] * 1000 * fVolume * afMolMass[tiN2I["Ca"]],
                    "Clminus": concentration * tfConcentration["Cl"] * 1000 * fVolume * afMolMass[tiN2I["Cl"]],
                    "C6H5O7": concentration * tfConcentration["C6H5O7"] * 1000 * fVolume * afMolMass[tiN2I["C6H5O7"]],
                    "Naplus": concentration * tfConcentration["Na"] * 1000 * fVolume * afMolMass[tiN2I["Na"]],
                    "SO4": concentration * tfConcentration["SO4"] * 1000 * fVolume * afMolMass[tiN2I["SO4"]],
                    "HPO4": concentration * tfConcentration["HPO4"] * 1000 * fVolume * afMolMass[tiN2I["HPO4"]],
                    "Kplus": concentration * tfConcentration["K"] * 1000 * fVolume * afMolMass[tiN2I["K"]],
                    "Mg2plus": concentration * tfConcentration["Mg"] * 1000 * fVolume * afMolMass[tiN2I["Mg"]]
                },
                295, 101325
            )

            matter.branch(self, f"CROP_Urine_Inlet_{i+1}", {}, oUrinePhase)
            matter.branch(self, f"CROP_Solution_Outlet_{i+1}", {}, oSolutionPhase)
            matter.branch(self, f"CROP_Air_Inlet_{i+1}", {}, oEnvironment)
            matter.branch(self, f"CROP_Air_Outlet_{i+1}", {}, oEnvironment)
            matter.branch(self, f"CROP_Calcite_Inlet_{i+1}", {}, oCalciteSupply)

            self.toChildren[f"CROP_{i+1}"].setIfFlows(
                f"CROP_Urine_Inlet_{i+1}",
                f"CROP_Solution_Outlet_{i+1}",
                f"CROP_Air_Inlet_{i+1}",
                f"CROP_Air_Outlet_{i+1}",
                f"CROP_Calcite_Inlet_{i+1}"
            )

    def createSolverStructure(self):
        """
        Creates the solver structure for the simulation.
        """
        super().createSolverStructure()

        csStoreNames = self.toStores.keys()
        for store_name in csStoreNames:
            for oPhase in self.toStores[store_name].aoPhases:
                tTimeStepProperties = {"fMaxStep": self.fTimeStep * 5}
                oPhase.setTimeStepProperties(tTimeStepProperties)
                oPhase.oCapacity.setTimeStepProperties(tTimeStepProperties)

        tTimeStepProperties = {"rMaxChange": float("inf")}
        solution_phase = self.toStores.CROP_Solution_Storage.toPhases.Solution
        solution_phase.setTimeStepProperties(tTimeStepProperties)
        solution_phase.oCapacity.setTimeStepProperties(tTimeStepProperties)

        self.setThermalSolvers()

    def exec(self, _):
        """
        Execute function for this system.
        """
        super().exec()
        self.oTimer.synchronizeCallBacks()
