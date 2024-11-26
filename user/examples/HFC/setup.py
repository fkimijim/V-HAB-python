import numpy as np
import matplotlib.pyplot as plt

class Setup:
    """
    This class is used to set up a simulation.
    It includes:
    - Instantiating the root object
    - Determining which items are logged
    - Setting the simulation duration
    - Providing methods for plotting the results
    """
    def __init__(self, ptConfigParams, tSolverParams):
        # Simulation setup
        self.sim_name = "HFC_System"
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.ttMonitorConfig = {
            'oLogger': {'cParams': [True, 10000]},
            'oTimeStepObserver': {
                'sClass': 'simulation.monitors.timestepObserver',
                'cParams': [0]
            }
        }

        # Load experimental data
        afUpTime, afUpCO2 = self.import_CO2_file(
            "+examples/+HFC/+data/April-04-2017-upstrm2.csv", 3, 1220
        )
        afDnTime, afDnCO2 = self.import_CO2_file(
            "+examples/+HFC/+data/April-04-2017-dwnstrm2.csv", 3, 1217
        )

        # Remove pre-test setup data points
        afUpTime = afUpTime[106:]
        afDnTime = afDnTime[102:]

        self.dStartTime = np.min([np.min(afDnTime), np.min(afUpTime)])
        self.dEndTime = np.max([np.max(afDnTime), np.max(afUpTime)])
        self.fSimTime = (self.dEndTime - self.dStartTime).total_seconds()
        self.bUseTime = True

    def import_CO2_file(self, filename, start_row, end_row):
        """
        Import CO2 data from a CSV file.
        """
        data = np.genfromtxt(filename, delimiter=",", skip_header=start_row, max_rows=end_row - start_row)
        Time = data[:, 0]  # Assuming the first column is time
        CO2 = data[:, 1]   # Assuming the second column is CO2
        return Time, CO2

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        self.logger_config = [
            {"path": "Example.toStores.Aether.toPhases.Air", "property": "afPP(this.oMT.tiN2I.CO2)", "unit": "Pa", "label": "Partial Pressure CO2 IN"},
            {"path": "Example.toStores.Exhaust.toPhases.Air", "property": "afPP(this.oMT.tiN2I.CO2)", "unit": "Pa", "label": "Partial Pressure CO2 OUT"}
        ]
        # Additional logging setup can be added here

    def plot(self):
        """
        Plotting function for the simulation results.
        """
        # Example: Create dummy data for plotting
        time = np.linspace(0, self.fSimTime, 100)  # Simulated time
        partial_pressure_in = np.random.rand(100) * 100
        partial_pressure_out = np.random.rand(100) * 100

        plt.figure(figsize=(10, 6))
        plt.plot(time, partial_pressure_in, label="Partial Pressure CO2 IN")
        plt.plot(time, partial_pressure_out, label="Partial Pressure CO2 OUT")
        plt.title("Partial Pressures CO2")
        plt.xlabel("Time [s]")
        plt.ylabel("Partial Pressure [Pa]")
        plt.legend()
        plt.grid()
        plt.show()
