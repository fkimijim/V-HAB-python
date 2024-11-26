import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

class Setup:
    def __init__(self, ptConfigParams=None, tSolverParams=None):
        self.fSimTime = 10  # Simulation time in seconds
        self.bUseTime = True
        self.toMonitors = {"oLogger": Logger()}
        
        if ptConfigParams is None:
            self.example_system = ExampleSystem(self, "Example", {})
        else:
            tParameters = ptConfigParams["tParameters"]
            self.example_system = ExampleSystem(self, "Example", tParameters)
            if "iSimTicks" in tParameters:
                self.iSimTicks = tParameters["iSimTicks"]
                self.bUseTime = False

    def configure_monitors(self):
        oLog = self.toMonitors["oLogger"]
        
        for iProtoflightTest in range(1, 7):
            oLog.add_value(f"Example:s:Cabin_{iProtoflightTest}.toPhases.Air", "rRelHumidity", "-", f"Relative Humidity Cabin_{iProtoflightTest}")
            oLog.add_value(f"Example:s:Cabin_{iProtoflightTest}.toPhases.Air", "fTemperature", "K", f"Temperature Cabin_{iProtoflightTest}")
            oLog.add_value(f"Example:c:CCAA_{iProtoflightTest}:c:CCAA_CHX", "fTotalCondensateHeatFlow", "W", f"CCAA_{iProtoflightTest} Condensate Heat Flow")
            oLog.add_value(f"Example:c:CCAA_{iProtoflightTest}:c:CCAA_CHX", "fTotalHeatFlow", "W", f"CCAA_{iProtoflightTest} Total Heat Flow")
            oLog.add_value(f"Example:c:CCAA_{iProtoflightTest}:c:CCAA_CHX", "fTempOut_Fluid1", "K", f"CCAA_{iProtoflightTest} Air Outlet Temperature")
            oLog.add_value(f"Example:c:CCAA_{iProtoflightTest}:c:CCAA_CHX", "fTempOut_Fluid2", "K", f"CCAA_{iProtoflightTest} Coolant Outlet Temperature")
            oLog.add_value(f"Example:c:CCAA_{iProtoflightTest}:s:CHX.toProcsP2P.CondensingHX", "fFlowRate", "kg/s", f"CCAA_{iProtoflightTest} Condensate Flow Rate")
            oLog.add_value(f"Example:c:CCAA_{iProtoflightTest}:s:Mixing.toPhases.MixedGas", "fTemperature", "K", f"CCAA_{iProtoflightTest} Mixed Air Outlet Temperature")

    def plot(self):
        plt.close("all")
        oPlotter = Plotter(self)
        
        csRelativeHumidities = [f'"Relative Humidity Cabin_{i}"' for i in range(1, 7)]
        csTemperatures = [f'"Temperature Cabin_{i}"' for i in range(1, 7)]
        csCondensateHeatFlow = [f'"CCAA_{i} Condensate Heat Flow"' for i in range(1, 7)]
        csTotalHeatFlow = [f'"CCAA_{i} Total Heat Flow"' for i in range(1, 7)]
        csAirOutTemperature = [f'"CCAA_{i} Air Outlet Temperature"' for i in range(1, 7)]
        csCoolantOutTemperature = [f'"CCAA_{i} Coolant Outlet Temperature"' for i in range(1, 7)]
        csCondensateFlow = [f'"CCAA_{i} Condensate Flow Rate"' for i in range(1, 7)]

        oPlotter.define_plot(csTemperatures, "Temperature")
        oPlotter.define_plot(csRelativeHumidities, "Relative Humidity")
        oPlotter.define_plot(csCondensateHeatFlow + csTotalHeatFlow, "CCAA Heat Flows")
        oPlotter.define_plot(csCondensateFlow, "CCAA Condensate Flow Rate")
        oPlotter.define_plot(csAirOutTemperature, "CCAA Air Outlet Temperature")
        oPlotter.define_plot(csCoolantOutTemperature, "CCAA Coolant Outlet Temperature")
        oPlotter.plot()

        oLogger = self.toMonitors["oLogger"]
        mfAirOutletTemperature = np.zeros((oLogger.iLogIndex, 6))
        mfMixedAirOutletTemperature = np.zeros((oLogger.iLogIndex, 6))
        mfCoolantOutletTemperature = np.zeros((oLogger.iLogIndex, 6))
        mfCondensateFlow = np.zeros((oLogger.iLogIndex, 6))
        
        for log in oLogger.tLogValues:
            for iProtoflightTest in range(6):
                label_prefix = f"CCAA_{iProtoflightTest + 1}"
                if log["sLabel"] == f"{label_prefix} Air Outlet Temperature":
                    mfAirOutletTemperature[:, iProtoflightTest] = log["data"]
                elif log["sLabel"] == f"{label_prefix} Mixed Air Outlet Temperature":
                    mfMixedAirOutletTemperature[:, iProtoflightTest] = log["data"]
                elif log["sLabel"] == f"{label_prefix} Coolant Outlet Temperature":
                    mfCoolantOutletTemperature[:, iProtoflightTest] = log["data"]
                elif log["sLabel"] == f"{label_prefix} Condensate Flow Rate":
                    mfCondensateFlow[:, iProtoflightTest] = log["data"]

        Data = sio.loadmat("user/+examples/+CCAA/+TestData/ProtoflightData.mat")["ProtoflightTestData"]
        air_temp_diff = mfMixedAirOutletTemperature[3, :] - Data["AirOutletTemperature"].squeeze()
        coolant_temp_diff = mfCoolantOutletTemperature[3, :] - Data["CoolantOutletTemperature"].squeeze()
        condensate_diff = mfCondensateFlow[3, :] * 3600 - Data["CondensateMassFlow"].squeeze()

        print(f"The average difference in air outlet temperature is: {np.mean(air_temp_diff):.2f} K")
        print(f"The average difference in coolant outlet temperature is: {np.mean(coolant_temp_diff):.2f} K")
        print(f"The average difference in condensate is: {np.mean(condensate_diff):.2f} kg/h")


class Logger:
    def __init__(self):
        self.tLogValues = []
        self.iLogIndex = 0

    def add_value(self, path, variable, unit, label):
        self.tLogValues.append({"path": path, "variable": variable, "unit": unit, "sLabel": label, "data": np.random.rand(100)})


class ExampleSystem:
    def __init__(self, parent, name, params):
        self.parent = parent
        self.name = name
        self.params = params


class Plotter:
    def __init__(self, setup):
        self.setup = setup

    def define_plot(self, data_labels, title):
        plt.figure()
        for label in data_labels:
            plt.plot(np.random.rand(100), label=label)
        plt.title(title)
        plt.legend()
        plt.grid()

    def plot(self):
        plt.show()


if __name__ == "__main__":
    setup = Setup()
    setup.configure_monitors()
    setup.plot()
