class Setup(SimulationInfrastructure):
    """
    Plotting data of components and showing water balance operations.
    """

    def __init__(self, pt_config_params, t_solver_params):
        tt_monitor_config = {
            "oLogger": {"cParams": [True, 20000]},
            "oTimeStepObserver": {
                "sClass": "simulation.monitors.timestepObserver",
                "cParams": [0],
            },
        }
        super().__init__("MFBED", pt_config_params, t_solver_params, tt_monitor_config)

        # Initialize Example system
        Example(self.o_simulation_container, "Example")

        # Simulation length
        self.f_sim_time = 86400  # in seconds
        self.b_use_time = True

        # Log indexes property
        self.ti_log_indexes = {}

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        o_log = self.to_monitors.o_logger
        o_mt = self.o_simulation_container.o_mt

        # Logging for the WPA system
        o_wpa = self.o_simulation_container.to_children.Example.to_children.WPA

        # Logging basic properties
        o_log.add_value("Example", "fTotalVolumePassedThroughWPA", "m^3", "WPA Total Volume Passed Through")

        self.ti_log_indexes["WPA"] = {
            "Masses": [
                o_log.add_value(
                    "Example:c:WPA.toStores.WasteWater.toPhases.Water",
                    "fMass",
                    "kg",
                    "WPA Waste Water Mass",
                )
            ],
            "Flowrates": [
                o_log.add_value("Example:c:WPA.toBranches.Inlet", "fFlowRate", "kg/s", "WPA Inflow"),
                o_log.add_value("Example:c:WPA.toBranches.Outlet", "fFlowRate", "kg/s", "WPA Outflow"),
                o_log.add_value("Example:c:WPA.toBranches.WasteWater_to_MLS1", "fFlowRate", "kg/s", "WPA Waste Water to Liquid Separator"),
                o_log.add_value("Example:c:WPA.toBranches.Check_to_WasteWater", "fFlowRate", "kg/s", "WPA Reflow of Waste Water"),
            ],
        }

        # Logging airflows
        self.ti_log_indexes["WPA"]["Airflows"] = {
            "Inflows": {
                "O2": o_log.add_value("Example:c:WPA.toBranches.AirInlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.O2)", "kg/s", "WPA Inflow O2"),
                "N2": o_log.add_value("Example:c:WPA.toBranches.AirInlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.N2)", "kg/s", "WPA Inflow N2"),
                "CO2": o_log.add_value("Example:c:WPA.toBranches.AirInlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)", "kg/s", "WPA Inflow CO2"),
                "H2O": o_log.add_value("Example:c:WPA.toBranches.AirInlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.H2O)", "kg/s", "WPA Inflow H2O"),
            },
            "Outflows": {
                "O2": o_log.add_value("Example:c:WPA.toBranches.AirOutlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.O2)", "kg/s", "WPA Outflow O2"),
                "N2": o_log.add_value("Example:c:WPA.toBranches.AirOutlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.N2)", "kg/s", "WPA Outflow N2"),
                "CO2": o_log.add_value("Example:c:WPA.toBranches.AirOutlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)", "kg/s", "WPA Outflow CO2"),
                "H2O": o_log.add_value("Example:c:WPA.toBranches.AirOutlet.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.H2O)", "kg/s", "WPA Outflow H2O"),
            },
        }

        # Logging effective flows
        self.ti_log_indexes["WPA"]["EffectiveFlows"] = {
            "O2": o_log.add_virtual_value('"WPA Outflow O2" + "WPA Inflow O2"', "kg/s", "WPA O2 Output"),
            "N2": o_log.add_virtual_value('"WPA Outflow N2" + "WPA Inflow N2"', "kg/s", "WPA N2 Output"),
            "CO2": o_log.add_virtual_value('"WPA Outflow CO2" + "WPA Inflow CO2"', "kg/s", "WPA CO2 Output"),
            "H2O": o_log.add_virtual_value('"WPA Outflow H2O" + "WPA Inflow H2O"', "kg/s", "WPA H2O Output"),
        }

        # Logging contaminant levels
        self.ti_log_indexes["WPA"]["Outflows"] = {
            "PPM": o_log.add_value("Example:c:WPA.toBranches.Outlet.aoFlowProcs(1)", "this.fPPM", "ppm", "WPA Outflow PPM"),
            "TOC": o_log.add_value("Example:c:WPA.toBranches.Outlet.aoFlowProcs(1)", "this.fTOC", "-", "WPA Outflow TOC"),
        }

    def plot(self):
        """
        Define and generate the plots for the simulation.
        """
        import matplotlib.pyplot as plt

        plt.close("all")
        try:
            self.to_monitors.o_logger.read_data_from_mat()
        except Exception as e:
            print("No data outputted yet:", e)

        o_plotter = super().plot()
        t_plot_options = {"sTimeUnit": "hours"}

        # Define plots
        co_plots = {
            (1, 1): o_plotter.define_plot(self.ti_log_indexes["WPA"]["Masses"], "WPA Water Mass", t_plot_options),
            (1, 2): o_plotter.define_plot(self.ti_log_indexes["WPA"]["Flowrates"], "WPA Flowrates", t_plot_options),
            (2, 1): o_plotter.define_plot(self.ti_log_indexes["WPA"]["EffectiveFlows"], "WPA Gas Flows", t_plot_options),
            (2, 2): o_plotter.define_plot(self.ti_log_indexes["WPA"]["Outflows"], "WPA Contaminant Flows", t_plot_options),
        }

        # Define a figure for these plots
        o_plotter.define_figure(co_plots, "WPA Parameters")
        o_plotter.plot()
