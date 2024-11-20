import os

class ExecutionControl:
    """
    ExecutionControl monitor for managing simulation execution.
    Allows pausing the simulation by creating STOP files in the working directory.
    Supports both general STOP files and simulation-specific STOP files.
    """

    def __init__(self, simulation_infrastructure, tick_interval=100):
        """
        Initialize the ExecutionControl instance.

        Args:
            simulation_infrastructure (object): Reference to the simulation infrastructure.
            tick_interval (int): Interval in ticks to check for STOP files.
        """
        self.simulation_infrastructure = simulation_infrastructure
        self.tick_interval = tick_interval
        self.paused = False

        # Bind to simulation events
        simulation_infrastructure.bind("step_post", self.on_step_post)
        simulation_infrastructure.bind("init_post", self.on_init_post)

    def on_step_post(self):
        """
        Checks for STOP files at defined intervals and pauses the simulation if necessary.
        """
        timer = self.simulation_infrastructure.timer
        sim_name = self.simulation_infrastructure.name
        sim_uuid = self.simulation_infrastructure.uuid

        # Check if we are at the interval to perform the check
        if timer.current_tick % self.tick_interval == 0:
            # Check for general STOP file
            general_stop_file = os.path.join(os.getcwd(), "STOP")
            specific_stop_file = os.path.join(os.getcwd(), f"STOP_{sim_uuid}.txt")

            pause_general = os.path.isfile(general_stop_file)
            pause_specific = os.path.isfile(specific_stop_file)

            # If a specific STOP file exists, rename it for quick resumption
            if pause_specific:
                os.rename(specific_stop_file, f"{specific_stop_file}_OFF")

            # Pause simulation if either STOP file is present
            if pause_general or pause_specific:
                if timer.current_tick == 0:
                    raise RuntimeError(
                        f"STOP file found before the simulation started. "
                        f"Please remove the STOP file and restart the simulation."
                    )
                else:
                    print(f"[ExecControl] Simulation '{sim_name}' paused by STOP file.")
                    self.simulation_infrastructure.pause()
                    self.paused = True
            else:
                self.paused = False

    def on_init_post(self):
        """
        Outputs a message after the simulation initialization to inform the user about STOP files.
        """
        sim_name = self.simulation_infrastructure.name
        sim_uuid = self.simulation_infrastructure.uuid
        print(
            f"[ExecControl] You can pause the simulation '{sim_name}' "
            f"by creating a file called 'STOP' or 'STOP_{sim_uuid}.txt' in the working directory. "
            f"This will be checked every {self.tick_interval} ticks."
        )
