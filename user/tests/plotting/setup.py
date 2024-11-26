class Setup(simulation.infrastructure):
    """
    Setup class for Test_Plotting simulation.
    - Instantiate the root object.
    - Configure logging and monitoring.
    - Set simulation duration.
    - Provide methods for plotting results.
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
        super().__init__('Test_Plotting', ptConfigParams, tSolverParams, ttMonitorConfig or {})
        examples.plotting.systems.Example(self.oSimulationContainer, 'Example')
        self.fSimTime = fSimTime if fSimTime is not None else 3600
        self.tiLogIndexes = {}

    def configure_monitors(self):
        """
        Configure monitors for logging.
        """
        oLog = self.toMonitors.oLogger

        # Adding log values
        self.tiLogIndexes['iTempIdx1'] = oLog.addValue(
            'Example.toProcsF2F.Pipe.aoFlows(1)', 'fTemperature', 'K', 
            'Flow Temperature - Left', 'flow_temp_left'
        )
        self.tiLogIndexes['iTempIdx2'] = oLog.addValue(
            'Example.toProcsF2F.Pipe.aoFlows(2)', 'fTemperature', 'K', 
            'Flow Temperature - Right', 'flow_temp_right'
        )

        # Add CO2 partial pressure and other properties
        oLog.addValue('Example:s:Tank_1.aoPhases(1)', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 
                      'Partial Pressure CO_2 Tank 1', 'ppCO2_Tank1')
        oLog.addValue('Example:s:Tank_2.aoPhases(1)', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 
                      'Partial Pressure CO_2 Tank 2', 'ppCO2_Tank2')

        # Add CO2 flow rate calculation
        oLog.addValue('Example.aoBranches(1).aoFlows(1)', 
                      'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)', 
                      'kg/s', 'Flowrate of CO2', 'fr_co2')

        # Add other phase-related values
        oLog.addValue('Example:s:Tank_1.aoPhases(1)', 'afMass(this.oMT.tiN2I.CO2)', 'kg')
        oLog.addValue('Example:s:Tank_2.aoPhases(1)', 'afMass(this.oMT.tiN2I.CO2)', 'kg', 'Partial Mass CO_2 Tank 2')
        oLog.addValue('Example:s:Tank_1.aoPhases(1)', 'fTemperature', 'K', 'Temperature Phase 1')
        oLog.addValue('Example:s:Tank_2.aoPhases(1)', 'fTemperature', 'K', 'Temperature Phase 2')
        oLog.addValue('Example:s:Tank_1.aoPhases(1)', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLog.addValue('Example:s:Tank_2.aoPhases(1)', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')
        oLog.addValue('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate', 'branch_FR')

        # Add virtual values for plotting
        self.tiLogIndexes['iIndex_1'] = oLog.addVirtualValue('fr_co2 * 1000', 'g/s', 'CO_2 Flowrate', 'co2_fr_grams')
        self.tiLogIndexes['iIndex_2'] = oLog.addVirtualValue('flow_temp_left - 273.15', 'degC', 'Temperature Left in Celsius')
        self.tiLogIndexes['iIndex_3'] = oLog.addVirtualValue('mod(flow_temp_right ** 2, 10) / "Partial Mass CO_2 Tank 2"', '-', 'Nonsense')

    def plot(self):
        """
        Plotting the results.
        """
        oPlotter = super().plot()

        # Define plots
        cxPlotValues1 = ['"CO_2 Flowrate"', self.tiLogIndexes['iIndex_2'], 'Nonsense']
        csPlotValues2 = ['"Partial Pressure CO_2 Tank 1"', '"Partial Pressure CO_2 Tank 2"']
        csPlotValues3 = ['flow_temp_left', 'flow_temp_right']

        tPlotOptions = {
            'csUnitOverride': [['degC'], ['g/s', '-']],
            'tLineOptions': {'fr_co2': {'csColor': 'g'}, 'Nonsense': {'csColor': 'y'}},
            'bLegend': False
        }
        coPlots = {}
        coPlots[(1, 1)] = oPlotter.definePlot(cxPlotValues1, 'This makes no sense', tPlotOptions)

        tPlotOptions['tLineOptions'] = {'ppCO2_Tank1': {'csColor': 'g'}, 'ppCO2_Tank2': {'csColor': 'y'}}
        coPlots[(1, 2)] = oPlotter.definePlot(csPlotValues2, 'CO_2 Partial Pressures', tPlotOptions)

        tPlotOptions = {'sTimeUnit': 'hours'}
        coPlots[(2, 1)] = oPlotter.definePlot(csPlotValues3, 'Temperatures', tPlotOptions)

        tFigureOptions = {'bTimePlot': True, 'bPlotTools': False}
        oPlotter.defineFigure(coPlots, 'Test Figure Title', tFigureOptions)

        # Additional plotting
        tPlotOptions = {'sAlternativeXAxisValue': '"Branch Flow Rate"', 'sXLabel': 'Main Branch Flow Rate in [kg/s]', 'fTimeInterval': 10}
        coPlots = {oPlotter.definePlot(['"Pressure Phase 1"'], 'Pressure vs. Flow Rate', tPlotOptions)}
        oPlotter.defineFigure(coPlots, 'Pressure vs. Flow Rate')

        tPlotOptions = {'sTimeUnit': 'hours'}
        coPlots = {
            (1, 1): oPlotter.definePlot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures', tPlotOptions),
            (1, 2): oPlotter.definePlot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure', tPlotOptions),
            (2, 1): oPlotter.definePlot(['"Branch Flow Rate"'], 'Flowrate', tPlotOptions),
        }
        oPlotter.defineFigure(coPlots, 'Tank Temperatures')

        # Quick and dirty logging example
        ciIndexes = list(range(1, self.toMonitors.oLogger.iNumberOfLogItems + 1))
        tPlotOptions = {'tFilter': {'sUnit': 'K'}}
        coPlots = {oPlotter.definePlot(ciIndexes, 'Temperatures', tPlotOptions)}
        oPlotter.defineFigure(coPlots, 'All Temperatures')

        # Execute plotting
        oPlotter.plot()
