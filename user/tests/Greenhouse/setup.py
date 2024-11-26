class Setup(simulation.infrastructure):
    """
    Setup file for the Greenhouse system
    """
    
    def __init__(self, ptConfigParams, tSolverParams, ttMonitorConfig, fSimTime=None):
        """
        Initialize the setup for the Greenhouse simulation.
        """
        super().__init__('Test_Greenhouse', ptConfigParams, tSolverParams, ttMonitorConfig)
        
        # Create Root Object - Initializing system 'Greenhouse'
        examples.Greenhouse.systems.Greenhouse(self.oSimulationContainer, 'Greenhouse')
        
        # Set simulation time
        self.fSimTime = fSimTime if fSimTime else 10e6  # [s]
    
    def configure_monitors(self):
        """
        Configure the monitors for the Greenhouse simulation.
        """
        oLogger = self.toMonitors.oLogger
        
        # Find the plant cultures to log
        csCultures = []
        oGreenhouse = self.oSimulationContainer.toChildren.Greenhouse
        for child_name in oGreenhouse.csChildren:
            child_obj = getattr(oGreenhouse.toChildren, child_name)
            if isinstance(child_obj, components.matter.PlantModule.PlantCulture):
                csCultures.append(child_name)
        
        oLogger.addValue('Greenhouse.oTimer', 'fTimeStepFinal', 's', 'Timestep')
        
        # Log culture subsystems
        for culture in csCultures:
            # Balance Mass
            oLogger.addValue(
                f'Greenhouse:c:{culture}:s:Plant_Culture.toPhases.Balance',
                'fMass', 'kg', f'{culture} Balance Mass'
            )
            # Plant Mass
            oLogger.addValue(
                f'Greenhouse:c:{culture}:s:Plant_Culture.toPhases.Plants',
                'fMass', 'kg', f'{culture} Plant Mass'
            )
            # Plant Nutrient Masses
            oLogger.addValue(
                f'Greenhouse:c:{culture}:s:Plant_Culture.toPhases.NutrientSolution',
                'fMass', 'kg', f'{culture} Nutrient Solution Mass'
            )
            oLogger.addValue(
                f'Greenhouse:c:{culture}:s:Plant_Culture.toPhases.StorageNitrate',
                'fMass', 'kg', f'{culture} Nitrogen Storage Mass'
            )
            # Plant Atmosphere Mass
            oLogger.addValue(
                f'Greenhouse:c:{culture}:s:Plant_Culture.toPhases.PlantAtmosphere',
                'fMass', 'kg', f'{culture} Plant Atmosphere Mass'
            )
            # p2p flowrates
            oLogger.addValue(
                f'Greenhouse:c:{culture}:s:Plant_Culture.toProcsP2P.BiomassGrowth_P2P',
                'fFlowRate', 'kg/s', f'{culture} BiomassGrowth'
            )
            oLogger.addValue(
                f'Greenhouse:c:{culture}.toBranches.Atmosphere_In.aoFlows(1)',
                'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2) * -1',
                'kg/s', f'{culture} CO2 In Flow'
            )
            # Log virtual values
            oLogger.addVirtualValue(
                f'"{culture} CO2 In Flow" - "{culture} CO2 Out Flow"',
                'kg/s', f'{culture} Atmosphere CO_2 Flow Rate'
            )
        
        # Greenhouse atmosphere composition
        oLogger.addValue('Greenhouse:s:Atmosphere.toPhases.Atmosphere', 'fPressure', 'Pa', 'Total Pressure')
        oLogger.addValue('Greenhouse:s:Atmosphere.toPhases.Atmosphere', 'rRelHumidity', '-', 'Humidity')
        oLogger.addValue(
            'Greenhouse:s:NutrientSupply.toPhases.NutrientSupply',
            'this.afMass(this.oMT.tiN2I.NO3) / this.oMT.afMolarMass(this.oMT.tiN2I.NO3) / this.afMass(this.oMT.tiN2I.H2O) / 1000',
            '-', 'NO3 Concentration'
        )
    
    def plot(self):
        """
        Define and plot the simulation results.
        """
        import matplotlib.pyplot as plt
        from tools import find_log_indices
        
        plt.close('all')
        
        oPlotter = super().plot()
        tPlotOptions = {'sTimeUnit': 'days'}
        tFigureOptions = {'bTimePlot': False, 'bPlotTools': False}
        
        # Example of defining plots dynamically for plant cultures
        csCultures = []
        oGreenhouse = self.oSimulationContainer.toChildren.Greenhouse
        for child_name in oGreenhouse.csChildren:
            child_obj = getattr(oGreenhouse.toChildren, child_name)
            if isinstance(child_obj, components.matter.PlantModule.PlantCulture):
                csCultures.append(child_name)
        
        coPlots = []
        for culture in csCultures:
            coPlots.append(
                oPlotter.definePlot(
                    [f'"{culture} BiomassGrowth"', f'"{culture} Atmosphere CO_2 Flow Rate"'],
                    f'P2P Flow Rates {culture}',
                    tPlotOptions
                )
            )
        
        # Define figure with plots
        oPlotter.defineFigure(coPlots, 'Plant Module Flow Rates', tFigureOptions)
        oPlotter.plot()
