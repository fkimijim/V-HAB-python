class Setup(simulation.infrastructure):
    """
    SETUP: This class is used to setup a simulation.
    Used for:
    - Instantiating the top-level system.
    - Setting the simulation duration.
    - Determining which items are logged.
    - Defining how results are plotted.
    """

    def __init__(self, ptConfigParams, tSolverParams, fSimTime=None):
        super().__init__('SWME_Simulation', ptConfigParams, tSolverParams)

        # Instantiate the example system
        examples.SWME.systems.Example(self.oSimulationContainer, 'Test')

        # Set simulation duration
        self.fSimTime = fSimTime if fSimTime is not None else 120

        # Adjust reporting interval for console output
        self.toMonitors.oConsoleOutput.setReportingInterval(1000, 100)

        # Struct with log item indexes
        self.tciLog = {}

    def configure_monitors(self):
        """
        Configure logging for the simulation.
        """
        oLogger = self.toMonitors.oLogger

        # Log temperature values
        self.tciLog["Temperatures"] = [
            oLogger.addValue('Test/SWME:s:SWMEStore.toProcsP2P.X50Membrane', 'fSWMEInletTemperature', 'K', 'SWME In'),
            oLogger.addValue('Test/SWME:s:SWMEStore.toProcsP2P.X50Membrane', 'fSWMEOutletTemperature', 'K', 'SWME Out')
        ]

        # Log flow rates
        self.tciLog["FlowRates"] = [
            oLogger.addValue('Test/SWME:b:InletBranch', 'fFlowRate * -1', 'kg/s', 'Inflow'),
            oLogger.addValue('Test/SWME:b:OutletBranch', 'fFlowRate', 'kg/s', 'Outflow')
        ]

        # Log valve position and area
        self.tciLog["ValvePosition"] = [
            oLogger.addValue('Test/SWME', 'iBPVCurrentSteps', '-', 'Valve Steps')
        ]
        self.tciLog["ValveArea"] = [
            oLogger.addValue('Test/SWME', 'fValveCurrentArea', 'm^2', 'Valve Area')
        ]

        # Log masses
        self.tciLog["Masses"] = [
            oLogger.addValue('Test/SWME:s:SWMEStore:p:VaporPhase', 'this.fMass', 'kg', 'Vapor Phase'),
            oLogger.addValue('Test/SWME:s:SWMEStore:p:FlowPhase', 'this.fMass', 'kg', 'Flow Phase')
        ]

        # Log combinations (e.g., backpressure and heat rejection)
        self.tciLog["Combo"] = [
            oLogger.addValue('Test/SWME:s:SWMEStore:p:VaporPhase', 'this.fMass * this.fMassToPressure', 'Pa', 'Vapor Backpressure'),
            oLogger.addValue('Test/SWME:s:SWMEStore.toProcsP2P.X50Membrane', 'fHeatRejectionSimple', 'W', 'Heat Rejection')
        ]

        # Log vapor mass lost to the environment
        self.tciLog["VaporMass"] = [
            oLogger.addValue('Test:s:EnvironmentTank:p:EnvironmentPhase', 'this.afMassChange(this.oMT.tiN2I.H2O)', 'kg', 'Vapor Mass lost to Environment')
        ]

        # Log vapor flow rates
        self.tciLog["VaporFlowRates"] = [
            oLogger.addValue('Test/SWME:s:SWMEStore.toProcsP2P.X50Membrane', 'fWaterVaporFlowRate', 'kg/s', 'Membrane Flow Rate'),
            oLogger.addValue('Test/SWME:b:EnvironmentBranch', 'fFlowRate', 'kg/s', 'Environment Flow Rate')
        ]

    def plot(self, tInputFigureOptions=None):
        """
        Define and create plots for the simulation.
        """
        oPlotter = super().plot()

        # Initialize figure options
        tFigureOptions = {
            "bTimePlot": True
        }

        # Create a grid of plots
        coPlots = [[None for _ in range(3)] for _ in range(3)]

        coPlots[0][0] = oPlotter.definePlot(self.tciLog["Temperatures"], "Temperatures")
        coPlots[0][1] = oPlotter.definePlot(self.tciLog["FlowRates"], "Water Flow Rates")
        coPlots[0][2] = oPlotter.definePlot(self.tciLog["ValvePosition"], "Valve Position")
        coPlots[1][0] = oPlotter.definePlot(self.tciLog["Masses"], "Masses")
        coPlots[1][1] = oPlotter.definePlot(self.tciLog["Combo"], "Heat Rejection", {"csUnitOverride": [["W"], ["Pa"]]})
        coPlots[1][2] = oPlotter.definePlot(self.tciLog["ValveArea"], "Valve Area")
        coPlots[2][0] = oPlotter.definePlot(self.tciLog["VaporMass"], "Vapor Mass")
        coPlots[2][1] = oPlotter.definePlot(self.tciLog["VaporFlowRates"], "Vapor Flow Rates")

        sName = "SWME Simulation Results"

        if tInputFigureOptions:
            tFigureOptions.update(tInputFigureOptions)

        # Define the figure and plot
        oPlotter.defineFigure(coPlots, sName, tFigureOptions)
        oPlotter.plot()
