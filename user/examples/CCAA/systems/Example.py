class Example(vsys):
    """
    Example simulation for the Common Cabin Air Assembly (CCAA) Subsystem.
    """

    def __init__(self, oParent, sName, tParameters=None):
        super().__init__(oParent, sName)

        if tParameters is None:
            tParameters = {}

        # Initialize test setpoints
        self.tProtoTestSetpoints = [
            {
                "fCoolantTemperature": 273.15 + 6.44,
                "fGasTemperature": 273.15 + 18.16,
                "fDewPointAir": 273.15 + 13.06,
                "fTCCV_Angle": 40,
                "fVolumetricAirFlow": 0.2,
                "fCoolantFlow": 145.15e-3,
            },
            {
                "fCoolantTemperature": 273.15 + 5.61,
                "fGasTemperature": 273.15 + 18.01,
                "fDewPointAir": 273.15 + 12.81,
                "fTCCV_Angle": 5,
                "fVolumetricAirFlow": 0.2,
                "fCoolantFlow": 74.27e-3,
            },
            # Other test cases (3-6) would follow in the same format...
        ]

        # Default atmosphere properties
        tAtmosphere = {
            "fPressure": 101325,
        }

        for iProtoflightTest, testSetpoint in enumerate(self.tProtoTestSetpoints, start=1):
            tAtmosphere["fTemperature"] = testSetpoint["fGasTemperature"]

            fVaporPressureGasTemperature = self.oMT.calculateVaporPressure(
                testSetpoint["fGasTemperature"], "H2O"
            )
            fVaporPressureDewPoint = self.oMT.calculateVaporPressure(
                testSetpoint["fDewPointAir"], "H2O"
            )

            testSetpoint["rRelHumidity"] = (
                fVaporPressureDewPoint / fVaporPressureGasTemperature
            )
            tAtmosphere["rRelHumidity"] = fVaporPressureDewPoint / fVaporPressureGasTemperature

            # Add the subsystem CCAA
            oCCAA = components.matter.CCAA.CCAA(
                self,
                f"CCAA_{iProtoflightTest}",
                5,
                testSetpoint["fCoolantTemperature"],
                tAtmosphere,
                None,  # No associated CDRA subsystem
            )

            tFixValues = {
                "fTCCV_Angle": testSetpoint["fTCCV_Angle"],
                "fVolumetricAirFlowRate": testSetpoint["fVolumetricAirFlow"],
                "fCoolantFlowRate": testSetpoint["fCoolantFlow"],
            }
            oCCAA.setFixValues(tFixValues)

            oCCAA.setParameterOverwrite(tParameters)

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        fTotalGasPressure = 101325

        for iProtoflightTest, testSetpoint in enumerate(self.tProtoTestSetpoints, start=1):
            cabin_name = f"Cabin_{iProtoflightTest}"
            coolant_name = f"Coolant_{iProtoflightTest}"
            condensate_name = f"Condensate_{iProtoflightTest}"

            # Create Cabin
            matter.store(self, cabin_name, 10)
            oCabin = self.toStores[cabin_name].createPhase(
                "gas",
                "Air",
                self.toStores[cabin_name].fVolume,
                {
                    "N2": 0.7896 * fTotalGasPressure,
                    "O2": 0.21 * fTotalGasPressure,
                    "CO2": 0.0004 * fTotalGasPressure,
                },
                testSetpoint["fGasTemperature"],
                testSetpoint["rRelHumidity"],
            )

            # Create Coolant
            matter.store(self, coolant_name, 2)
            oCoolant = self.toStores[coolant_name].createPhase(
                "liquid",
                "boundary",
                "Water",
                self.toStores[coolant_name].fVolume,
                {"H2O": 1},
                testSetpoint["fCoolantTemperature"],
                1e5,
            )

            # Create Condensate
            matter.store(self, condensate_name, 2)
            oCondensate = self.toStores[condensate_name].createPhase(
                "liquid",
                "Water",
                self.toStores[condensate_name].fVolume,
                {"H2O": 1},
                testSetpoint["fCoolantTemperature"],
                1e5,
            )

            # Define Branches
            matter.branch(self, f"CCAAinput{iProtoflightTest}", {}, oCabin)
            matter.branch(self, f"CCAA_Output{iProtoflightTest}", {}, oCabin)
            matter.branch(self, f"CCAA_CondensateOutput{iProtoflightTest}", {}, oCondensate)
            matter.branch(self, f"CCAA_CoolantInput{iProtoflightTest}", {}, oCoolant)
            matter.branch(self, f"CCAA_CoolantOutput{iProtoflightTest}", {}, oCoolant)

            # Interface with CCAA subsystem
            self.toChildren[f"CCAA_{iProtoflightTest}"].setIfFlows(
                f"CCAAinput{iProtoflightTest}",
                f"CCAA_Output{iProtoflightTest}",
                f"CCAA_CondensateOutput{iProtoflightTest}",
                f"CCAA_CoolantInput{iProtoflightTest}",
                f"CCAA_CoolantOutput{iProtoflightTest}",
            )

    def createThermalStructure(self):
        super().createThermalStructure()

    def createSolverStructure(self):
        super().createSolverStructure()
        self.setThermalSolvers()

    def exec(self, _):
        super().exec()
