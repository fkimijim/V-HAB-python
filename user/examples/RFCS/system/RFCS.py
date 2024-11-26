import numpy as np
import pandas as pd

class RFCS:
    """
    Regenerative Fuel Cell System (RFCS) simulation.
    """

    def __init__(self, oParent, sName, fSolarPanelArea=50, rSolarpanelEfficiency=0.12):
        self.oParent = oParent
        self.sName = sName
        self.fTimeStep = 5 * 60  # 5-minute intervals
        self.fSolarPanelArea = fSolarPanelArea
        self.rSolarpanelEfficiency = rSolarpanelEfficiency
        self.fElectricalPayloadPower = 350  # W
        self.afPower = pd.read_excel(
            'HAPS_AvailableSolarPower.xlsx', usecols=[1, 2], skiprows=39, nrows=287
        ).to_numpy()
        self.afPower[:, 1] *= self.rSolarpanelEfficiency * self.fSolarPanelArea

        self.toStores = {}
        self.toChildren = {}
        self.toBranches = {}
        self.oTimer = None  # Placeholder for timer

        # Initialize subsystems
        self.initialize_components()

    def initialize_components(self):
        """
        Initialize components like Electrolyzer, Fuel Cell, and stores.
        """
        self.toChildren["Electrolyzer"] = Electrolyzer(30, 1e-2, 50e-6, 20000)
        self.toChildren["FuelCell"] = FuelCell(30)

        # Initialize stores
        self.create_matter_structure()

    def create_matter_structure(self):
        """
        Define the matter structure including stores and branches.
        """
        fInitialTemperature = 293

        # Define stores
        self.toStores["Water_Tank"] = Store(0.004, {"H2O": 1}, fInitialTemperature)
        self.toStores["CoolingSystem"] = Store(0.1, {"H2O": 1}, 340)
        self.toStores["H2_Tank"] = Store(0.1, {"H2": 50e5}, fInitialTemperature)
        self.toStores["O2_Tank"] = Store(0.05, {"O2": 50e5}, fInitialTemperature)

        # Define radiator and pipes
        self.toChildren["Radiator"] = Radiator(3.5, 0.4)
        self.toBranches["Radiator_Pipe"] = Pipe(3, 0.002)

        # Connect branches
        self.create_branches()

    def create_branches(self):
        """
        Connect branches between components.
        """
        self.toBranches["Radiator_Cooling"] = Branch(
            self.toStores["CoolingSystem"],
            [self.toBranches["Radiator_Pipe"], self.toChildren["Radiator"]],
            self.toStores["CoolingSystem"],
        )

        # Fuel Cell connections
        self.toBranches["FuelCell_H2_Inlet"] = Branch(
            self.toStores["H2_Tank"], [], None
        )
        self.toBranches["FuelCell_O2_Inlet"] = Branch(
            self.toStores["O2_Tank"], [], None
        )
        self.toBranches["FuelCell_Water_Outlet"] = Branch(
            None, [], self.toStores["Water_Tank"]
        )
        self.toBranches["FuelCell_Cooling_Inlet"] = Branch(
            self.toStores["CoolingSystem"], [], None
        )
        self.toBranches["FuelCell_Cooling_Outlet"] = Branch(
            None, [], self.toStores["CoolingSystem"]
        )

        # Electrolyzer connections
        self.toBranches["Electrolyzer_H2_Outlet"] = Branch(
            None, [], self.toStores["H2_Tank"]
        )
        self.toBranches["Electrolyzer_O2_Outlet"] = Branch(
            None, [], self.toStores["O2_Tank"]
        )
        self.toBranches["Electrolyzer_Water_Inlet"] = Branch(
            self.toStores["Water_Tank"], [], None
        )
        self.toBranches["Electrolyzer_Cooling_Inlet"] = Branch(
            self.toStores["CoolingSystem"], [], None
        )
        self.toBranches["Electrolyzer_Cooling_Outlet"] = Branch(
            None, [], self.toStores["CoolingSystem"]
        )

    def exec(self):
        """
        Execute the simulation logic.
        """
        # Calculate current time
        fCurrentTime = (self.oTimer.fTime / (24 * 3600)) + 0.5
        afTimeDataPoints = np.abs(self.afPower[:, 0] - np.mod(fCurrentTime, 1))
        fAvailablePower = (
            self.afPower[np.argmin(afTimeDataPoints), 1] - self.fElectricalPayloadPower
        )

        if fAvailablePower > 0:
            fLowestTankPressure = min(
                self.toStores["H2_Tank"].get_pressure(),
                self.toStores["O2_Tank"].get_pressure(),
            )
            if fLowestTankPressure > 50e5:
                fSetPower = (
                    (1 / ((fLowestTankPressure - 40e5) / 10e5) ** 2) * fAvailablePower
                )
            else:
                fSetPower = fAvailablePower
            self.toChildren["Electrolyzer"].set_power(fSetPower)
            self.toChildren["FuelCell"].set_power(0)
        else:
            self.toChildren["Electrolyzer"].set_power(0)
            self.toChildren["FuelCell"].set_power(-fAvailablePower)

        # Regulate coolant temperature
        fDeltaTemperature = (
            self.toStores["CoolingSystem"].get_temperature() - 338.15
        )
        if fDeltaTemperature > 0:
            self.toBranches["Radiator_Cooling"].set_flow_rate(
                0.2 * fDeltaTemperature
            )
        else:
            self.toBranches["Radiator_Cooling"].set_flow_rate(0)

        self.oTimer.synchronize_callbacks()
