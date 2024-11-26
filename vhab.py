class Vhab:
    """
    V-HAB Launch Class

    This class provides static methods to initialize the Python environment
    and methods to construct and run V-HAB simulations.
    """

    @staticmethod
    def init():
        """
        Initialize the environment for V-HAB.
        """
        print('+-----------------------------------------------------------------------------------+')
        print('+------------------------------ V-HAB INITIALIZATION -------------------------------+')
        print('+-----------------------------------------------------------------------------------+')

        # Add necessary paths (adjust paths based on Python project structure)
        import sys
        import os
        current_dir = os.getcwd().replace('\\', '/')
        sys.path.append(f"{current_dir}/lib")
        sys.path.append(f"{current_dir}/core")
        sys.path.append(f"{current_dir}/user")

        # Check if 'old' folder exists and add to the path
        if os.path.isdir(f"{current_dir}/old"):
            sys.path.append(f"{current_dir}/old")

    @staticmethod
    def sim(simulation_class, *args, **kwargs):
        """
        Create a simulation object.

        :param simulation_class: String path to the simulation class, e.g., 'tutorials.simple_flow.setup'.
        :param args: Positional arguments for the simulation constructor.
        :param kwargs: Keyword arguments for the simulation constructor.
        :return: An instance of the simulation object.
        """
        # Initialize the environment
        Vhab.init()

        # Dynamically import and construct the simulation class
        module_name, class_name = simulation_class.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        sim_class = getattr(module, class_name)

        # Create the simulation instance
        sim_instance = sim_class(*args, **kwargs)

        # Call the initialize method
        sim_instance.initialize()
        return sim_instance

    @staticmethod
    def clear(preserve_breakpoints=False):
        """
        Clear variables, classes, and objects from previous runs.

        :param preserve_breakpoints: If True, preserves debug breakpoints (not applicable in Python).
        """
        print("Clearing Python environment...")

        import gc
        import time
        start_time = time.time()

        # Explicit garbage collection
        gc.collect()

        # Notify the user
        print(f"Environment cleared in {time.time() - start_time:.2f} seconds!")

    @staticmethod
    def exec(simulation_class, config_params=None, solver_params=None, *args, **kwargs):
        """
        Run a V-HAB simulation.

        :param simulation_class: String path to the simulation class.
        :param config_params: Configuration parameters (default: empty dictionary).
        :param solver_params: Solver parameters (default: empty dictionary).
        :param args: Additional positional arguments for the simulation class.
        :param kwargs: Additional keyword arguments for the simulation class.
        :return: The simulation object after running the simulation.
        """
        # Clear the environment
        Vhab.clear()

        # Set default parameters if not provided
        config_params = config_params or {}
        solver_params = solver_params or {}

        # Create the simulation object
        sim_instance = Vhab.sim(simulation_class, config_params, solver_params, *args, **kwargs)

        # Assign the simulation instance for debugging (if applicable)
        globals()["last_sim_instance"] = sim_instance

        # Run the simulation
        sim_instance.run()

        return sim_instance
