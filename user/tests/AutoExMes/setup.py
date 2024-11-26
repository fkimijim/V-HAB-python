class Setup:
    """
    Setup class for simulation.
    This class is used to setup a simulation, instantiate the root object,
    set the simulation duration, determine which items are logged, and provide
    methods for plotting the results.
    """

    def __init__(self, ptConfigParams=None, tSolverParams=None, ttMonitorConfig=None, fSimTime=3600):
        """
        Constructor function.
        """
        self.simulation_name = "Test_Automatic_ExMes"
        self.ptConfigParams = ptConfigParams
        self.tSolverParams = tSolverParams
        self.ttMonitorConfig = ttMonitorConfig
        self.fSimTime = fSimTime  # Simulation length in seconds
        self.bUseTime = True
        self.tiLogIndexes = {}

        # Create the 'Example' system
        self.oSimulationContainer = {}
        self.create_example_system()

    def create_example_system(self):
        """
        Create the 'Example' system as a child of the root system.
        """
        self.oSimulationContainer["Example"] = ExampleSystem("Example")

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        oLog = Logger()

        # Add log values
        oLog.add_value("Example:s:Tank_1.aoPhases(1)", "afPP(this.oMT.tiN2I.CO2)", "Pa", "Partial Pressure CO2 Tank 1", "ppCO2_Tank1")
        oLog.add_value("Example:s:Tank_2.aoPhases(1)", "afPP(this.oMT.tiN2I.CO2)", "Pa", "Partial Pressure CO2 Tank 2", "ppCO2_Tank2")

        # Example of calculated log value
        oLog.add_value(
            "Example.aoBranches(1).aoFlows(1)",
            "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)",
            "kg/s",
            "Flowrate of CO2",
            "fr_co2",
        )

        oLog.add_value("Example:s:Tank_1.aoPhases(1)", "afMass(this.oMT.tiN2I.CO2)", "kg")
        oLog.add_value("Example:s:Tank_2.aoPhases(1)", "afMass(this.oMT.tiN2I.CO2)", "kg", "Partial Mass CO2 Tank 2")
        oLog.add_value("Example:s:Tank_1.aoPhases(1)", "fTemperature", "K", "Temperature Phase 1")
        oLog.add_value("Example:s:Tank_2.aoPhases(1)", "fTemperature", "K", "Temperature Phase 2")
        oLog.add_value("Example:s:Tank_1.aoPhases(1)", "this.fMass * this.fMassToPressure", "Pa", "Pressure Phase 1")
        oLog.add_value("Example:s:Tank_2.aoPhases(1)", "this.fMass * this.fMassToPressure", "Pa", "Pressure Phase 2")
        oLog.add_value("Example.toBranches.Branch", "fFlowRate", "kg/s", "Branch Flow Rate", "branch_FR")

        # Add virtual log values
        self.tiLogIndexes["iTempIdx1"] = oLog.add_value(
            "Example.toProcsF2F.Pipe.aoFlows(1)", "fTemperature", "K", "Flow Temperature - Left", "flow_temp_left"
        )
        self.tiLogIndexes["iTempIdx2"] = oLog.add_value(
            "Example.toProcsF2F.Pipe.aoFlows(2)", "fTemperature", "K", "Flow Temperature - Right", "flow_temp_right"
        )
        self.tiLogIndexes["iIndex_1"] = oLog.add_virtual_value("fr_co2 * 1000", "g/s", "CO2 Flowrate", "co2_fr_grams")
        self.tiLogIndexes["iIndex_2"] = oLog.add_virtual_value(
            "flow_temp_left - 273.15", "degC", "Temperature Left in Celsius"
        )
        self.tiLogIndexes["iIndex_3"] = oLog.add_virtual_value(
            'mod(flow_temp_right ** 2, 10) / "Partial Mass CO2 Tank 2"', "-", "Nonsense"
        )

    def plot(self):
        """
        Plot the simulation results.
        """
        oPlotter = Plotter()

        # Define plot options
        tPlotOptions = {"sTimeUnit": "hours"}
        coPlots = []
        coPlots.append(
            oPlotter.define_plot(
                ['"Temperature Phase 1"', '"Temperature Phase 2"'], "Temperatures", tPlotOptions
            )
        )
        coPlots.append(oPlotter.define_plot(['"Pressure Phase 1"', '"Pressure Phase 2"'], "Pressure", tPlotOptions))
        coPlots.append(oPlotter.define_plot(['"Branch Flow Rate"'], "Flowrate", tPlotOptions))

        oPlotter.define_figure(coPlots, "Tank Temperatures", {"bTimePlot": True})
        oPlotter.plot()


class ExampleSystem:
    """
    Example system for the simulation.
    """

    def __init__(self, name):
        self.name = name


class Logger:
    """
    Logger class for handling simulation logs.
    """

    def __init__(self):
        self.logs = []

    def add_value(self, path, value, unit, label, legend=None):
        self.logs.append({"path": path, "value": value, "unit": unit, "label": label, "legend": legend})
        return len(self.logs)

    def add_virtual_value(self, expression, unit, label, legend=None):
        self.logs.append({"expression": expression, "unit": unit, "label": label, "legend": legend})
        return len(self.logs)


class Plotter:
    """
    Plotter class for handling simulation plots.
    """

    def __init__(self):
        self.figures = []

    def define_plot(self, data, title, options):
        return {"data": data, "title": title, "options": options}

    def define_figure(self, plots, title, options):
        self.figures.append({"plots": plots, "title": title, "options": options})

    def plot(self):
        for figure in self.figures:
            print(f"Plotting figure: {figure['title']}")
