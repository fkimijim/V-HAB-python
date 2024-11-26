class Example(vsys):
    """
    Example simulation for a system with the Sabatier Carbon Dioxide Reduction Assembly (SCRA).
    It requires the CDRA for CO2 supply and therefore also the CCAA.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 60)

        # Atmospheric initialization values for the CCAA
        tAtmosphere = {
            'fTemperature': 295,
            'rRelHumidity': 0.5,
            'fPressure': 101325,
            'fCO2Percent': 0.0062
        }

        # CDRA subsystem name
        sCDRA = 'CDRA'

        # Adding the CCAA subsystem
        components.matter.CCAA.CCAA(self, 'CCAA', 60, 277.31, tAtmosphere, sCDRA)

        # Adding the CDRA subsystem
        try:
            tInitialization = oParent.oCfgParams.ptConfigParams.get('tInitialization')
            components.matter.CDRA.CDRA(self, 'CDRA', tAtmosphere, tInitialization, 60)
        except KeyError:
            components.matter.CDRA.CDRA(self, 'CDRA', tAtmosphere, None, 60)

        # Adding the SCRA subsystem
        components.matter.SCRA.SCRA(self, 'SCRA', 20, 277.31)

    def create_matter_structure(self):
        super().create_matter_structure()

        # Gas System
        # Creating a cabin store with a volume of 97.71 m^3
        matter.store(self, 'Cabin', 97.71)
        fCoolantTemperature = 277.31
        oCabinPhase = self.toStores.Cabin.create_phase(
            'gas', 'boundary', 'CabinAir', 97.71,
            {'N2': 8e4, 'O2': 2e4, 'CO2': 200},
            295, 0.4
        )
        matter.procs.exmes.gas(oCabinPhase, 'Port_ToCCAA')
        matter.procs.exmes.gas(oCabinPhase, 'Port_FromCCAA')
        matter.procs.exmes.gas(oCabinPhase, 'CDRA_Port_1')

        # Coolant store
        matter.store(self, 'CoolantStore', 1)
        oCoolantPhase = matter.phases.liquid(
            self.toStores.CoolantStore, 'Coolant_Phase',
            {'H2O': 1}, fCoolantTemperature, 101325
        )
        matter.procs.exmes.liquid(oCoolantPhase, 'Port_1')
        matter.procs.exmes.liquid(oCoolantPhase, 'Port_2')

        # Condensate store
        matter.store(self, 'CondensateStore', 1)
        oCondensatePhase = matter.phases.liquid(
            self.toStores.CondensateStore, 'Condensate_Phase',
            {'H2O': 1}, 280.15, 101325
        )
        matter.procs.exmes.liquid(oCondensatePhase, 'Port_1')

        # Store for vented gas
        matter.store(self, 'Vented', 100)
        oVentedPhase = self.toStores.Vented.create_phase(
            'gas', 'boundary', 'VentedMass', 200,
            {'N2': 3}, 295, 0
        )

        # CDRA and CCAA connection
        matter.store(self, 'CCAA_CDRA_Connection', 0.1)
        oConnectionPhase = self.toStores.CCAA_CDRA_Connection.create_phase(
            'gas', 'flow', 'CabinAir', 0.1,
            {'N2': 8e4, 'O2': 2e4, 'CO2': 200}, 295, 0
        )
        matter.procs.exmes.gas(oConnectionPhase, 'Port_1')
        matter.procs.exmes.gas(oConnectionPhase, 'Port_2')

        # CO2 connection for SCRA
        fConnectionVolume = 1e-6
        matter.store(self, 'CO2_Connection', fConnectionVolume)
        oConnectionCO2 = self.toStores.CO2_Connection.create_phase(
            'gas', 'flow', 'CO2_Connection_Phase', fConnectionVolume,
            {'CO2': 1e5}, 295, 0
        )

        # H2 connection for SCRA
        matter.store(self, 'H2_Connection', 100 + fConnectionVolume)
        oH2 = self.toStores.H2_Connection.create_phase(
            'gas', 'boundary', 'H2_Phase', 100,
            {'H2': 1e5}, 295, 0
        )
        oConnectionH2 = self.toStores.H2_Connection.create_phase(
            'gas', 'flow', 'H2_Connection_Phase', fConnectionVolume,
            {'H2': 1e5}, 295, 0
        )

        # Define branches
        matter.branch(self, 'CCAA_Input', {}, 'Cabin.Port_ToCCAA')
        matter.branch(self, 'CCAA_Output', {}, 'Cabin.Port_FromCCAA')
        matter.branch(self, 'CCAA_CondensateOutput', {}, 'CondensateStore.Port_1')
        matter.branch(self, 'CCAA_CoolantInput', {}, 'CoolantStore.Port_1')
        matter.branch(self, 'CCAA_CoolantOutput', {}, 'CoolantStore.Port_2')
        matter.branch(self, 'CCAA_CHX_to_CDRA_Out', {}, 'CCAA_CDRA_Connection.Port_1')

        matter.branch(self, 'CDRA_Input', {}, 'CCAA_CDRA_Connection.Port_2')
        matter.branch(self, 'CDRA_Output', {}, 'Cabin.CDRA_Port_1')
        matter.branch(self, 'CDRA_Vent', {}, oConnectionCO2)

        # SCRA
        matter.branch(self, oH2, {}, oConnectionH2, 'H2_to_SCRA')
        matter.branch(self, 'SCRA_H2_In', {}, oConnectionH2)
        matter.branch(self, 'SCRA_CO2_In', {}, oConnectionCO2)
        matter.branch(self, 'SCRA_DryGas_Out', {}, oVentedPhase)
        matter.branch(self, 'SCRA_Condensate_Out', {}, oCondensatePhase)
        matter.branch(self, 'SCRA_CoolantIn', {}, oCoolantPhase)
        matter.branch(self, 'SCRA_CoolantOut', {}, oCoolantPhase)

        # Set flows for subsystems
        self.toChildren.CCAA.setIfFlows('CCAA_Input', 'CCAA_Output', 'CCAA_CondensateOutput', 'CCAA_CoolantInput', 'CCAA_CoolantOutput', 'CCAA_CHX_to_CDRA_Out')
        self.toChildren.CDRA.setIfFlows('CDRA_Input', 'CDRA_Output', 'CDRA_Vent')
        self.toChildren.SCRA.setIfFlows('SCRA_H2_In', 'SCRA_CO2_In', 'SCRA_DryGas_Out', 'SCRA_Condensate_Out', 'SCRA_CoolantIn', 'SCRA_CoolantOut')

    def create_solver_structure(self):
        super().create_solver_structure()

        # Configure temperature
        self.toChildren.CCAA.setTemperature(273.15 + 18.33)

        # Set solver properties
        solver.matter.manual.branch(self.toBranches.H2_to_SCRA)

        for store in self.toStores.values():
            for phase in store.aoPhases:
                phase.set_time_step_properties({'fMaxStep': 300, 'rMaxChange': 0.05})

        self.set_thermal_solvers()

    def exec(self, _):
        super().exec()
        if self.oTimer.fTime > 143 * 60 and self.toBranches.H2_to_SCRA.fFlowRate == 0:
            self.toBranches.H2_to_SCRA.oHandler.setFlowRate((2.461e-3 * 0.089885) / 60)
        self.oTimer.synchronize_callbacks()
