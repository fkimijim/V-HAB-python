import numpy as np

class Example:
    def __init__(self, oParent, sName):
        self.oParent = oParent
        self.sName = sName
        self.fTimeStep = 1  # [s]
        self.iSwitchCount = 1

        # DATA INITIALIZATIONS
        self.txInput = {
            "fTemperature": 303.15,  # [K]
            "rRelHumidity": 0.2,  # [ ]
            "fPressure": 8.41e4,  # [Pa]
            "fCO2Percent": 0.005,  # [%]
            "Fiber": {
                "fCount": 118,
                "fInnerDiameter": 0.00039116,  # [m]
                "fThickness": 0.00014,  # [m]
                "fLength": 0.1524,  # [m]
                "fPorosity": 1
            },
            "Tube": {
                "fCount": 1,
                "fInnerDiameter": 0.03683,  # [m]
                "fThickness": 0.01524  # [m]
            },
            "iCellNumber": 3,
            "iTubeNumber": 2,
            "rWaterVolFraction": 0.04,
            "fReservoirSizeIncreaseFactor": 100,
            "fPipelength": 1,  # [m]
            "fPipeDiameter": 0.01,  # [m]
            "fFrictionFactor": 2e-4
        }

        self.tTestData = self.load_and_condition_experimental_data()

    def load_and_condition_experimental_data(self):
        # Load data from CSV (Simulating MATLAB import behavior)
        afUpTime, afUpCO2 = self.import_CO2_file('April-04-2017-upstrm2.csv', 3, 1220)
        afDnTime, afDnCO2 = self.import_CO2_file('April-04-2017-dwnstrm2.csv', 3, 1217)

        # Remove pre-test setup data points
        afUpTime, afUpCO2 = afUpTime[106:], afUpCO2[106:]
        afDnTime, afDnCO2 = afDnTime[102:], afDnCO2[102:]

        afUpErr = np.full_like(afUpCO2, 50)
        afUpErr[afUpCO2 >= 1667] = 0.03 * afUpCO2[afUpCO2 >= 1667]
        afDnErr = np.full_like(afDnCO2, 50)
        afDnErr[afDnCO2 >= 1667] = 0.03 * afDnCO2[afDnCO2 >= 1667]

        # Initialize common time array
        afTime_C = np.linspace(min(np.hstack([afDnTime, afUpTime])), max(np.hstack([afDnTime, afUpTime])), 1200)[:-1]
        dt = afTime_C[1] - afTime_C[0]
        print(f"Bin Width: {dt:.2f} [s]")

        # Initialize data arrays to size of common time
        afUpCO2_C, afUpCO2_E = np.full(len(afTime_C) - 1, np.nan), np.full(len(afTime_C) - 1, np.nan)
        afDnCO2_C, afDnCO2_E = np.full(len(afTime_C) - 1, np.nan), np.full(len(afTime_C) - 1, np.nan)

        for i in range(len(afTime_C) - 1):
            # Find and average measurements for upstream and downstream
            iFindUp = np.where((afTime_C[i] <= afUpTime) & (afUpTime <= afTime_C[i + 1]))[0]
            afUpCO2_C[i] = np.mean(afUpCO2[iFindUp])
            afUpCO2_E[i] = np.sum(afUpErr[iFindUp]) / len(iFindUp)

            iFindDn = np.where((afTime_C[i] <= afDnTime) & (afDnTime <= afTime_C[i + 1]))[0]
            afDnCO2_C[i] = np.mean(afDnCO2[iFindDn])
            afDnCO2_E[i] = np.sum(afDnErr[iFindDn]) / len(iFindDn)

        # Remove data gaps
        iDelete = np.isnan(afUpCO2_C) | np.isnan(afDnCO2_C)
        afTime_C = np.delete(afTime_C, iDelete)
        afUpCO2_C, afDnCO2_C = afUpCO2_C[~iDelete], afDnCO2_C[~iDelete]
        afUpCO2_E, afDnCO2_E = afUpCO2_E[~iDelete], afDnCO2_E[~iDelete]

        # Convert datetime values to seconds
        afTime = (afTime_C - afTime_C[0]).astype(float)

        return {
            "afUpCO2": afUpCO2_C,
            "afDnCO2": afDnCO2_C,
            "afTime": afTime
        }

    def import_CO2_file(self, filename, start_row, end_row):
        """
        Simulated import of CO2 data from file.
        Replace with actual file reading logic using pandas or numpy.
        """
        # Simulate imported data (example only)
        time_data = np.linspace(0, 10000, 2000)
        co2_data = np.random.normal(500, 50, 2000)
        return time_data[start_row:end_row], co2_data[start_row:end_row]

    def exec(self):
        """
        Execution logic for system state changes.
        Updates inlet flow conditions based on experimental data.
        """
        fPressure = self.txInput["fPressure"]
        fTemperature = self.txInput["fTemperature"]

        if self.iSwitchCount < len(self.tTestData["afUpCO2"]) and self.oParent.oTimer.fTime > self.tTestData["afTime"][self.iSwitchCount]:
            self.iSwitchCount += 1
            oBoundary = self.toStores["Aether"].toPhases["Air"]
            tProperties = {"afPP": oBoundary.afPP.copy()}
            tProperties["afPP"][self.oMT["tiN2I"]["CO2"]] = self.tTestData["afUpCO2"][self.iSwitchCount - 1] / 1e6 * fPressure
            oBoundary.setBoundaryProperties(tProperties)
