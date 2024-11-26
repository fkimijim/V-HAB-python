class Example(vsys):
    """
    Example simulation for a system with a heat exchanger in V-HAB 2.0.
    This system includes four stores with one phase each: two gas phases and two liquid phases.
    """

    def __init__(self, oParent, sName):
        """
        Initialize the Example system.
        
        :param oParent: Parent system
        :param sName: Name of the system
        """
        super().__init__(oParent, sName, 60)
        
        # Basic atmospheric values for initialization
        tAtmosphere = {
            "fTemperature": 295,
            "rRelHumidity": 0.5,
            "fPressure": 101325,
            "fCO2Percent": 0.0062,
        }

        # Adding the CCAA subsystem
        sCDRA = "CDRA"
        components.matter.CCAA.CCAA(self, "CCAA", 60, 277.31, tAtmosphere, sCDRA)

        # Adding the CDRA subsystem
        try:
            tInitialization = oParent.oCfgParams.ptConfigParams["tInitialization"]
            components.matter.CDRA.CDRA(self, "CDRA", tAtmosphere, tInitialization, 60)
        except KeyError:
            components.matter.CDRA.CDRA(self, "CDRA", tAtmosphere, {}, 60)

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        # Gas System
        matter.store(self, "Cabin", 498.71)
        fCoolantTemperature = 277.31
        fCO2Percent = 0.0062

        cAirHelper = matter.helper.phase.create.air_custom(
            self.toStores["Cabin"], 97.71, {"CO2": fCO2Percent}, 295, 0.4, 1e5
        )
        oCabinPhase = matter.phases.gas(
            self.toStores["Cabin"], "CabinAir", cAirHelper[0], cAirHelper[1], cAirHelper[2]
        )

        matter.procs.exmes.gas(oCabinPhase, "Port_ToCCAA")
        matter.procs.exmes.gas(oCabinPhase, "Port_FromCCAA")
        matter.procs.exmes.gas(oCabinPhase, "CDRA_Port_1")

        # Coolant Store
        matter.store(self, "CoolantStore", 1)
        oCoolantPhase = matter.phases.liquid(
            self.toStores["CoolantStore"],
            "Coolant_Phase",
            {"H2O": 1},
            fCoolantTemperature,
            101325,
        )

        matter.procs.exmes.liquid(oCoolantPhase, "Port_1")
        matter.procs.exmes.liquid(oCoolantPhase, "Port_2")

        # Condensate Store
        matter.store(self, "CondensateStore", 1)
        oCondensatePhase = matter.phases.liquid(
            self.toStores["CondensateStore"],
            "Condensate_Phase",
            {"H2O": 1},
            280.15,
            101325,
        )

        matter.procs.exmes.liquid(oCondensatePhase, "Port_1")

        # Vented Store
        matter.store(self, "Vented", 100)
        cAirHelper = matter.helper.phase.create.air_custom(
            self.toStores["Cabin"], 100, {"CO2": fCO2Percent}, 295, 0, 2000
        )
        oVentedPhase = matter.phases.gas(
            self.toStores["Vented"], "VentedMass", cAirHelper[0], cAirHelper[1], cAirHelper[2]
        )
        matter.procs.exmes.gas(oVentedPhase, "Port_1")

        # Connections
        matter.branch(self, "CCAA_Input", {}, "Cabin.Port_ToCCAA")
        matter.branch(self, "CCAA_Output", {}, "Cabin.Port_FromCCAA")
        matter.branch(self, "CCAA_CondensateOutput", {}, "CondensateStore.Port_1")
        matter.branch(self, "CCAA_CoolantInput", {}, "CoolantStore.Port_1")
        matter.branch(self, "CCAA_CoolantOutput", {}, "CoolantStore.Port_2")
        matter.branch(self, "CCAA_CHX_to_CDRA_Out", {}, "CCAA_CDRA_Connection.Port_1")

        matter.branch(self, "CDRA_Input", {}, "CCAA_CDRA_Connection.Port_2")
        matter.branch(self, "CDRA_Output", {}, "Cabin.CDRA_Port_1")
        matter.branch(self, "CDRA_Vent", {}, "Vented.Port_1")

        # Interfaces
        self.toChildren["CCAA"].setIfFlows(
            "CCAA_Input", "CCAA_Output", "CCAA_CondensateOutput", "CCAA_CoolantInput", "CCAA_CoolantOutput", "CCAA_CHX_to_CDRA_Out"
        )
        self.toChildren["CDRA"].setIfFlows("CDRA_Input", "CDRA_Output", "CDRA_Vent")

    def createThermalStructure(self):
        super().createThermalStructure()

        # Heat Sources
        oHeatSource = thermal.heatsource("Heater", 940)
        self.toStores["Cabin"].toPhases["CabinAir"].oCapacity.addHeatSource(oHeatSource)

        oHeatSource = components.thermal.heatsources.ConstantTemperature(
            "Coolant_Constant_Temperature"
        )
        self.toStores["CoolantStore"].toPhases["Coolant_Phase"].oCapacity.addHeatSource(oHeatSource)

        self.toChildren["CDRA"].setReferencePhase(self.toStores["Cabin"].toPhases["CabinAir"])

    def createSolverStructure(self):
        super().createSolverStructure()

        # Cabin setpoint
        self.toChildren["CCAA"].setTemperature(273.15 + 18.33)

        tTimeStepProperties = {"rMaxChange": 0.5}
        self.toStores["CondensateStore"].toPhases["Condensate_Phase"].setTimeStepProperties(
            tTimeStepProperties
        )

    def exec(self, *args):
        super().exec()

        if self.oTimer.fTime <= 19.3 * 3600:
            fCO2Production = 13.2 * 0.45359237 / 86400
            fWaterVapor = 12 * 0.45359237 / 86400
            fDryHeat = 940
            fCoolantTemperature = 277.31
        elif 19.3 * 3600 < self.oTimer.fTime < 37.8 * 3600:
            fCO2Production = 8.8 * 0.45359237 / 86400
            fWaterVapor = 12 * 0.45359237 / 86400
            fDryHeat = 940
            fCoolantTemperature = 277.594
        else:
            fCO2Production = 6.6 * 0.45359237 / 86400
            fWaterVapor = 12 * 0.45359237 / 86400
            fDryHeat = 940
            fCoolantTemperature = 277.594

        afCO2Flow = [0] * self.oMT.iSubstances
        afCO2Flow[self.oMT.tiN2I["CO2"]] = fCO2Production
        self.toStores["Cabin"].toProcsP2P["CrewCO2"].setFlowRate(afCO2Flow)

        afH2OFlow = [0] * self.oMT.iSubstances
        afH2OFlow[self.oMT.tiN2I["H2O"]] = fWaterVapor
        self.toStores["Cabin"].toProcsP2P["CrewHumidity"].setFlowRate(afH2OFlow)

        self.toStores["Cabin"].toPhases["CabinAir"].oCapacity.toHeatSources["Heater"].setHeatFlow(
            fDryHeat
        )
        self.toStores["CoolantStore"].toPhases["Coolant_Phase"].oCapacity.toHeatSources[
            "Coolant_Constant_Temperature"
        ].setTemperature(fCoolantTemperature)

        self.oTimer.synchronizeCallBacks()
