import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

class Setup(simulation.infrastructure):
    """
    Setup class for PH Calculation simulation.
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
        if ttMonitorConfig is None:
            ttMonitorConfig = {}

        super().__init__('Test_PH_Calculation', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Create the Example system
        examples.PH_Calculation.systems.Example(self.oSimulationContainer, 'Example')

        # Set simulation duration
        self.fSimTime = fSimTime if fSimTime else 10 * 3600

    def configure_monitors(self):
        """
        Configure monitors for logging.
        """
        oLogger = self.toMonitors.oLogger

        # Logging phosphate and OH concentrations, pH, and volume
        oLogger.addValue(
            'Example:s:Tank_1:p:Water.toManips.substance',
            'this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.PhosphoricAcid)) + '
            'this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.DihydrogenPhosphate)) + '
            'this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.HydrogenPhosphate)) + '
            'this.afConcentrations(this.oMT.tiN2I.(this.oMT.tsN2S.Phosphate))',
            'mol/m^3',
            'Concentration Phosphate'
        )
        oLogger.addValue(
            'Example:s:Tank_1:p:Water.toManips.substance',
            'afConcentrations(this.oMT.tiN2I.OH)',
            'mol/m^3',
            'Concentration OH-'
        )
        oLogger.addValue(
            'Example:s:Tank_1:p:Water.toManips.substance',
            'afConcentrations(this.oMT.tiN2I.Naplus)',
            'mol/m^3',
            'Concentration Naplus'
        )
        oLogger.addValue(
            'Example:s:Tank_1:p:Water.toManips.substance',
            'fpH',
            '-',
            'PH'
        )
        oLogger.addValue(
            'Example:s:Tank_1:p:Water',
            'fVolume',
            'm^3',
            'Volume'
        )

        # Adding a virtual value for OH- to phosphate ratio
        oLogger.addVirtualValue(
            '"Concentration Naplus" ./ "Concentration Phosphate"',
            '-',
            'OH- to Phosphate'
        )

    def plot(self):
        """
        Plot the results of the simulation.
        """
        # Create plotter object
        oPlotter = super().plot()

        # Define plots
        tPlotOptions = {'sAlternativeXAxisValue': '"OH- to Phosphate"', 'sXLabel': 'n(OH-)/n(H3PO4) in [-]'}
        tPlotOptions['yLabel'] = 'PH in [-]'
        coPlots = {
            (1, 1): oPlotter.definePlot(['"PH"'], 'Titration Curve', tPlotOptions),
            (1, 2): oPlotter.definePlot(['"Concentration Phosphate"', '"Concentration Naplus"'], 'Concentrations'),
            (2, 1): oPlotter.definePlot(['"PH"'], 'PH')
        }

        # Define and plot figures
        oPlotter.defineFigure(coPlots, 'Plots')
        oPlotter.plot()

        # Overlay experimental data
        test_data = np.loadtxt('+examples/+PH_Calculation/Titration_Curve.csv', delimiter=',')
        x_test, y_test = test_data[:, 0], test_data[:, 1]

        # Simulation data
        oLogger = self.toMonitors.oLogger
        mfOHtoPhosphate = oLogger.getVirtualValue('OH- to Phosphate')
        mfPH = oLogger.getValue('PH')

        # Remove NaN values
        mask = ~np.isnan(mfOHtoPhosphate) & ~np.isnan(mfPH)
        mfOHtoPhosphate = mfOHtoPhosphate[mask]
        mfPH = mfPH[mask]

        # Interpolate test data
        interp_func = interp1d(x_test, y_test, bounds_error=False, fill_value="extrapolate")
        interpolated_test_data = interp_func(mfOHtoPhosphate)

        # Plot comparison
        plt.figure()
        plt.plot(x_test, y_test, label='Literature', linestyle='-')
        plt.plot(mfOHtoPhosphate, mfPH, label='V-HAB', linestyle='--')
        plt.xlabel('n(OH-)/n(H3PO4)')
        plt.ylabel('PH in [-]')
        plt.grid(True)
        plt.legend()

        # Calculate differences
        diffs = mfPH - interpolated_test_data
        max_diff = np.max(np.abs(diffs))
        min_diff = np.min(np.abs(diffs))
        mean_diff = np.mean(diffs)
        percent_error = 100 * np.mean(diffs / interpolated_test_data)

        print(f"Maximum Difference: {max_diff}")
        print(f"Minimum Difference: {min_diff}")
        print(f"Mean Difference: {mean_diff}")
        print(f"Mean Percent Error: {percent_error} %")
