class Thermal:
    """
    A simple thermal layer for the detailed human model that assumes the human is in thermal equilibrium at all times.
    """

    def __init__(self, oParent, sName):
        self.oParent = oParent
        self.sName = sName

        # Properties
        self.fRequiredSweatWaterFlow = 0  # [kg/s]
        self.fPerspirationWaterOutput = 0  # [kg/s]

        # Constants
        self.fEnthalpyOfVaporizationWater = 2.2574e6  # [J/kg]
        self.fTransepidermalWaterLoss = 0.75 / (24 * 3600)  # [kg/s]

    def createMatterStructure(self):
        """
        Creates the matter structure for the thermal layer.
        """
        fHumanTissueDensity = self.oParent.oMT.calculateDensity('solid', {'Human_Tissue': 1})
        fVolume = self.oParent.toChildren.Metabolic.fBodyMass / fHumanTissueDensity

        self.toStores = {}
        self.toStores['Thermal'] = {
            'phase': {
                'Tissue': {
                    'type': 'solid',
                    'composition': {'Human_Tissue': fVolume},
                    'temperature': self.oParent.fBodyCoreTemperature,
                    'pressure': 1e5
                }
            }
        }

    def createThermalStructure(self):
        """
        Adds a constant temperature heat source to maintain body core temperature.
        """
        oHeatSource = {
            'type': 'ConstantTemperature',
            'name': 'ThermalConstantTemperature'
        }
        self.toStores['Thermal']['phase']['Tissue']['heat_source'] = oHeatSource

    def createSolverStructure(self):
        """
        Sets solver properties for the thermal structure.
        """
        tTimeStepProperties = {'fMaxStep': 60, 'rMaxChange': 0.1}
        self.toStores['Thermal']['phase']['Tissue']['time_step_properties'] = tTimeStepProperties

    def update(self):
        """
        Main update function for the thermal layer.
        """
        fMetabolicHeatFlow = self.oParent.toChildren.Metabolic.fMetabolicHeatFlow

        # Respiration heat flow
        fRespirationLatentHeatFlow = (
            self.fEnthalpyOfVaporizationWater * 
            self.oParent.toChildren.Respiration.fRespirationWaterOutput
        )

        fHeatFlowToHeatExhaledAir = (
            self.oParent.toChildren.Respiration.toStores['Lung']['phase']['Air']['heat_source']['fHeatFlow']
        )

        fOtherRespirationHeatFlows = (
            self.oParent.toChildren.Respiration.toStores['Brain']['phase']['Blood']['heat_source']['fHeatFlow'] +
            self.oParent.toChildren.Respiration.toStores['Tissue']['phase']['Blood']['heat_source']['fHeatFlow']
        )

        fRespirationHeatFlow = (
            fRespirationLatentHeatFlow + fHeatFlowToHeatExhaledAir + fOtherRespirationHeatFlows
        )

        # Transepidermal Water Loss (TEWL) heat flow
        fTransepidermalWaterLossHeatFlow = (
            self.fEnthalpyOfVaporizationWater * self.fTransepidermalWaterLoss
        )

        # Sweat heat flow
        fSweatHeatFlow = (
            ((653.33 - fRespirationLatentHeatFlow - fTransepidermalWaterLossHeatFlow) / 826.11) * 
            (fMetabolicHeatFlow - self.oParent.toChildren.Metabolic.fBaseMetabolicHeatFlow)
        )

        if fSweatHeatFlow < 0:
            fSweatHeatFlow = 0

        self.fRequiredSweatWaterFlow = fSweatHeatFlow / self.fEnthalpyOfVaporizationWater

        # Water flow for sweat
        fWaterFlowSweat = (
            self.fRequiredSweatWaterFlow * 
            self.oParent.toChildren.WaterBalance.rRatioOfAvailableSweat
        )

        # Total perspiration
        self.fPerspirationWaterOutput = fWaterFlowSweat + self.fTransepidermalWaterLoss

        # Set perspiration flow rates
        afPartialFlowRates = {'H2O': self.fPerspirationWaterOutput, 'Naplus': 0}
        self.oParent.toBranches.PerspirationWaterTransfer.setFlowRate(afPartialFlowRates)

        # Perspiration heat flow
        fPerspirationHeatFlow = (
            self.fEnthalpyOfVaporizationWater * self.fPerspirationWaterOutput
        )

        # Sensible heat flow
        fHeatFlowToHeatIngestedMatter = (
            self.oParent.toChildren.Digestion.toStores['Digestion']['phase']['Stomach']['heat_source']['fHeatFlow']
        )

        fSensibleHeatFlow = (
            fMetabolicHeatFlow - fRespirationHeatFlow - fPerspirationHeatFlow - fHeatFlowToHeatIngestedMatter
        )

        # Set sensible heat output
        self.oParent.toThermalBranches.SensibleHeatOutput.setHeatFlow(fSensibleHeatFlow)
