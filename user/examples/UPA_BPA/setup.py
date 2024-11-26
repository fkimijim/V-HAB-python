class Setup(SimulationInfrastructure):
    """
    The setup file for the simulation of the CROP model.
    Includes simulation length and plots for analysis.
    """

    def __init__(self, pt_config_params, t_solver_params):
        super().__init__("UPA_BPA_Example", pt_config_params, t_solver_params, {})

        # Define compound compositions
        tr_base_composition_urine = {"H2O": 0.9644, "CH4N2O": 0.0356}
        self.o_simulation_container.oMT.define_compound_mass("Urine", tr_base_composition_urine)

        tr_base_composition_feces = {"H2O": 0.7576, "DietaryFiber": 0.2424}
        self.o_simulation_container.oMT.define_compound_mass("Feces", tr_base_composition_feces)

        tr_base_composition_brine = {"H2O": 0.8, "C2H6O2N2": 0.2}
        self.o_simulation_container.oMT.define_compound_mass("Brine", tr_base_composition_brine)

        tr_base_composition_concentrated_brine = {"H2O": 0.44, "C2H6O2N2": 0.56}
        self.o_simulation_container.oMT.define_compound_mass("ConcentratedBrine", tr_base_composition_concentrated_brine)

        # Create the CROP system
        Example(self.o_simulation_container, "Example")

        # Simulation length
        self.f_sim_time = 60 * 24 * 3600  # in seconds
        self.i_sim_ticks = 200
        self.b_use_time = True

    def configure_monitors(self):
        o_logger = self.to_monitors.o_logger

        # UPA + BPA Logging
        o_logger.add_value("Example.toChildren.UPA.toBranches.Outlet", "fFlowRate", "kg/s", "UPA Water Flow")
        o_logger.add_value("Example.toChildren.UPA.toBranches.BrineOutlet", "fFlowRate", "kg/s", "UPA Brine Flow")
        o_logger.add_value("Example.toChildren.UPA.toStores.WSTA.toPhases.Urine", "fMass", "kg", "UPA WSTA Mass")
        o_logger.add_value("Example.toChildren.UPA.toStores.ARTFA.toPhases.Brine", "fMass", "kg", "UPA ARTFA Mass")

        o_logger.add_value("Example.toStores.BrineStorage.toPhases.Brine", "fMass", "kg", "Brine Storage Mass")

        o_logger.add_value("Example.oTimer", "fTimeStepFinal", "s", "Timestep")

        o_logger.add_value("Example.toChildren.BPA.toStores.Bladder.toProcsP2P.WaterP2P", "fFlowRate", "kg/s", "BPA Water Flow")
        o_logger.add_value("Example.toChildren.BPA.toStores.Bladder.toPhases.Brine", "fMass", "kg", "BPA Bladder Mass")
        o_logger.add_value("Example.toChildren.BPA.toStores.ConcentratedBrineDisposal.toPhases.ConcentratedBrine", "fMass", "kg", "BPA Concentrated Brine Mass")

        o_logger.add_value("Example.toChildren.UPA", "fPower", "W", "UPA Power Consumption")
        o_logger.add_value("Example.toChildren.BPA", "fPower", "W", "BPA Power Consumption")

        o_logger.add_virtual_value('cumsum("UPA Water Flow" * "Timestep")', "kg", "UPA Produced Water")
        o_logger.add_virtual_value('cumsum("UPA Brine Flow" * "Timestep")', "kg", "UPA Produced Brine")
        o_logger.add_virtual_value('cumsum("BPA Water Flow" * "Timestep")', "kg", "BPA Produced Water")

    def plot(self):
        """
        Define and generate the plots for the simulation.
        """
        try:
            self.to_monitors.o_logger.read_from_mat()
        except Exception:
            print("No data outputted yet.")

        o_plotter = super().plot()

        t_plot_options = {"sTimeUnit": "hours"}
        t_figure_options = {"bTimePlot": False, "bPlotTools": False}
        co_plots = []

        co_plots.append(
            o_plotter.define_plot(
                ['"UPA WSTA Mass"', '"UPA ARTFA Mass"', '"Brine Storage Mass"', '"BPA Bladder Mass"', '"BPA Concentrated Brine Mass"'],
                "Store Masses",
                t_plot_options,
            )
        )
        co_plots.append(
            o_plotter.define_plot(
                ['"UPA Power Consumption"', '"BPA Power Consumption"'],
                "Power",
                t_plot_options,
            )
        )
        co_plots.append(
            o_plotter.define_plot(
                ['"UPA Produced Water"', '"UPA Produced Brine"'],
                "UPA",
                t_plot_options,
            )
        )
        co_plots.append(
            o_plotter.define_plot(
                ['"BPA Produced Water"'],
                "BPA",
                t_plot_options,
            )
        )

        o_plotter.define_figure(co_plots, "UPA + BPA", t_figure_options)
        o_plotter.plot()
