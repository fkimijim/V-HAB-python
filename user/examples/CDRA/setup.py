import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

class CDRASetup:
    def __init__(self, ptConfigParams=None, tSolverParams=None):
        self.simulation_name = "Example_CDRA"
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.simulation_time = 3600 * 50  # in seconds
        self.use_time = True
        self.example_system = ExampleSystem()

    def configure_monitors(self):
        self.logger = Logger()

        self.logger.add_value("Example:s:Cabin.toPhases.CabinAir", "rRelHumidity", "-", "Relative Humidity Cabin")
        self.logger.add_value("Example:s:Cabin.toPhases.CabinAir", "afPP.CO2", "Pa", "Partial Pressure CO2")
        self.logger.add_value("Example:s:Cabin.toPhases.CabinAir", "fTemperature", "K", "Temperature Atmosphere")

        # Add various monitoring logs for CDRA, TCCV, and other subsystems
        # Similar to the MATLAB `addValue` calls

    def plot_results(self):
        try:
            self.logger.read_from_mat()
        except Exception as e:
            print("No data outputted yet.")
            return

        time_unit = "hours"

        # Define and calculate CO2 outlet flow for convergence metrics
        co2_outlet_flow = self.logger.get_virtual_value("CDRA CO2 OutletFlow")
        if co2_outlet_flow is None:
            print("CDRA CO2 OutletFlow not found in logger.")
            return
        co2_outlet_flow = np.nan_to_num(co2_outlet_flow[:-1])  # Remove last NaN entry

        time_steps = self.logger.get_time_steps()
        averaged_co2_outlet = np.sum(co2_outlet_flow * time_steps[:len(co2_outlet_flow)]) / np.sum(time_steps)

        print("\nAveraged CO2 Outlet Flow:", averaged_co2_outlet, "\n")

        # Example of plotting configurations for pressure
        pressure_variables = [
            "Flow Pressure Sylobead_1",
            "Flow Pressure Zeolite13x_1",
            "Flow Pressure Zeolite5A_1",
        ]
        self.plot_pressure(pressure_variables, time_unit)

        # Plot overlay with test data
        self.plot_test_data()

    def plot_pressure(self, pressure_variables, time_unit):
        plt.figure("Pressure")
        for var in pressure_variables:
            data = self.logger.get_value(var)
            if data is not None:
                plt.plot(self.logger.time / 3600, data, label=var)
        plt.xlabel(f"Time ({time_unit})")
        plt.ylabel("Pressure (Pa)")
        plt.legend()
        plt.show()

    def plot_test_data(self):
        test_data = np.loadtxt("CDRA_Test_Data.csv", delimiter=",")
        test_data[:, 0] -= 30.7
        test_data = test_data[test_data[:, 0] >= 0]

        plt.figure("Test Data vs Simulation")
        plt.plot(test_data[:, 0], test_data[:, 1], label="Test Data")

        co2_partial_pressure = self.logger.get_virtual_value("Partial Pressure CO2 Torr")
        if co2_partial_pressure is not None:
            co2_partial_pressure = np.nan_to_num(co2_partial_pressure)
            time_hours = self.logger.time / 3600
            plt.plot(time_hours[:len(co2_partial_pressure)], co2_partial_pressure, label="Simulation")
        plt.xlabel("Time (h)")
        plt.ylabel("Partial Pressure CO2 (Torr)")
        plt.legend()
        plt.grid()
        plt.show()

        # Interpolate test data
        time_unique, indices = np.unique(test_data[:, 0], return_index=True)
        co2_data_unique = test_data[indices, 1]
        interp_function = interp1d(time_unique, co2_data_unique, fill_value="extrapolate")
        interpolated_test_data = interp_function(self.logger.time / 3600)

        # Calculate differences
        co2_partial_pressure = co2_partial_pressure[:len(interpolated_test_data)]
        interpolated_test_data = interpolated_test_data[:len(co2_partial_pressure)]
        differences = co2_partial_pressure - interpolated_test_data
        max_diff = np.max(np.abs(differences))
        min_diff = np.min(np.abs(differences))
        mean_diff = np.mean(differences)
        percent_error = 100 * mean_diff / np.mean(interpolated_test_data)
        mse = np.mean(differences ** 2)

        print(f"Max Difference: {max_diff} Torr")
        print(f"Min Difference: {min_diff} Torr")
        print(f"Mean Difference: {mean_diff} Torr")
        print(f"Percent Error: {percent_error}%")
        print(f"MSE: {mse} Torr")


class Logger:
    def __init__(self):
        self.time = np.linspace(0, 3600 * 50, 1000)
        self.data = {}

    def add_value(self, source, variable, unit, label):
        self.data[label] = np.random.random(len(self.time))  # Placeholder for actual data

    def add_virtual_value(self, formula, unit, label):
        # Process and store virtual values based on the formula
        pass

    def get_value(self, label):
        return self.data.get(label)

    def get_virtual_value(self, label):
        # Return calculated virtual values
        return self.data.get(label)

    def read_from_mat(self):
        # Placeholder for reading from MAT files
        pass

    def get_time_steps(self):
        return np.diff(self.time, prepend=self.time[0])


class ExampleSystem:
    def __init__(self):
        # Initialize the example system
        pass


# Example usage:
if __name__ == "__main__":
    setup = CDRASetup()
    setup.configure_monitors()
    setup.plot_results()
