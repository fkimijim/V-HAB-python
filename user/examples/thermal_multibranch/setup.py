import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

class Setup:
    def __init__(self, pt_config_params, t_solver_params, f_sim_time=None):
        # Simulation name
        self.simulation_name = "Tutorial_Thermal_Multibranch"
        self.pt_config_params = pt_config_params
        self.t_solver_params = t_solver_params
        self.f_sim_time = f_sim_time if f_sim_time is not None else 1800  # Default to 1800 seconds
        self.i_sim_ticks = 1500
        self.b_use_time = True
        self.ti_log_indexes = {}
        self.o_simulation_container = None  # Placeholder for simulation container
        self.example_system = Example(self.o_simulation_container, "Example")
        self.logger = Logger()

    def configure_monitors(self):
        """Configure logging of the simulation."""
        i_nodes_per_direction = self.example_system.i_nodes_per_direction
        for i_x in range(1, i_nodes_per_direction + 1):
            for i_y in range(1, i_nodes_per_direction + 1):
                for i_z in range(1, i_nodes_per_direction + 1):
                    node_name = f"Node_X{i_x}_Y{i_y}_Z{i_z}"
                    self.logger.add_value(
                        f"Example:s:Cube.toPhases.{node_name}",
                        "fTemperature",
                        "K",
                        f"Temperature {node_name}"
                    )

    def plot(self):
        """Plot the results of the simulation."""
        plt.close('all')

        i_nodes_per_direction = self.example_system.i_nodes_per_direction
        logged_temperatures = self.logger.get_logged_data(i_nodes_per_direction)

        # Final temperature data for visualization
        final_temperatures = logged_temperatures[:, :, :, -1]
        x, y, z = np.meshgrid(
            np.arange(1, i_nodes_per_direction + 1),
            np.arange(1, i_nodes_per_direction + 1),
            np.arange(1, i_nodes_per_direction + 1)
        )
        xq, yq, zq = np.meshgrid(
            np.arange(1, i_nodes_per_direction + 0.5, 0.5),
            np.arange(1, i_nodes_per_direction + 0.5, 0.5),
            np.arange(1, i_nodes_per_direction + 0.5, 0.5)
        )

        interpolator = RegularGridInterpolator(
            (np.arange(1, i_nodes_per_direction + 1),
             np.arange(1, i_nodes_per_direction + 1),
             np.arange(1, i_nodes_per_direction + 1)),
            final_temperatures
        )
        interpolated_temperatures = interpolator((xq.flatten(), yq.flatten(), zq.flatten())).reshape(xq.shape)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        slice_x = [1, i_nodes_per_direction // 2, i_nodes_per_direction]
        slice_y = [i_nodes_per_direction]
        slice_z = [i_nodes_per_direction // 2]

        ax.contourf(xq, yq, zq, interpolated_temperatures, cmap="viridis")
        ax.set_title("Temperature Distribution")
        plt.colorbar(ax.collections[0], ax=ax, orientation='vertical')
        plt.show()

        # Animation loop
        time_points = np.arange(0, self.logger.af_time[-1], 10)
        for time_point in time_points:
            time_idx = (np.abs(self.logger.af_time - time_point)).argmin()
            current_temperatures = logged_temperatures[:, :, :, time_idx]
            interpolated_temperatures = interpolator((xq.flatten(), yq.flatten(), zq.flatten())).reshape(xq.shape)

            fig.clear()
            ax = fig.add_subplot(111, projection='3d')
            ax.contourf(xq, yq, zq, interpolated_temperatures, cmap="viridis")
            ax.set_title(f"Time: {time_point:.1f} seconds")
            plt.pause(0.5)

        plt.close()
