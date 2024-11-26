import numpy as np
import matplotlib.pyplot as plt

class SimulationSetup:
    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig, fSimTime=None):
        """
        Initializes the simulation setup.
        """
        self.simulation_name = 'Example_DetailedHumanModel'
        self.config_params = ptConfigParams
        self.solver_params = tSolverParams
        self.monitor_config = ttMonitorConfig
        self.fSimTime = fSimTime if fSimTime is not None else 3600 * 24

        # Define the base composition of substances
        self.trBaseCompositionUrine = {'H2O': 0.9644, 'CH4N2O': 0.0356}
        self.trBaseCompositionFeces = {'H2O': 0.7576, 'DietaryFiber': 0.2424}
        self.logger = Logger()

    def configure_monitors(self):
        """
        Configures the logging of simulation values.
        """
        logger = self.logger

        # Example of setting up store values
        stores = ['FecesStorage', 'UrineStorage']
        for store in stores:
            logger.add_value(f'Example.toStores.{store}.toPhases.{store[:-7]}', 'fMass', 'kg', f'{store} Mass')
            logger.add_value(f'Example.toStores.{store}.toPhases.{store[:-7]}', 'fPressure', 'Pa', f'{store} Pressure')
            logger.add_value(f'Example.toStores.{store}.toPhases.{store[:-7]}', 'fTemperature', 'K', f'{store} Temperature')

        # Example of setting up branches
        branches = ['Potable_Water_In', 'RespirationWaterOutput', 'PerspirationWaterOutput', 'Urine_Out']
        for branch in branches:
            logger.add_value(f'Example:c:Human_1.toBranches.{branch}', 'fFlowRate', 'kg/s', f'{branch} Flowrate')

        # Set up detailed respiration logging
        respiration_values = [
            ('Volumetric Blood Flow Brain', 'fVolumetricFlow_BrainBlood'),
            ('Volumetric Blood Flow Tissue', 'fVolumetricFlow_TissueBlood'),
            ('Volumetric Air Flow', 'fVolumetricFlow_Air')
        ]
        for label, field in respiration_values:
            logger.add_value('Example:c:Human_1:c:Respiration', field, 'm^3/s', label)

    def plot(self):
        """
        Plots the results of the simulation.
        """
        logger = self.logger
        time = logger.get_time() / 3600  # Convert time to hours

        # Example of plotting water flows
        water_flows = ['Ingested Water Flow Rate', 'Respiration Water Flow Rate', 
                       'Perspiration Water Flow Rate', 'Urine Flow Rate']
        data = [logger.get_log(f'Example:c:Human_1.toBranches.{flow}') for flow in water_flows]

        plt.figure()
        for i, series in enumerate(data):
            plt.plot(time, series, label=water_flows[i])
        plt.xlabel('Time (hours)')
        plt.ylabel('Flow Rate (kg/s)')
        plt.legend()
        plt.title('Water Flows')
        plt.grid()
        plt.show()


class Logger:
    """
    Mimics a logger for recording and managing simulation values.
    """
    def __init__(self):
        self.values = {}
        self.time = np.linspace(0, 3600 * 24, 100)  # Simulated time array

    def add_value(self, path, attribute, unit, label):
        self.values[label] = np.random.rand(len(self.time))  # Placeholder for simulation data

    def get_time(self):
        return self.time

    def get_log(self, label):
        return self.values.get(label, np.zeros_like(self.time))


# Example of usage
ptConfigParams = {}
tSolverParams = {}
ttMonitorConfig = {}
fSimTime = 3600 * 24

simulation = SimulationSetup(ptConfigParams, tSolverParams, ttMonitorConfig, fSimTime)
simulation.configure_monitors()
simulation.plot()
