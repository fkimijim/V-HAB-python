class Setup(simulation.infrastructure):
    """
    Setup class for the RFCS simulation.
    - Instantiates the simulation.
    - Configures logging and monitoring.
    - Defines simulation duration.
    - Provides methods for plotting results.
    """

    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig=None, fSimTime=None):
        """
        Constructor function.

        Args:
            ptConfigParams: Configuration parameters.
            tSolverParams: Solver parameters.
            ttMonitorConfig: Monitor configuration (optional).
            fSimTime: Simulation time in seconds (optional).
        """
        super().__init__('RFCS', ptConfigParams, tSolverParams, ttMonitorConfig or {})
        examples.RFCS.system.RFCS(self.oSimulationContainer, 'RFCS')

        # Set simulation length
        self.fSimTime = fSimTime if fSimTime is not None else 3600 * 24

    def configure_monitors(self):
        """
        Configure monitors for logging values.
        """
        oLogger = self.toMonitors.oLogger

        # Tank logging
        oLogger.addValue('RFCS:s:O2_Tank:p:O2', 'fPressure', 'Pa', 'O_2 Tank Pressure')
        oLogger.addValue('RFCS:s:H2_Tank:p:H2', 'fPressure', 'Pa', 'H_2 Tank Pressure')
        oLogger.addValue('RFCS:s:Water_Tank:p:Water', 'fMass', 'kg', 'H2O Tank Mass')
        oLogger.addValue('RFCS:s:CoolingSystem:p:CoolingWater', 'fTemperature', 'K', 'Coolant Temperature')
        oLogger.addValue('RFCS.toBranches.Radiator_Cooling', 'fFlowRate', 'kg/s', 'Radiator Flowrate')

        # Fuel cell logging
        oLogger.addValue('RFCS:c:FuelCell', 'rEfficiency', '-', 'Fuel Cell Efficiency')
        oLogger.addValue('RFCS:c:FuelCell', 'fStackCurrent', 'A', 'Fuel Cell Current')
        oLogger.addValue('RFCS:c:FuelCell', 'fStackVoltage', 'V', 'Fuel Cell Voltage')
        oLogger.addValue('RFCS:c:FuelCell', 'fPower', 'W', 'Fuel Cell Power')
        oLogger.addValue('RFCS:c:FuelCell:s:FuelCell:p:Membrane.toManips.substance', 
                         'this.afPartialFlows(this.oMT.tiN2I.H2)', 'kg/s', 'Fuel Cell Reaction H_2 Flow')
        oLogger.addValue('RFCS:c:FuelCell:s:FuelCell:p:Membrane.toManips.substance', 
                         'this.afPartialFlows(this.oMT.tiN2I.O2)', 'kg/s', 'Fuel Cell Reaction O_2 Flow')
        oLogger.addValue('RFCS:c:FuelCell:s:FuelCell:p:Membrane.toManips.substance', 
                         'this.afPartialFlows(this.oMT.tiN2I.H2O)', 'kg/s', 'Fuel Cell Reaction H2O Flow')

        # Electrolyzer logging
        oLogger.addValue('RFCS:c:Electrolyzer', 'rEfficiency', '-', 'Electrolyzer Efficiency')
        oLogger.addValue('RFCS:c:Electrolyzer', 'fStackCurrent', 'A', 'Electrolyzer Current')
        oLogger.addValue('RFCS:c:Electrolyzer', 'fStackVoltage', 'V', 'Electrolyzer Voltage')
        oLogger.addValue('RFCS:c:Electrolyzer', 'fPower', 'W', 'Electrolyzer Power')
        oLogger.addValue('RFCS:c:Electrolyzer:s:Electrolyzer:p:Membrane.toManips.substance', 
                         'this.afPartialFlows(this.oMT.tiN2I.H2)', 'kg/s', 'Electrolyzer Reaction H_2 Flow')
        oLogger.addValue('RFCS:c:Electrolyzer:s:Electrolyzer:p:Membrane.toManips.substance', 
                         'this.afPartialFlows(this.oMT.tiN2I.O2)', 'kg/s', 'Electrolyzer Reaction O_2 Flow')
        oLogger.addValue('RFCS:c:Electrolyzer:s:Electrolyzer:p:Membrane.toManips.substance', 
                         'this.afPartialFlows(this.oMT.tiN2I.H2O)', 'kg/s', 'Electrolyzer Reaction H2O Flow')

    def plot(self):
        """
        Define and generate plots for the simulation results.
        """
        # Close any existing figures
        from matplotlib import pyplot as plt
        plt.close('all')

        oPlotter = super().plot()
        tPlotOptions = {'sTimeUnit': 'hours'}

        # RFCS plots
        coPlots = {
            (1, 1): oPlotter.definePlot(['"O_2 Tank Pressure"', '"H_2 Tank Pressure"'], 'Tank Pressures', tPlotOptions),
            (1, 2): oPlotter.definePlot(['"H2O Tank Mass"'], 'Tank Masses', tPlotOptions),
            (2, 1): oPlotter.definePlot(['"Coolant Temperature"'], 'Temperatures', tPlotOptions),
            (2, 2): oPlotter.definePlot(['"Radiator Flowrate"'], 'Flow Rates', tPlotOptions)
        }
        oPlotter.defineFigure(coPlots, 'RFCS')

        # Fuel cell plots
        coPlots = {
            (1, 1): oPlotter.definePlot(['"Fuel Cell Current"', '"Fuel Cell Voltage"'], 'Fuel Cell Electric Parameters', tPlotOptions),
            (1, 2): oPlotter.definePlot(['"Fuel Cell Power"', '"Fuel Cell Efficiency"'], 'Fuel Cell Power', tPlotOptions),
            (2, 1): oPlotter.definePlot(['"Fuel Cell Reaction H_2 Flow"', '"Fuel Cell Reaction O_2 Flow"', '"Fuel Cell Reaction H2O Flow"'], 
                                        'Flowrates', tPlotOptions)
        }
        oPlotter.defineFigure(coPlots, 'FuelCell')

        # Electrolyzer plots
        coPlots = {
            (1, 1): oPlotter.definePlot(['"Electrolyzer Current"', '"Electrolyzer Voltage"'], 'Electrolyzer Electric Parameters', tPlotOptions),
            (1, 2): oPlotter.definePlot(['"Electrolyzer Power"', '"Electrolyzer Efficiency"'], 'Electrolyzer Power', tPlotOptions),
            (2, 1): oPlotter.definePlot(['"Electrolyzer Reaction H_2 Flow"', '"Electrolyzer Reaction O_2 Flow"', '"Electrolyzer Reaction H2O Flow"'], 
                                        'Flowrates', tPlotOptions)
        }
        oPlotter.defineFigure(coPlots, 'Electrolyzer')

        # Generate all plots
        oPlotter.plot()
