class OGA(vsys):
    """
    Oxygen Generation Assembly (OGA).
    Simulates an electrolyzer that splits water into H2 and O2.
    Can be configured to simulate the Russian Elektron VM electrolyzer.
    """

    def __init__(self, oParent, sName, fFixedTS, fElectrolyzerOutflowTemp, bElektron=False, bOn=True):
        super().__init__(oParent, sName, fFixedTS)
        self.oAtmosphere = None
        self.bOn = bOn
        self.bElektron = bElektron
        self.fElectrolyzerOutflowTemp = fElectrolyzerOutflowTemp

    def createMatterStructure(self):
        super().createMatterStructure()
        
        AmbientTemperature = 295.35  # [K]
        fPressure = 101325  # [Pa]

        # Create Buffer store
        self.createStore('Buffer', 0.01)
        oLiquid = self.toStores['Buffer'].createPhase(
            'water', 'PhaseLiquid', 0.009, AmbientTemperature, fPressure)
        oLiquid.createExme('Port_In_1')
        const_press_exme_liquid(oLiquid, 'Port_OutLiquid', 101325)

        # Create Electrolyzer store
        self.createStore('Electrolyzer', 0.225)
        oH2O = self.toStores['Electrolyzer'].createMixturePhase(
            'PhaseInLiquid', 'liquid',
            {'H2O': 24, 'H2': 0.1, 'O2': 0.1}, AmbientTemperature, fPressure)

        # Create O2 phase
        fDensityO2 = self.oMT.findProperty({
            'sSubstance': 'O2',
            'sProperty': 'Density',
            'sFirstDepName': 'Pressure', 'fFirstDepValue': 101325,
            'sSecondDepName': 'Temperature', 'fSecondDepValue': AmbientTemperature,
            'sPhaseType': 'gas'
        })
        oO2 = self.toStores['Electrolyzer'].createGasPhase(
            'O2Phase', {'O2': fDensityO2 * 0.1}, 0.1, AmbientTemperature)

        # Create H2 phase
        fDensityH2 = self.oMT.findProperty({
            'sSubstance': 'H2',
            'sProperty': 'Density',
            'sFirstDepName': 'Pressure', 'fFirstDepValue': 101325,
            'sSecondDepName': 'Temperature', 'fSecondDepValue': AmbientTemperature,
            'sPhaseType': 'gas'
        })
        oH2 = self.toStores['Electrolyzer'].createGasPhase(
            'H2Phase', {'H2': fDensityH2 * 0.1}, 0.1, AmbientTemperature)

        # Create exmes for Electrolyzer
        oH2O.createExme('Port_In')
        oH2O.createExme('Port_H2_Out')
        oH2.createExme('Port_H2_In')
        const_press_exme(oH2, 'Port_Out_H2', 101325)
        oH2O.createExme('Port_O2_Out')
        oO2.createExme('Port_O2_In')
        const_press_exme(oO2, 'Port_Out_O2', 101325)

        # Create manipulators and P2Ps
        CellStack_manip_proc('ElectrolyzerProcMain', oH2O, self.fElectrolyzerOutflowTemp)
        ManualP2P(self.toStores['Electrolyzer'], 'O2Proc', 'PhaseInLiquid.Port_O2_Out', 'O2Phase.Port_O2_In')
        ManualP2P(self.toStores['Electrolyzer'], 'GLS_proc', 'PhaseInLiquid.Port_H2_Out', 'H2Phase.Port_H2_In')

        # Add f2f components
        CellStack_f2f(self, 'Electrolyzer_f2f_H2', 'Electrolyzer')
        CellStack_f2f(self, 'Electrolyzer_f2f_O2', 'Electrolyzer')

        # Create branches
        self.createBranch('Buffer.Port_In_1', [], 'OGA_Water_In')
        self.createBranch('Electrolyzer.Port_Out_H2', ['Electrolyzer_f2f_H2'], 'OGA_H2_Out')
        self.createBranch('Buffer.Port_OutLiquid', [], 'Electrolyzer.Port_In')
        self.createBranch('Electrolyzer.Port_Out_O2', ['Electrolyzer_f2f_O2'], 'OGA_O2_Out')

        # Set electrolyzer power
        self.toStores['Electrolyzer'].aoPhases[0].toManips.substance.setPower(44.8 * 10)

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.manual.branch(self.toBranches['OGA_Water_In'])
        solver.matter.residual.branch(self.toBranches['OGA_H2_Out'])
        solver.matter.residual.branch(self.toBranches['ELY_In'])
        solver.matter.residual.branch(self.toBranches['OGA_O2_Out'])

        for store in self.toStores.values():
            for phase in store.aoPhases:
                arMaxChange = [0] * self.oMT.iSubstances
                arMaxChange[self.oMT.tiN2I['Ar']] = 0.75
                arMaxChange[self.oMT.tiN2I['O2']] = 1
                arMaxChange[self.oMT.tiN2I['N2']] = 0.75
                arMaxChange[self.oMT.tiN2I['H2']] = 1
                arMaxChange[self.oMT.tiN2I['H2O']] = 0.75
                arMaxChange[self.oMT.tiN2I['CO2']] = 0.75
                arMaxChange[self.oMT.tiN2I['CH4']] = 0.75

                tTimeStepProperties = {'arMaxChange': arMaxChange, 'fMaxStep': self.fTimeStep * 5}
                phase.setTimeStepProperties(tTimeStepProperties)
                phase.oCapacity.setTimeStepProperties({'fMaxStep': self.fTimeStep * 5})

        self.setThermalSolvers()

    def setIfFlows(self, sInlet1, sOutlet1, sOutlet2):
        self.connectIF('OGA_Water_In', sInlet1)
        self.connectIF('OGA_O2_Out', sOutlet1)
        self.connectIF('OGA_H2_Out', sOutlet2)
        self.oAtmosphere = self.toBranches['OGA_O2_Out'].coExmes[1].oPhase

    def exec(self, _):
        super().exec(_)

        if self.oTimer.iTick != 0:
            fAtmosphereO2Press = self.oAtmosphere.afPP[self.oMT.tiN2I['O2']]
            fAtmospherePress = self.oAtmosphere.fPressure
        else:
            fAtmospherePress = 101325
            fAtmosphereO2Press = 20600

        if self.bOn:
            if fAtmosphereO2Press > 23700 or (fAtmosphereO2Press / fAtmospherePress) > 0.235:
                fElectrolyzedMassFlow = (0.2 / (8 / 9)) / (24 * 3600)
            elif fAtmosphereO2Press < 19500:
                fElectrolyzedMassFlow = ((5.22 if self.bElektron else 9.25) / (8 / 9)) / (24 * 3600)
            else:
                fElectrolyzedMassFlow = ((2.59 if self.bElektron else (0.31 * 9)) / (8 / 9)) / (24 * 3600)
        else:
            fElectrolyzedMassFlow = (0.2 / (8 / 9)) / (24 * 3600)

        self.toBranches['OGA_Water_In'].oHandler.setFlowRate(-fElectrolyzedMassFlow)
