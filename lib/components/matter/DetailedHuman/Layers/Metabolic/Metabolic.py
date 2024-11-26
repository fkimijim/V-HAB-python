class Metabolic:
    def __init__(self, oParent, sName):
        self.oParent = oParent
        self.sName = sName

        # Properties
        self.fBodyMass = 75  # [kg] (Mcardle,2006,p761)
        
        self.fMaxHeartRate = None  # [beat/min]
        self.fMaxCardiacOutput = None  # [l/min]
        self.fRestHeartRate = None  # [beat/min]
        self.fVO2_rest = None  # [l/min]
        self.fVO2_max = None  # [l/min]
        self.fVO2_Debt = 0  # [l/min]
        self.fVO2 = None  # [l/min]
        self.fVCO2 = None  # [l/min]
        
        self.fMaxStrokeVolume = 0.1  # [l/beat]
        self.fRestStrokeVolume = 0.07102  # [l/beat]
        
        self.fLeanBodyMass = None
        self.fBoneMass = None
        self.fOrganMass = None
        self.fTotalH2OMass = None
        self.fH2OinBloodPlasmaMass = None
        self.fH2OinInterstitialFluidMass = None
        self.fH2OinIntracellularFluidMass = None
        
        self.fBMI = None

        self.fMolarVolume = None
        self.rRespiratoryCoefficient = None
        
        self.tfMetabolicConversionFactors = {}
        
        self.hExerciseOnsetFatUsage = None

        self.fCurrentStateStartTime = 0
        self.rActivityLevel = 0.15
        self.rExerciseTargetActivityLevel = 0.15
        self.rActivityLevelBeforeExercise = 0.15

        self.mrExcessPostExerciseActivityLevel = []

        self.tfMetabolicFlowsRest = {}
        self.tfMetabolicFlowsAerobicActivity = {}
        self.tfMetabolicFlowsProteins = {}
        self.tfMetabolicFlowsFatSynthesis = {}

        self.fAlpha_Debt = 0.876
        
        self.fAerobicActivityMetabolicRate = 0
        self.fBaseMetabolicRate = 0
        self.fRestMetabolicRate = 0
        
        self.fTotalMetabolicRate = 0
        self.fLastAerobicMonitorExecution = 0

        self.fTotalAerobicEnergyExpenditure = 0  # [J]
        self.fTotalAerobicActivityEnergyExpenditure = 0  # [J]
        self.fTotalBasicEnergyExpenditure = 0  # [J]
        self.fTotalATPEnergy = 0  # [J]

        self.fMetabolicHeatFlow = None  # [W]
        self.fBaseMetabolicHeatFlow = None  # [W]

        self.bDailyAerobicTrainingThresholdReached = False
        self.bDailyAnaerobicTrainingThresholdReached = False

        self.iRestDays = 0
        self.iAerobicTrainingDays = 0
        self.iAnaerobicTrainingDays = 0
        self.iAerobicTrainingWeeks = 0
        self.iAnaerobicTrainingWeeks = 0
        self.iAerobicDetrainingWeeks = 0
        self.iAnaerobicDetrainingWeeks = 0

        self.fTimeModuloWeek = 0  # s
        self.fTimeModuloDay = 0  # s

        self.tTrainingFactors = {}

        self.fMuscleChangeMassFlow = 0
        self.fMaximumGlucoseContentLiver = None
        self.fMaximumGlucoseContentMuscle = None

        self.tInterpolations = {}

        self.bExercise = False
        self.bPostExercise = False

        self.fRestingDailyEnergyExpenditure = None  # [kJ/day]
        self.fAdditionalFoodEnergyDemand = 0  # [kJ/day]
        self.fCaloricValueOxygen = 1.4654e+07  # [J/kg]
        self.fUreaFlowRate = 0
        self.fLastMetabolismUpdate = 0

        self.fInitialProteinMassMetabolism = None

    def createMatterStructure(self):
        fLiverVolume = 1
        fAdiposeTissueVolume = 10
        fMetabolismVolume = fLiverVolume + fAdiposeTissueVolume + 0.01

        self.fBodyMass = self.fInitialBodyMassWithoutFatOrMuscle + self.tfMetabolicFlowsFatSynthesis.get("AdiposeTissue", {}).get("mass", 0) + self.tfMetabolicFlowsFatSynthesis.get("MuscleTissue", {}).get("mass", 0)
        
        self.fLeanBodyMass = self.fBodyMass - self.tfMetabolicFlowsFatSynthesis.get("AdiposeTissue", {}).get("mass", 0)
        self.fBMI = self.fBodyMass / self.oParent.fHeight ** 2
        self.fRestingDailyEnergyExpenditure = (370 + 21.6 * self.fLeanBodyMass) * 4184

    def createThermalStructure(self):
        pass

    def createSolverStructure(self):
        pass

    def setActivityLevel(self, rActivityLevel, bExercise, bPostExercise):
        self.rActivityLevel = rActivityLevel
        self.bExercise = bExercise
        self.fCurrentStateStartTime = self.oParent.oTimer.fTime
        
        if bExercise:
            self.rExerciseTargetActivityLevel = rActivityLevel
            self.rActivityLevelBeforeExercise = self.rActivityLevel
        else:
            self.rExerciseTargetActivityLevel = None

        if self.bPostExercise and not bPostExercise:
            self.mrExcessPostExerciseActivityLevel = []
        self.bPostExercise = bPostExercise

    def resetAdditionalFoodEnergyDemand(self):
        self.fAdditionalFoodEnergyDemand = 0

    def CardiacPerformance(self):
        self.fMaxHeartRate = 220 - self.oParent.fAge  # [beat/min]
        self.fMaxCardiacOutput = self.fMaxHeartRate * self.fMaxStrokeVolume  # [l/min]
        self.fRestHeartRate = self.fRestCardiacOutput / self.fRestStrokeVolume
        self.fVO2_max = self.tInterpolations.get("hVO2maxFromCardiacOutput", lambda x: x)(self.fMaxCardiacOutput)

    def BodyComposition(self):
        self.fBodyMass = self.fInitialBodyMassWithoutFatOrMuscle + self.tfMetabolicFlowsFatSynthesis.get("AdiposeTissue", {}).get("mass", 0) + self.tfMetabolicFlowsFatSynthesis.get("MuscleTissue", {}).get("mass", 0)
        self.fLeanBodyMass = self.fBodyMass - self.tfMetabolicFlowsFatSynthesis.get("AdiposeTissue", {}).get("mass", 0)
        self.fBMI = self.fBodyMass / self.oParent.fHeight ** 2
        self.fBoneMass = self.fLeanBodyMass * self.rBoneToLeanMassRatio
        self.fOrganMass = self.fLeanBodyMass * self.rOrgansToLeanMassRatio
        self.fTotalH2OMass = self.rH2OtoFatWithoutH2OMassRatio * self.tfMetabolicFlowsFatSynthesis.get("AdiposeTissue", {}).get("mass", 0) + \
                             self.rH2OtoMuscleMassRatio * self.tfMetabolicFlowsFatSynthesis.get("MuscleTissue", {}).get("mass", 0) + \
                             self.rH2OtoBoneMassRatio * self.fBoneMass + \
                             self.rH2OtoOrganMassRatio * self.fOrganMass

# Additional methods and their implementations should follow a similar approach,
# translating the MATLAB functionality into Python while ensuring logical consistency.
