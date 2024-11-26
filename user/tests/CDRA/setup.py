import numpy as np
import matplotlib.pyplot as plt
import csv

class Setup:
    """
    SETUP class for initializing and configuring a simulation.
    
    Responsibilities:
    - Instantiate the root object.
    - Register branches to appropriate solvers.
    - Configure logging.
    - Set the simulation duration.
    - Provide methods for plotting results.
    """
    
    def __init__(self, config_params, solver_params, monitor_config, sim_time=20000):
        """
        Constructor for Setup class.

        Args:
            config_params (dict): Configuration parameters.
            solver_params (dict): Solver parameters.
            monitor_config (dict): Monitor configuration.
            sim_time (float): Simulation time in seconds (default is 20000).
        """
        monitor_config['oTimeStepObserver'] = {
            'sClass': 'simulation.monitors.timestepObserver',
            'cParams': [0]
        }
        self.simulation_name = "Test_CDRA"
        self.config_params = config_params
        self.solver_params = solver_params
        self.monitor_config = monitor_config
        self.sim_time = sim_time

        # Create root simulation container
        self.simulation_container = SimulationContainer(self.simulation_name)
        self.example_system = Example(self.simulation_container, "Example")

    def configure_monitors(self):
        """
        Configures the logger for the simulation.
        """
        logger = Logger()

        # General logging
        logger.add_value("Example:s:Cabin.toPhases.CabinAir", "rRelHumidity", "-", "Relative Humidity Cabin")
        logger.add_value("Example:s:Cabin.toPhases.CabinAir", "afPP(this.oMT.tiN2I.CO2)", "Pa", "Partial Pressure CO2")
        logger.add_value("Example:s:Cabin.toPhases.CabinAir", "fTemperature", "K", "Temperature Atmosphere")

        # CDRA-related logging
        for i_type, cs_type in enumerate(["Sylobead_", "Zeolite13x_", "Zeolite5A_"]):
            for i_bed in range(1, 3):
                for i_cell in range(1, 11):  # Adjust the range based on miCellNumber
                    logger.add_value(
                        f"Example:c:CDRA:s:{cs_type}{i_bed}.toPhases.Absorber_{i_cell}",
                        "afMass(this.oMT.tiN2I.CO2)",
                        "kg",
                        f"Partial Mass CO2 {cs_type}{i_bed} Cell {i_cell}"
                    )
                    logger.add_value(
                        f"Example:c:CDRA:s:{cs_type}{i_bed}.toPhases.Absorber_{i_cell}",
                        "afMass(this.oMT.tiN2I.H2O)",
                        "kg",
                        f"Partial Mass H2O {cs_type}{i_bed} Cell {i_cell}"
                    )
        self.logger = logger

    def plot(self):
        """
        Plots simulation results.
        """
        try:
            self.logger.read_from_mat()
        except FileNotFoundError:
            print("No data outputted yet")
            return
        
        plotter = Plotter(self.simulation_name)

        # Example CO2 and H2O adsorption plots
        cs_type = ["Sylobead_", "Zeolite13x_", "Zeolite5A_"]
        total_mass_co2 = [[f'"Total Mass CO2 {cs}{i}"' for i in range(1, 3)] for cs in cs_type]
        total_mass_h2o = [[f'"Total Mass H2O {cs}{i}"' for i in range(1, 3)] for cs in cs_type]

        for i, cs in enumerate(cs_type):
            for j in range(2):
                plotter.define_plot(
                    total_mass_co2[i][j], f"{cs} {j+1} Adsorbed CO2 Mass"
                )
                plotter.define_plot(
                    total_mass_h2o[i][j], f"{cs} {j+1} Adsorbed H2O Mass"
                )

        # Plot test data comparison
        with open('+examples/+CDRA/+TestData/CDRA_Test_Data.csv', newline='') as csvfile:
            test_data = list(csv.reader(csvfile))

        # Process test data
        test_data = np.array(test_data, dtype=float)
        test_data[:, 0] -= 30.7  # Shift time
        test_data = test_data[test_data[:, 0] >= 0]

        time, partial_pressure_co2 = test_data[:, 0], test_data[:, 1]
        plt.plot(time, partial_pressure_co2, label='Test Data')

        sim_time, sim_partial_pressure_co2 = self.logger.get_simulated_partial_pressure_co2()
        plt.plot(sim_time, sim_partial_pressure_co2, label='Simulation')

        plt.xlabel("Time (hours)")
        plt.ylabel("Partial Pressure CO2 (Torr)")
        plt.legend()
        plt.show()


# Supporting classes for simulation
class SimulationContainer:
    def __init__(self, name):
        self.name = name


class Logger:
    def __init__(self):
        self.values = []

    def add_value(self, path, attribute, unit, label):
        self.values.append((path, attribute, unit, label))

    def read_from_mat(self):
        print("Reading from MAT file...")

    def get_simulated_partial_pressure_co2(self):
        # Placeholder for simulation data retrieval
        return np.linspace(0, 10, 100), np.random.rand(100)


class Plotter:
    def __init__(self, simulation_name):
        self.simulation_name = simulation_name

    def define_plot(self, data, title):
        print(f"Defining plot: {title}")
