class Setup:
    def __init__(self, ptConfigParams, tSolverParams):
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.fSimTime = 35000
        self.bUseTime = True
        self.toMonitors = {"oLogger": Logger()}
        self.oSimulationContainer = SimulationContainer("ELY_FC", self.ptConfigParams, self.tSolverParams)
        self.oSimulationContainer.toChildren["ELY_FC"] = ELY_FC(self.oSimulationContainer, "ELY_FC")

    def configure_monitors(self):
        oLogger = self.toMonitors["oLogger"]
        oELY_FC = self.oSimulationContainer.toChildren["ELY_FC"]

        # Electrolyzer Logging
        for iPressure in range(len(oELY_FC.mfPressure)):
            for iTemperature in range(len(oELY_FC.mfTemperature)):
                sElectrolyzer = f"Electrolyzer_{oELY_FC.mfPressure[iPressure]}_{oELY_FC.mfTemperature[iTemperature]}"
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "rEfficiency", "-", f"{sElectrolyzer} Efficiency")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fStackCurrent", "A", f"{sElectrolyzer} Current")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fStackVoltage", "V", f"{sElectrolyzer} Voltage")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fPower", "W", f"{sElectrolyzer} Power")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fCellVoltage", "V", f"{sElectrolyzer} Cell Voltage")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fOhmicOverpotential", "V", f"{sElectrolyzer} Ohmic Overpotential")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fKineticOverpotential", "V", f"{sElectrolyzer} Kinetic Overpotential")
                oLogger.add_value(f"ELY_FC:c:{sElectrolyzer}", "fMassTransportOverpotential", "V", f"{sElectrolyzer} Mass Transport Overpotential")

    def plot(self):
        import matplotlib.pyplot as plt
        import numpy as np

        oELY_FC = self.oSimulationContainer.toChildren["ELY_FC"]
        oLogger = self.toMonitors["oLogger"]

        # Overpotential Plot
        plt.figure("Electrolyzer Overpotential for Different Pressures and Temperatures")

        # Subplot 1
        plt.subplot(1, 2, 1)
        colors = [[77 / 255, 175 / 255, 74 / 255], [228 / 255, 26 / 255, 28 / 255], [55 / 255, 126 / 255, 184 / 255]]

        for iPressure, pressure in enumerate(oELY_FC.mfPressure):
            iTemperature = oELY_FC.mfTemperature.index(50)
            sElectrolyzer = f"Electrolyzer_{pressure}_{oELY_FC.mfTemperature[iTemperature]}"
            oEly = oELY_FC.toChildren[sElectrolyzer]

            log_indices = oLogger.find_log_indices([
                f'"{sElectrolyzer} Current"', f'"{sElectrolyzer} Ohmic Overpotential"',
                f'"{sElectrolyzer} Kinetic Overpotential"', f'"{sElectrolyzer} Mass Transport Overpotential"'
            ])
            fCurrentDensity = oLogger.mfLog[:, log_indices[0]] / (oEly.fMembraneArea * 10000)  # A/cm²

            plt.plot(fCurrentDensity, oLogger.mfLog[:, log_indices[1]], color=colors[iPressure], linestyle='-', label=f"{pressure} bar Ohmic")
            plt.plot(fCurrentDensity, oLogger.mfLog[:, log_indices[2]], color=colors[iPressure], linestyle='--', label=f"{pressure} bar Kinetic")
            plt.plot(fCurrentDensity, oLogger.mfLog[:, log_indices[3]], color=colors[iPressure], linestyle='-.', label=f"{pressure} bar Mass Transport")

        plt.xlabel("Current Density / A/cm²")
        plt.ylabel("Overpotential / V")
        plt.legend()
        plt.grid(True)

        # Subplot 2
        plt.subplot(1, 2, 2)
        colors = [
            [77 / 255, 175 / 255, 74 / 255], [55 / 255, 126 / 255, 184 / 255],
            [228 / 255, 26 / 255, 28 / 255], [152 / 255, 78 / 255, 163 / 255], [255 / 255, 127 / 255, 0 / 255]
        ]

        for iTemperature, temperature in enumerate(oELY_FC.mfTemperature):
            iPressure = oELY_FC.mfPressure.index(10)
            sElectrolyzer = f"Electrolyzer_{oELY_FC.mfPressure[iPressure]}_{temperature}"
            oEly = oELY_FC.toChildren[sElectrolyzer]

            log_indices = oLogger.find_log_indices([
                f'"{sElectrolyzer} Current"', f'"{sElectrolyzer} Ohmic Overpotential"',
                f'"{sElectrolyzer} Kinetic Overpotential"', f'"{sElectrolyzer} Mass Transport Overpotential"'
            ])
            fCurrentDensity = oLogger.mfLog[:, log_indices[0]] / (oEly.fMembraneArea * 10000)  # A/cm²

            plt.plot(fCurrentDensity, oLogger.mfLog[:, log_indices[1]], color=colors[iTemperature], linestyle='-', label=f"{temperature} °C Ohmic")
            plt.plot(fCurrentDensity, oLogger.mfLog[:, log_indices[2]], color=colors[iTemperature], linestyle='--', label=f"{temperature} °C Kinetic")
            plt.plot(fCurrentDensity, oLogger.mfLog[:, log_indices[3]], color=colors[iTemperature], linestyle='-.', label=f"{temperature} °C Mass Transport")

        plt.xlabel("Current Density / A/cm²")
        plt.ylabel("Overpotential / V")
        plt.legend()
        plt.grid(True)

        plt.show()


class Logger:
    def __init__(self):
        self.mfLog = np.zeros((1000, 10))  # Example log structure
        self.values = {}

    def add_value(self, path, var, unit, desc):
        self.values[path] = {"var": var, "unit": unit, "desc": desc}

    def find_log_indices(self, variables):
        # Simulated implementation to find indices
        return [0, 1, 2, 3]


class SimulationContainer:
    def __init__(self, name, config_params, solver_params):
        self.name = name
        self.config_params = config_params
        self.solver_params = solver_params
        self.toChildren = {}


class ELY_FC:
    def __init__(self, parent, name):
        self.mfPressure = [1, 10, 100]
        self.mfTemperature = [30, 40, 50, 60, 70]
        self.toChildren = {}
        self.fMembraneArea = 1
