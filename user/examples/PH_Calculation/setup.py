class Setup(simulation.infrastructure):
    """
    This class sets up the simulation.
    - Instantiates the root object
    - Determines which items are logged
    - Sets the simulation duration
    - Provides methods for plotting the results
    """
    
    def __init__(self, *args, **kwargs):
        """
        Constructor function
        """
        super().__init__('Example_PH_Calculation', {}, {}, {})
        
        # Creating the 'Example' system as a child of the root system
        examples.PH_Calculation.systems.Example(self.oSimulationContainer, 'Example')
        
        # Setting the simulation duration to 12000 seconds
        self.fSimTime = 12000

    def configure_monitors(self):
        """
        Logging function
        """
        # To make the code more legible, we create a local variable for the logger object.
        oLogger = self.toMonitors.oLogger

        # Adding the tank temperatures to the log
        oLogger.add_value(
            'Example:s:Tank_1:p:Water.toManips.substance',
            'this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.PhosphoricAcid)) + this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.DihydrogenPhosphate)) + this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.HydrogenPhosphate)) + this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.Phosphate))',
            'mol/m^3',
            'Concentration Phosphate'
        )
        oLogger.add_value('Example:s:Tank_1:p:Water.toManips.substance', 'afConcentrations(this.oMT.tiN2I.OH)', 'mol/m^3', 'Concentration OH-')
        oLogger.add_value('Example:s:Tank_1:p:Water.toManips.substance', 'afConcentrations(this.oMT.tiN2I.Naplus)', 'mol/m^3', 'Concentration Naplus')
        oLogger.add_value('Example:s:Tank_1:p:Water.toManips.substance', 'fpH', '-', 'PH')
        oLogger.add_value('Example:s:Tank_1:p:Water', 'fVolume', 'm^3', 'Volume')

        oLogger.add_virtual_value('"Concentration Naplus" / "Concentration Phosphate"', '-', 'OH- to Phosphate')

    def plot(self, *args, **kwargs):
        """
        Plotting function
        """
        # Get a handle to the plotter object associated with this simulation.
        oPlotter = super().plot()

        tPlotOptions = {
            'sAlternativeXAxisValue': '"OH- to Phosphate"',
            'sXLabel': 'n(OH-)/n(H3PO4) in [-]',
            'yLabel': 'PH in [-]'
        }
        coPlots = {
            (1, 1): oPlotter.define_plot({'"PH"'}, 'Titration Curve', tPlotOptions),
            (1, 2): oPlotter.define_plot({'"Concentration Phosphate"', '"Concentration Naplus"'}, 'Concentrations'),
            (2, 1): oPlotter.define_plot({'"PH"'}, 'PH'),
        }

        oPlotter.define_figure(coPlots, 'Plots')

        # Plotting all figures
        oPlotter.plot()

        # Load test data
        with open('+examples/+PH_Calculation/Titration_Curve.csv', 'r') as file:
            mfTestData = np.loadtxt(file, delimiter=',')

        oLogger = self.toMonitors.oLogger

        # Retrieve virtual values
        calculationHandle = next(
            log.calculationHandle for log in oLogger.tVirtualValues if log.sLabel == 'OH- to Phosphate'
        )
        mfOHtoPhosphate = calculationHandle(oLogger.mfLog)
        mfOHtoPhosphate = mfOHtoPhosphate[~np.isnan(mfOHtoPhosphate)]

        # Retrieve PH values
        iPH = next(log.iIndex for log in oLogger.tLogValues if log.sLabel == 'PH')
        mfPH = oLogger.mfLog[:, iPH]
        mfPH = mfPH[~np.isnan(mfPH)]

        # Plot overlay with test data
        plt.figure()
        plt.plot(mfTestData[:, 0], mfTestData[:, 1], label='Literature')
        plt.grid(True)
        plt.xlabel('n(OH-)/n(H3PO4)')
        plt.ylabel('PH in [-]')
        plt.plot(mfOHtoPhosphate[:len(mfPH)], mfPH, label='V-HAB')
        plt.legend()

        # Interpolate test data
        afXDataUnique, ia = np.unique(mfTestData[:, 0], return_index=True)
        afYDataUnique = mfTestData[ia, 1]
        interpolatedTestData = np.interp(mfOHtoPhosphate, afXDataUnique, afYDataUnique)

        # Remove NaN values
        valid_indices = ~np.isnan(interpolatedTestData)
        mfPH = mfPH[valid_indices]
        interpolatedTestData = interpolatedTestData[valid_indices]

        # Calculate differences
        fMaxDiff = np.max(np.abs(mfPH - interpolatedTestData))
        fMinDiff = np.min(np.abs(mfPH - interpolatedTestData))
        fMeanDiff = np.mean(mfPH - interpolatedTestData)
        rMeanPercentualError = 100 * np.mean((mfPH - interpolatedTestData) / interpolatedTestData)

        print(f'Maximum   Difference between Simulation and Test:     {fMaxDiff}')
        print(f'Minimum   Difference between Simulation and Test:     {fMinDiff}')
        print(f'Mean      Difference between Simulation and Test:     {fMeanDiff}')
        print(f'Percent   Difference between Simulation and Test:     {rMeanPercentualError} %')
