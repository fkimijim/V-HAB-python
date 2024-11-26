class Setup(simulation.infrastructure):
    """
    Setup class for plotting example.
    The plot() method contains examples for different features for
    plotting simulation results.
    """

    def __init__(self, *args):
        """
        Constructor function for Setup class.
        """
        super().__init__('Example_Plotting')

        # Creating the 'Example' system as a child of the root system
        # of this simulation.
        examples.plotting.systems.Example(self.oSimulationContainer, 'Example')

        # Setting the simulation duration to one hour.
        self.fSimTime = 3600

        # Initialize a property for log indexes
        self.tiLogIndexes = {}

    def configure_monitors(self):
        """
        Configure monitors and logging for the simulation.
        """
        # Creating a logger object
        oLog = self.toMonitors.oLogger

        # Add log values with specific paths, units, and labels
        oLog.add_value('Example:s:Tank_1:p:Tank_1_Phase_1', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 'Partial Pressure CO_2 Tank 1', 'ppCO2_Tank1')
        oLog.add_value('Example:s:Tank_2:p:Tank_2_Phase_1', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 'Partial Pressure CO_2 Tank 2', 'ppCO2_Tank2')
        oLog.add_value('Example.toBranches.Branch.aoFlows(1)', 'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)', 'kg/s', 'Flowrate of CO2', 'fr_co2')

        oLog.add_value('Example:s:Tank_1:p:Tank_1_Phase_1', 'afMass(this.oMT.tiN2I.CO2)', 'kg')
        oLog.add_value('Example:s:Tank_2:p:Tank_2_Phase_1', 'afMass(this.oMT.tiN2I.CO2)', 'kg', 'Partial Mass CO_2 Tank 2')

        oLog.add_value('Example:s:Tank_1:p:Tank_1_Phase_1', 'fTemperature', 'K', 'Temperature Phase 1')
        oLog.add_value('Example:s:Tank_2:p:Tank_2_Phase_1', 'fTemperature', 'K', 'Temperature Phase 2')

        oLog.add_value('Example:s:Tank_1:p:Tank_1_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLog.add_value('Example:s:Tank_2:p:Tank_2_Phase_1', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')

        oLog.add_value('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate', 'branch_FR')

        oLog.add_value('Example.toProcsF2F.Pipe.aoFlows(1)', 'fTemperature', 'K', 'Flow Temperature - Left', 'flow_temp_left')
        oLog.add_value('Example.toProcsF2F.Pipe.aoFlows(2)', 'fTemperature', 'K', 'Flow Temperature - Right', 'flow_temp_right')

        # Add virtual log values
        self.tiLogIndexes['iIndex_1'] = oLog.add_virtual_value('fr_co2 * 1000', 'g/s', 'CO_2 Flowrate', 'co2_fr_grams')
        self.tiLogIndexes['iIndex_2'] = oLog.add_virtual_value('flow_temp_left - 273.15', 'degC', 'Temperature Left in Celsius')
        self.tiLogIndexes['iIndex_3'] = oLog.add_virtual_value('mod(flow_temp_right ** 2, 10) / "Partial Mass CO_2 Tank 2"', '-', 'Nonsense')

    def plot(self):
        """
        Plotting the results of the simulation.
        """
        # Create a plotter object
        oPlotter = super().plot()

        # Define plots with different value references
        cxPlotValues1 = ['"CO_2 Flowrate"', self.tiLogIndexes['iIndex_2'], 'Nonsense']
        csPlotValues2 = ['"Partial Pressure CO_2 Tank 1"', '"Partial Pressure CO_2 Tank 2"']
        csPlotValues3 = ['flow_temp_left', 'flow_temp_right']

        # Define plot options
        tPlotOptions = {
            'csUnitOverride': [[['degC'], ['g/s', '-']]],
            'tLineOptions': {'fr_co2': {'csColor': 'g'}, 'Nonsense': {'csColor': 'y'}},
            'bLegend': False,
        }
        coPlots = [[oPlotter.define_plot(cxPlotValues1, 'This makes no sense', tPlotOptions)]]

        tPlotOptions['tLineOptions'] = {'ppCO2_Tank1': {'csColor': 'g'}, 'ppCO2_Tank2': {'csColor': 'y'}}
        coPlots[0].append(oPlotter.define_plot(csPlotValues2, 'CO_2 Partial Pressures', tPlotOptions))

        tPlotOptions = {'sTimeUnit': 'hours'}
        coPlots.append([oPlotter.define_plot(csPlotValues3, 'Temperatures', tPlotOptions)])

        # Define a figure with the plots
        tFigureOptions = {'bTimePlot': True, 'bPlotTools': False}
        oPlotter.define_figure(coPlots, 'Test Figure Title', tFigureOptions)

        tPlotOptions = {'sAlternativeXAxisValue': '"Branch Flow Rate"', 'sXLabel': 'Main Branch Flow Rate in [kg/s]', 'fTimeInterval': 10}
        coPlots = [[oPlotter.define_plot(['"Pressure Phase 1"'], 'Pressure vs. Flow Rate', tPlotOptions)]]
        oPlotter.define_figure(coPlots, 'Pressure vs. Flow Rate')

        tPlotOptions = {'sTimeUnit': 'hours'}
        coPlots = [
            [oPlotter.define_plot(['"Temperature Phase 1"', '"Temperature Phase 2"'], 'Temperatures', tPlotOptions)],
            [oPlotter.define_plot(['"Pressure Phase 1"', '"Pressure Phase 2"'], 'Pressure', tPlotOptions)],
            [oPlotter.define_plot(['"Branch Flow Rate"'], 'Flowrate', tPlotOptions)],
        ]
        oPlotter.define_figure(coPlots, 'Tank Temperatures')

        # Filtering by unit
        ciIndexes = list(range(1, self.toMonitors.oLogger.iNumberOfLogItems + 1))
        tPlotOptions = {'tFilter': {'sUnit': 'K'}}
        coPlots = [[oPlotter.define_plot(ciIndexes, 'Temperatures', tPlotOptions)]]
        oPlotter.define_figure(coPlots, 'All Temperatures')

        # Execute the actual plotting
        oPlotter.plot()
