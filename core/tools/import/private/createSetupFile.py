import os
import create_hierarchy

def create_setup_file(tVHAB_Objects, sPath, sSystemLabel, sRootName, csPhases, csF2F, oMT, tSystemIDtoLabel):
    """
    Create a setup file for the simulation infrastructure.

    Args:
        tVHAB_Objects (dict): The V-HAB objects.
        sPath (str): The file path where the setup file will be created.
        sSystemLabel (str): The system label.
        sRootName (str): The root name of the system.
        csPhases (list): List of phase types.
        csF2F (list): List of F2F types.
        oMT (object): Material properties object.
        tSystemIDtoLabel (dict): Mapping of system IDs to their labels.
    """
    setup_file_path = os.path.join(sPath, "setup.py")

    with open(setup_file_path, "w") as f:
        # Write class and properties
        f.write("\nclass Setup:\n")
        f.write("    def __init__(self, ptConfigParams, tSolverParams):\n")
        f.write("        # Creating the monitors struct\n")
        f.write("        self.ttMonitorConfig = {}\n\n")

        # Add monitor configurations
        setup = tVHAB_Objects["Setup"][0]
        if "DumpLogFiles" in setup:
            f.write(f"        self.ttMonitorConfig['oLogger'] = {{'cParams': [{setup['DumpLogFiles']}]}}\n\n")
        if "TimeStepObserver" in setup and setup["TimeStepObserver"] == "true":
            f.write("        self.ttMonitorConfig['oTimeStepObserver'] = {\n")
            f.write("            'sClass': 'simulation.monitors.timestepObserver',\n")
            f.write("            'cParams': [0]\n")
            f.write("        }\n\n")
        if "MassBalanceObserver" in setup and setup["MassBalanceObserver"] == "true":
            f.write("        self.ttMonitorConfig['oMassBalanceObserver'] = {\n")
            f.write("            'sClass': 'simulation.monitors.massbalanceObserver',\n")
            f.write("            'cParams': [1e-8, float('inf'), False]\n")
            f.write("        }\n\n")

        # Initialize simulation infrastructure
        f.write(f"        self.simulation = SimulationInfrastructure('{sRootName}', ptConfigParams, tSolverParams, self.ttMonitorConfig)\n\n")

        # Define compound masses
        f.write("        # Defining compound masses for the simulation\n")
        compounds = {
            "Urine": {"H2O": 0.9644, "CH4N2O": 0.0356},
            "Feces": {"H2O": 0.7576, "DietaryFiber": 0.2424},
            "Brine": {"H2O": 0.8, "C2H6O2N2": 0.2},
            "ConcentratedBrine": {"H2O": 0.44, "C2H6O2N2": 0.56}
        }
        for compound, composition in compounds.items():
            f.write(f"        self.simulation.oMT.define_compound_mass('{compound}', {composition})\n")
        f.write("\n")

        # Create the root object
        f.write("        # Creating the root object\n")
        f.write(f"        DrawIoImport.{sSystemLabel}.systems.{sRootName}(self.simulation.oSimulationContainer, '{sRootName}')\n\n")

        # Set simulation time
        f.write(f"        self.simulation.fSimTime = {setup['fSimTime']}\n")
        f.write("        self.simulation.bUseTime = True\n\n")

        # Add configuration method for monitors
        f.write("    def configure_monitors(self):\n")
        f.write("        oLogger = self.simulation.toMonitors['oLogger']\n\n")

        # Generate hierarchy
        tVHAB_Objects, _ = create_hierarchy(tVHAB_Objects, tSystemIDtoLabel)

        for i, system in enumerate(tVHAB_Objects["System"]):
            sSystemPath = f"self.simulation.{system['sFullPath']}.oTimer"
            f.write(f"        oLogger.add_value('{sSystemPath}', 'fTimeStepFinal', 's', 'Timestep')\n")

            # Log specific values
            for log_value in system.get("csToLog", []):
                sLogPath = f"{sSystemPath}.toStores.{log_value}"
                f.write(f"        oLogger.add_value('{sLogPath}', '{log_value}', '-', '{log_value}')\n")

        # Add plot function
        f.write("\n    def plot(self):\n")
        f.write("        oPlotter = self.simulation.create_plotter()\n\n")

        for system in tVHAB_Objects["System"]:
            for plot_item in system.get("csToPlot", []):
                f.write(f"        oPlotter.define_plot('{plot_item}', '{plot_item}')\n")

        f.write("        oPlotter.plot()\n")

    print(f"Setup file created at: {setup_file_path}")
