class Setup(simulation.infrastructure):
    """
    Setup class for the Example V-HAB system with Bosch Reactor.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        # Initialize the base class with the system name and parameters
        ttMonitorConfig = {}
        super().__init__('Example', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Creating the root object
        examples.Bosch.systems.Example(self.oSimulationContainer, 'Example')

    def configure_monitors(self):
        oLog = self.toMonitors.oLogger

        # Adding monitor values for RWGS
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance', 
                       'fMolarFluxInCO2', 'mol/s', 'RWGS Molar Inflow CO2')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance', 
                       'fMolarFluxOutCO', 'mol/s', 'RWGS Molar Outflow CO2')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance', 
                       'fConversionCO2', '-', 'RWGS CO2 Conversion Ratio')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance', 
                       'fReactionRate', '-', 'RWGS CO2 Reaction Rate')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance', 
                       'fVelocityConstant', '-', 'RWGS Velocity Constant')

        # Adding flow monitoring for RWGS
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.H2)', 'kg/s', 'RWGS Manip H2 Flow')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.CO2)', 'kg/s', 'RWGS Manip CO2 Flow')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.H2O)', 'kg/s', 'RWGS Manip H2O Flow')
        oLog.add_value('Example:c:BoschReactor:s:RWGSr.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.CO)', 'kg/s', 'RWGS Manip CO Flow')

        # Adding monitors for CFR flows
        oLog.add_value('Example:c:BoschReactor:s:CFR.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.H2)', 'kg/s', 'Carbon Formation Manip H2 Flow')
        oLog.add_value('Example:c:BoschReactor:s:CFR.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.CO2)', 'kg/s', 'Carbon Formation Manip CO2 Flow')
        oLog.add_value('Example:c:BoschReactor:s:CFR.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.CO)', 'kg/s', 'Carbon Formation Manip CO Flow')
        oLog.add_value('Example:c:BoschReactor:s:CFR.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.H2O)', 'kg/s', 'Carbon Formation Manip H2O Flow')
        oLog.add_value('Example:c:BoschReactor:s:CFR.toPhases.CO2_H2_CO_H2O.toManips.substance',
                       'this.afPartialFlows(this.oMT.tiN2I.C)', 'kg/s', 'Carbon Formation Manip C Flow')

        # Adding system pressure monitors
        oLog.add_value('Example:s:TankH2.aoPhases(1, 1)', 'fPressure', 'Pa', 'Pressure H2 Tank')
        oLog.add_value('Example:s:TankCO2.aoPhases(1, 1)', 'fPressure', 'Pa', 'Pressure CO2 Tank')
        oLog.add_value('Example:c:BoschReactor:s:Compressor.aoPhases(1, 1)', 'fPressure', 'Pa', 'Pressure Compressor')

        # Additional monitors for system mass and flow rates
        # (similar additions based on the MATLAB code above)

        # Set simulation time
        self.fSimTime = 1 * 300

    def plot(self):
        import matplotlib.pyplot as plt
        from simulation.infrastructure import Plotter

        plt.close('all')
        oPlotter = Plotter(self)

        tPlotOptions = {'sTimeUnit': 'hours'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}

        coPlots = []

        # Define RWGS plots
        coPlots.append(oPlotter.define_plot(
            ['"RWGS Molar Inflow CO2"', '"RWGS Molar Outflow CO2"'], 
            'Molar Flows CO2 RWGS', tPlotOptions)
        )
        coPlots.append(oPlotter.define_plot(
            ['"RWGS CO2 Conversion Ratio"', '"RWGS CO2 Reaction Rate"'], 
            'Conversion and Reaction Rates CO2 RWGS', tPlotOptions)
        )

        # Define system pressure and flowrate plots
        coPlots.append(oPlotter.define_plot(
            ['"Pressure H2 Tank"', '"Pressure CO2 Tank"'], 
            'System Pressures', tPlotOptions)
        )
        coPlots.append(oPlotter.define_plot(
            ['"H2 to RGWS"', '"CO2 to RGWS"'], 
            'System Flowrates', tPlotOptions)
        )

        oPlotter.define_figure(coPlots, 'System Pressures and Flowrates', tFigureOptions)
        oPlotter.plot()
