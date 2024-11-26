class Example(vsys):
    """
    Example V-HAB system with CAMRAS.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 10)

        # Atmosphere Control Parameters
        self.fFlowRateH2O = 0.000078667
        self.fFlowRateCO2 = 0.0000583  # CO2 Output for nominal activity
        self.fFlowRateN2 = 0.01
        self.fFlowRateO2 = 0.01

        self.fUpdateFrequency = self.fTimeStep
        self.iCounter = 0
        self.iOn = 0
        self.iOff = 0
        self.iOn2 = 0
        self.iOff2 = 0
        self.iTickModuloCounter = 0

        # Insert CAMRAS subsystems
        components.matter.CAMRAS.CAMRAS(self, 'CAMRAS', 1, 0.0122706, 'exercise')
        components.matter.CAMRAS.CAMRAS(self, 'CAMRAS_2', 1, 0.0122706, 'exercise')

    def createMatterStructure(self):
        super().createMatterStructure()

        fTemperatureInit = 295  # [K]
        fPressureInit = 101325  # [Pa]
        fRelHumidityInit = 0.2  # Chosen to match test data
        fCO2Percent = 0.002  # Chosen to match test data

        # Atmosphere of Orion Test Rig
        fTestRigVolume = 16.2
        matter.store(self, 'Atmosphere', fTestRigVolume)
        oAtmosphere = self.toStores.Atmosphere.createPhase(
            'gas',
            'Atmosphere_Phase_1',
            fTestRigVolume,
            {'N2': 8e4, 'O2': 2e4, 'CO2': 150},
            fTemperatureInit,
            fRelHumidityInit
        )

        self.toChildren.CAMRAS.setReferencePhase(oAtmosphere)

        matter.procs.exmes.gas(oAtmosphere, 'From_H2O')
        matter.procs.exmes.gas(oAtmosphere, 'From_CO2')
        matter.procs.exmes.gas(oAtmosphere, 'From_N2')
        matter.procs.exmes.gas(oAtmosphere, 'From_O2')
        matter.procs.exmes.gas(oAtmosphere, 'ToCAMRAS_C1')
        matter.procs.exmes.gas(oAtmosphere, 'FromCAMRAS_C1')
        matter.procs.exmes.gas(oAtmosphere, 'ToCAMRAS_C2')
        matter.procs.exmes.gas(oAtmosphere, 'FromCAMRAS_C2')

        # Water Supply
        matter.store(self, 'WaterSupply', 100e3 / 997)
        oWaterSupply = matter.phases.liquid(
            self.toStores.WaterSupply,
            'WaterSupply',
            {'H2O': 100e3},
            fTemperatureInit,
            fPressureInit
        )
        matter.procs.exmes.liquid(oWaterSupply, 'To_Atmosphere')

        # CO2 Supply
        matter.store(self, 'CO2Supply', 20)
        oCO2Supply = matter.phases.gas(
            self.toStores.CO2Supply,
            'CO2Supply',
            {'CO2': 50},
            2,
            fTemperatureInit
        )
        matter.procs.exmes.gas(oCO2Supply, 'To_Atmosphere')

        # Nitrogen Supply
        matter.store(self, 'N2Supply', 100)
        oN2Supply = matter.phases.gas(
            self.toStores.N2Supply,
            'N2Supply',
            {'N2': 50},
            2,
            fTemperatureInit
        )
        matter.procs.exmes.gas(oN2Supply, 'To_Atmosphere')

        # Oxygen Supply
        matter.store(self, 'O2Supply', 20)
        oO2Supply = matter.phases.gas(
            self.toStores.O2Supply,
            'O2Supply',
            {'O2': 50},
            2,
            fTemperatureInit
        )
        matter.procs.exmes.gas(oO2Supply, 'To_Atmosphere')

        # Vacuum
        matter.store(self, 'Vacuum', 100000)
        oVacuum = matter.phases.gas(
            self.toStores.Vacuum,
            'Vacuum_Phase',
            {'N2': 1.12 * 100000},
            100000,
            293.15
        )
        matter.procs.exmes.gas(oVacuum, 'FromCAMRAS_C1_Desorb')
        matter.procs.exmes.gas(oVacuum, 'FromCAMRAS_C2_Desorb')
        matter.procs.exmes.gas(oVacuum, 'FromCAMRAS_C1_Vacuum')
        matter.procs.exmes.gas(oVacuum, 'FromCAMRAS_C2_Vacuum')

        # Connect CAMRAS with atmosphere and vacuum
        self.toChildren.CAMRAS.setIfFlows(
            'FromAtmosphereToCAMRAS_C1', 'ToAtmosphereFromCAMRAS_C1',
            'FromAtmosphereToCAMRAS_C2', 'ToAtmosphereFromCAMRAS_C2',
            'ToVacuumFromCAMRAS_C1_Vacuum', 'ToVacuumFromCAMRAS_C2_Vacuum',
            'ToVacuumFromCAMRAS_C1_Desorb', 'ToVacuumFromCAMRAS_C2_Desorb'
        )

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.manual.branch(self.toBranches.H2OBufferSupply)
        solver.matter.manual.branch(self.toBranches.CO2BufferSupply)
        solver.matter.manual.branch(self.toBranches.N2BufferSupply)
        solver.matter.manual.branch(self.toBranches.O2BufferSupply)

        self.toBranches.H2OBufferSupply.oHandler.setFlowRate(self.fFlowRateH2O)
        self.toBranches.CO2BufferSupply.oHandler.setFlowRate(self.fFlowRateCO2)
        self.toBranches.N2BufferSupply.oHandler.setFlowRate(0)
        self.toBranches.O2BufferSupply.oHandler.setFlowRate(0)

        self.setThermalSolvers()

    def update(self):
        if not self.oTimer.fTime:
            return

        fPartialPressureO2 = self.toStores.Atmosphere.toPhases.Atmosphere_Phase_1.afPP(self.oMT.tiN2I.O2)
        fPressure = self.toStores.Atmosphere.toPhases.Atmosphere_Phase_1.fPressure

        # O2 Controller
        if fPartialPressureO2 <= 18665:
            self.toBranches.O2BufferSupply.oHandler.setFlowRate(self.fFlowRateO2)
        elif fPartialPressureO2 > 23000:
            self.toBranches.O2BufferSupply.oHandler.setFlowRate(0)

        # Pressure Controller
        if fPressure < 100000:
            self.toBranches.N2BufferSupply.oHandler.setFlowRate(self.fFlowRateN2)
        else:
            self.toBranches.N2BufferSupply.oHandler.setFlowRate(0)

    def exec(self, _):
        super().exec(_)
        self.update()

        if self.oTimer.iTick % 500 < self.iTickModuloCounter:
            self.oTimer.synchronizeCallBacks()

        self.iTickModuloCounter = self.oTimer.iTick % 500
