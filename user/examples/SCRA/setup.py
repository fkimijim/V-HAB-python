class Setup(simulation.infrastructure):
    """
    SETUP class to setup a simulation for Example_SCRA.
    """

    def __init__(self, ptConfigParams, tSolverParams):
        # Initialize the parent class
        ttMonitorConfig = {
            'oTimeStepObserver': {'sClass': 'simulation.monitors.timestepObserver', 'cParams': [0]},
            'oLogger': {'cParams': [True]}
        }

        super().__init__('Example_SCRA', ptConfigParams, tSolverParams, ttMonitorConfig)

        # Creating the root object
        examples.SCRA.systems.Example(self.oSimulationContainer, 'Example')

        # Simulation length
        self.fSimTime = 3600 * 16.1 + 144 * 60  # In seconds
        self.bUseTime = True

    def configure_monitors(self):
        """
        Configure the monitors for logging.
        """
        oLog = self.toMonitors.oLogger

        # Add various log values
        oLog.addValue('Example:s:Cabin.toPhases.CabinAir', 'rRelHumidity', '-', 'Relative Humidity Cabin')
        oLog.addValue('Example:s:Cabin.toPhases.CabinAir', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 'Partial Pressure CO2')
        oLog.addValue('Example:s:Cabin.toPhases.CabinAir', 'fTemperature', 'K', 'Temperature Atmosphere')

        oLog.addValue('Example:c:CCAA:s:CHX.toPhases.CHX_PhaseIn', 'fTemperature', 'K', 'Temperature CHX')
        oLog.addValue('Example:c:CCAA:s:CHX.toPhases.CHX_PhaseIn', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure CHX')

        oLog.addValue('Example:c:CCAA:s:TCCV.toPhases.TCCV_PhaseGas', 'fTemperature', 'K', 'Temperature TCCV')
        oLog.addValue('Example:c:CCAA:s:TCCV.toPhases.TCCV_PhaseGas', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure TCCV')
        oLog.addValue('Example:c:CCAA:s:TCCV.toPhases.TCCV_PhaseGas', 'afPP(this.oMT.tiN2I.H2O)', 'Pa', 'Partial Pressure H2O TCCV')
        oLog.addValue('Example:c:CCAA:s:TCCV.toPhases.TCCV_PhaseGas', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 'Partial Pressure CO2 TCCV')

        oLog.addValue('Example:c:CCAA:s:CHX.toProcsP2P.CondensingHX', 'fFlowRate', 'kg/s', 'Condensate Flowrate CHX')
        oLog.addValue('Example:c:CCAA', 'fTCCV_Angle', '°', 'TCCV Angle')

        # CDRA Geometry information
        iCellNumber13x = self.oSimulationContainer.toChildren.Example.toChildren.CDRA.tGeometry.Zeolite13x.iCellNumber
        iCellNumberSylobead = self.oSimulationContainer.toChildren.Example.toChildren.CDRA.tGeometry.Sylobead.iCellNumber
        iCellNumber5A = self.oSimulationContainer.toChildren.Example.toChildren.CDRA.tGeometry.Zeolite5A.iCellNumber

        miCellNumber = [iCellNumberSylobead, iCellNumber13x, iCellNumber5A]
        csType = ['Sylobead_', 'Zeolite13x_', 'Zeolite5A_']

        for iType in range(3):
            for iBed in range(2):
                for iCell in range(1, miCellNumber[iType] + 1):
                    oLog.addValue(
                        f'Example:c:CDRA:s:{csType[iType]}{iBed+1}.toPhases.Flow_{iCell}',
                        'fPressure',
                        'Pa',
                        f'Flow Pressure {csType[iType]}{iBed+1} Cell {iCell}'
                    )
                    oLog.addValue(
                        f'Example:c:CDRA:s:{csType[iType]}{iBed+1}.toPhases.Flow_{iCell}',
                        'afPP(this.oMT.tiN2I.H2O)',
                        'Pa',
                        f'Flow Pressure H2O {csType[iType]}{iBed+1} Cell {iCell}'
                    )
                    oLog.addValue(
                        f'Example:c:CDRA:s:{csType[iType]}{iBed+1}.toPhases.Flow_{iCell}',
                        'afPP(this.oMT.tiN2I.CO2)',
                        'Pa',
                        f'Flow Pressure CO2 {csType[iType]}{iBed+1} Cell {iCell}'
                    )
                    oLog.addValue(
                        f'Example:c:CDRA:s:{csType[iType]}{iBed+1}.toPhases.Flow_{iCell}',
                        'fTemperature',
                        'K',
                        f'Flow Temperature {csType[iType]}{iBed+1} Cell {iCell}'
                    )

        # Add virtual values for logging
        oLog.addVirtualValue('-1 .*("CDRA CO2 Inlet Flow 1" + "CDRA CO2 Inlet Flow 2")', 'kg/s', 'CDRA CO2 InletFlow')
        oLog.addVirtualValue('-1 .*("CDRA H2O Inlet Flow 1" + "CDRA H2O Inlet Flow 2")', 'kg/s', 'CDRA H2O InletFlow')

    def plot(self):
        """
        Generate plots for the simulation results.
        """
        close_all_figures()

        try:
            self.toMonitors.oLogger.readFromMat()
        except Exception as e:
            print(f"No data outputted yet: {e}")

        oPlotter = super().plot()
        tPlotOptions = {'sTimeUnit': 'hours', 'bLegend': False}

        # Example: Define a plot
        coPlots = []
        coPlots.append(oPlotter.definePlot(['"CDRA CO2 InletFlow"', '"CDRA H2O InletFlow"'], 'CDRA Inlet Flows', tPlotOptions))
        coPlots.append(oPlotter.definePlot(['"Partial Pressure CO2"'], 'Partial Pressure CO2 Habitat', tPlotOptions))
        oPlotter.defineFigure(coPlots, 'Example Plots')

        oPlotter.plot()
