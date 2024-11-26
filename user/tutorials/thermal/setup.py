class Setup(simulation.infrastructure):
    def __init__(self, ptConfigParams, tSolverParams):
        ttMonitorConfig = {}
        super().__init__('Tutorial_Thermal_Test', ptConfigParams, tSolverParams, ttMonitorConfig)
        
        # Add the example system
        tutorials.thermal.systems.Example(self.oSimulationContainer, 'Example')
        
        # Simulation settings
        self.fSimTime = 3600 * 1  # 1 hour
        self.bUseTime = True
        
        # Initialize log indexes
        self.tiLogIndexes = {}

    def configureMonitors(self):
        oLog = self.toMonitors.oLogger

        # Logging temperature of flows
        self.tiLogIndexes['iTempIdx1'] = oLog.add_value(
            'Example.toProcsF2F.Pipe.aoFlows(1)', 'fTemperature', 'K', 'Flow Temperature - Left', 'flow_temp_left'
        )
        self.tiLogIndexes['iTempIdx2'] = oLog.add_value(
            'Example.toProcsF2F.Pipe.aoFlows(2)', 'fTemperature', 'K', 'Flow Temperature - Right', 'flow_temp_right'
        )

        # Logging partial pressures and flow rates
        oLog.add_value('Example:s:Tank_1.toPhases.Tank1Air', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 'Partial Pressure CO_2 Tank 1', 'ppCO2_Tank1')
        oLog.add_value('Example:s:Tank_2.toPhases.Tank2Air', 'afPP(this.oMT.tiN2I.CO2)', 'Pa', 'Partial Pressure CO_2 Tank 2', 'ppCO2_Tank2')

        oLog.add_value(
            'Example.aoBranches(1).aoFlows(1)', 
            'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)', 
            'kg/s', 
            'Flowrate of CO2', 
            'fr_co2'
        )

        # Logging mass and temperature of tanks
        oLog.add_value('Example:s:Tank_1.toPhases.Tank1Air', 'afMass(this.oMT.tiN2I.CO2)', 'kg')
        oLog.add_value('Example:s:Tank_2.toPhases.Tank2Air', 'afMass(this.oMT.tiN2I.CO2)', 'kg', 'Partial Mass CO_2 Tank 2')
        oLog.add_value('Example:s:Tank_1.toPhases.Tank1Air', 'fTemperature', 'K', 'Temperature Air 1')
        oLog.add_value('Example:s:Tank_2.toPhases.Tank2Air', 'fTemperature', 'K', 'Temperature Air 2')
        oLog.add_value('Example:s:Space.toPhases.VacuumPhase', 'fTemperature', 'K', 'Temperature Space')

        # Logging filter phases
        oLog.add_value('Example:c:SubSystem:s:Filter.toPhases.FlowPhase', 'fTemperature', 'K', 'Temperature Filter Flow')
        oLog.add_value('Example:c:SubSystem:s:Filter.toPhases.FlowPhase', 'fPressure', 'Pa', 'Pressure Filter Flow')
        oLog.add_value('Example:c:SubSystem:s:Filter.toPhases.FilteredPhase', 'fTemperature', 'K', 'Temperature Filter Absorbed')

        # Logging pressure and flow rates
        oLog.add_value('Example:s:Tank_1.toPhases.Tank1Air', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 1')
        oLog.add_value('Example:s:Tank_2.toPhases.Tank2Air', 'this.fMass * this.fMassToPressure', 'Pa', 'Pressure Phase 2')

        oLog.add_value('Example.toBranches.Branch', 'fFlowRate', 'kg/s', 'Branch Flow Rate', 'branch_FR')
        oLog.add_value('Example:c:SubSystem.toBranches.Inlet', 'fFlowRate', 'kg/s', 'Subsystem Inlet Flow Rate')
        oLog.add_value('Example:c:SubSystem.toBranches.Outlet', 'fFlowRate', 'kg/s', 'Subsystem Outlet Flow Rate')

        # Logging heat flows
        oLog.add_value('Example.toThermalBranches.Branch', 'fHeatFlow', 'W', 'Branch Heat Flow')
        oLog.add_value('Example.toThermalBranches.Radiator', 'fHeatFlow', 'W', 'Radiator Heat Flow')
        oLog.add_value('Example.toThermalBranches.Pipe_Material_Conductor', 'fHeatFlow', 'W', 'Pipe Conductor Heat Flow')
        oLog.add_value('Example:c:SubSystem.toThermalBranches.Inlet', 'fHeatFlow', 'W', 'Subsystem Inlet Heat Flow')
        oLog.add_value('Example:c:SubSystem.toThermalBranches.Outlet', 'fHeatFlow', 'W', 'Subsystem Outlet Heat Flow')
        oLog.add_value('Example:c:SubSystem.toThermalBranches.filterproc', 'fHeatFlow', 'W', 'Subsystem Adsorption Mass Heat Flow')
        oLog.add_value('Example:c:SubSystem.toThermalBranches.Pipe_Material_Conductor_In', 'fHeatFlow', 'W', 'Subsystem Conduction Inlet Heat Flow')
        oLog.add_value('Example:c:SubSystem.toThermalBranches.Pipe_Material_Conductor_Out', 'fHeatFlow', 'W', 'Subsystem Conduction Outlet Heat Flow')
        oLog.add_value('Example:c:SubSystem.toThermalBranches.Convective_Branch', 'fHeatFlow', 'W', 'Subsystem Convective Heat Flow')

        # Logging heat source
        oLog.add_value('Example:s:Tank_1.toPhases.Tank1Air.oCapacity.toHeatSources.Heater', 'fHeatFlow', 'W', 'Phase 1 Heat Source Heat Flow')

    def plot(self):
        oPlotter = plot.simulation.infrastructure(self)

        tPlotOptions = {"sTimeUnit": "hours"}
        coPlots = []

        # Define plots for temperatures, pressures, flow rates, and heat flows
        coPlots.append(oPlotter.define_plot(
            ["Temperature Air 1", "Temperature Air 2", "Temperature Space", "Temperature Filter Flow", "Temperature Filter Absorbed"],
            "Temperatures",
            tPlotOptions
        ))
        coPlots.append(oPlotter.define_plot(
            ["Pressure Phase 1", "Pressure Phase 2", "Pressure Filter Flow"],
            "Pressure",
            tPlotOptions
        ))
        coPlots.append(oPlotter.define_plot(
            ["Branch Flow Rate", "Subsystem Inlet Flow Rate", "Subsystem Outlet Flow Rate"],
            "Flowrate",
            tPlotOptions
        ))
        coPlots.append(oPlotter.define_plot(
            ["Branch Heat Flow", "Radiator Heat Flow", "Pipe Conductor Heat Flow", "Subsystem Inlet Heat Flow",
             "Subsystem Outlet Heat Flow", "Subsystem Conduction Inlet Heat Flow", "Subsystem Conduction Outlet Heat Flow",
             "Subsystem Convective Heat Flow", "Phase 1 Heat Source Heat Flow", "Subsystem Adsorption Mass Heat Flow"],
            "Heat Flows",
            tPlotOptions
        ))

        # Combine and plot
        oPlotter.define_figure(coPlots, "Thermal Values and Flowrates")
        oPlotter.plot()
