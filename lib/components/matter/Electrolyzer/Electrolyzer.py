class Electrolyzer:
    """
    Model of an electrolyzer.
    Calculates the required voltage to cleave the water depending on pressure and temperature.
    """

    def __init__(self, oParent, sName, fTimeStep, txInput):
        self.oParent = oParent
        self.sName = sName
        self.fTimeStep = fTimeStep

        # Default properties
        self.fStackCurrent = 0
        self.fCellVoltage = 1.48
        self.fPower = 0
        self.iCells = 50
        self.fStackVoltage = None
        self.rEfficiency = 1
        self.fMembraneArea = 0.01  # m^2
        self.fMembraneThickness = 2.1e-4  # m
        self.fMaxCurrentDensity = 40000  # A/m^2
        self.fChargeTransferAnode = 1
        self.fChargeTransferCatode = 0.5
        self.fOhmicOverpotential = 0
        self.fKineticOverpotential = 0
        self.fMassTransportOverpotential = 0

        # Update properties from txInput
        valid_fields = [
            "iCells",
            "fMembraneArea",
            "fMembraneThickness",
            "fMaxCurrentDensity",
            "fChargeTransferAnode",
            "fChargeTransferCatode",
            "fPower",
        ]
        for key, value in txInput.items():
            if key in valid_fields:
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid input {key} for the electrolyzer")

        self.fStackVoltage = self.iCells * self.fCellVoltage

    def create_matter_structure(self):
        """
        Create the matter structure for the electrolyzer.
        """
        # Store and phases (assuming relevant methods exist)
        fInitialTemperature = 293

        self.toStores = {
            "Electrolyzer": {
                "Membrane": {
                    "type": "liquid",
                    "volume": 0.4 * self.iCells * self.fMembraneArea,
                    "composition": {"H2O": 0.5, "H2": 0.25, "O2": 0.25},
                    "temperature": fInitialTemperature,
                    "pressure": 1e5,
                },
                "H2_Channel": {
                    "type": "gas",
                    "volume": 0.05,
                    "composition": {"H2": 1e5},
                    "temperature": fInitialTemperature,
                    "pressure": 0.8,
                },
                "O2_Channel": {
                    "type": "gas",
                    "volume": 0.05,
                    "composition": {"O2": 1e5},
                    "temperature": fInitialTemperature,
                    "pressure": 0.8,
                },
                "ProductWater": {
                    "type": "liquid",
                    "volume": 0.01334 * self.iCells * self.fMembraneArea,
                    "composition": {"H2O": 1},
                    "temperature": fInitialTemperature,
                    "pressure": 1e5,
                },
                "CoolingSystem": {
                    "type": "liquid",
                    "volume": 0.0001,
                    "composition": {"H2O": 1},
                    "temperature": 340,
                    "pressure": 1e5,
                },
            }
        }

        # Pipes, valves, and manipulators
        self.components = {
            "pipes": {
                "Pipe_H2_Out": {"length": 1.5, "diameter": 0.003},
                "Pipe_O2_Out": {"length": 1.5, "diameter": 0.003},
                "Pipe_Water_In": {"length": 1.5, "diameter": 0.003},
                "Pipe_Cooling_In": {"length": 1.5, "diameter": 0.003},
                "Pipe_Cooling_Out": {"length": 1.5, "diameter": 0.003},
            },
            "valves": {
                "Valve_H2": {"is_open": True},
                "Valve_O2": {"is_open": True},
            },
        }

        # Add manipulator and P2P flows
        self.manipulators = {
            "ElectrolyzerReaction": {
                "type": "ElectrolyzerReaction",
                "phase": self.toStores["Electrolyzer"]["Membrane"],
            }
        }
        self.p2p_flows = {
            "H2_from_Membrane": {
                "from": self.toStores["Electrolyzer"]["Membrane"],
                "to": self.toStores["Electrolyzer"]["H2_Channel"],
            },
            "O2_from_Membrane": {
                "from": self.toStores["Electrolyzer"]["Membrane"],
                "to": self.toStores["Electrolyzer"]["O2_Channel"],
            },
            "H2O_to_Membrane": {
                "from": self.toStores["Electrolyzer"]["ProductWater"],
                "to": self.toStores["Electrolyzer"]["Membrane"],
            },
        }

    def calculate_voltage(self):
        """
        Calculate the voltage of the electrolyzer.
        """
        fTemperature = self.toStores["Electrolyzer"]["CoolingSystem"]["temperature"]

        fPressureH2 = self.toStores["Electrolyzer"]["H2_Channel"]["pressure"]
        fPressureO2 = self.toStores["Electrolyzer"]["O2_Channel"]["pressure"]
        fPressureH2O = self.toStores["Electrolyzer"]["ProductWater"]["pressure"]

        fOpenCircuitCellVoltage = self.calculate_open_circuit_cell_voltage(
            fTemperature, fPressureH2, fPressureO2, fPressureH2O
        )

        if self.fPower == 0:
            self.fCellVoltage = fOpenCircuitCellVoltage
        else:
            fMaxCurrent = self.fMaxCurrentDensity * self.fMembraneArea
            self.fStackCurrent = self.fPower / self.fStackVoltage
            if self.fStackCurrent > fMaxCurrent:
                self.fStackCurrent = fMaxCurrent
            self.fPower = self.fStackCurrent * self.fStackVoltage

            # Calculate heat flow
            fHeatFlow = self.fStackCurrent * self.fStackVoltage * (1 - self.rEfficiency)
            self.toStores["Electrolyzer"]["CoolingSystem"][
                "heat_source"
            ] = fHeatFlow  # Assuming structure to add heat flow

    def calculate_open_circuit_cell_voltage(
        self, fTemperature, fPressureH2, fPressureO2, fPressureH2O
    ):
        """
        Calculate the open circuit cell voltage using the Nernst equation.
        """
        return (
            1.229
            - 0.9 * 10 ** -3 * (fTemperature - 298)
            + (8.314 * fTemperature / (2 * 96485))
            * (fPressureH2 * fPressureO2 ** 0.5 / fPressureH2O)
        )

    def set_power(self, fPower):
        """
        Set the power for the electrolyzer and adjust related parameters.
        """
        self.fPower = fPower
        self.calculate_voltage()

        if self.fPower > 0:
            self.components["valves"]["Valve_H2"]["is_open"] = True
            self.components["valves"]["Valve_O2"]["is_open"] = True
        elif self.fPower == 0:
            self.components["valves"]["Valve_H2"]["is_open"] = False
            self.components["valves"]["Valve_O2"]["is_open"] = False
