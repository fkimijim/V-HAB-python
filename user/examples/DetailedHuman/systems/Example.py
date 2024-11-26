class Example(vsys):
    """
    Example simulation for a human model in V-HAB 2.0.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 600)

        # Properties
        self.iNumberOfCrewMembers = 7
        self.bHumanMoved = False

        # Crew Planer
        iLengthOfMission = 200  # [days]
        tMealTimes = {'Breakfast': 0.1 * 3600, 'Lunch': 6 * 3600, 'Dinner': 15 * 3600}
        mfExerciseStartTime = [1, 5, 9]  # [hours]
        mfExerciseDuration = [0.5 * 3600, 0.5 * 3600, 0.5 * 3600]  # [seconds]
        mfExerciseLevel = [0.75, 0.75, 0.75]
        mfSleepStartTime = [14 * 3600]  # [seconds]
        mfSleepDuration = [8 * 3600]  # [seconds]

        # Schedule Initialization
        ctEvents = [[None for _ in range(self.iNumberOfCrewMembers)] for _ in range(iLengthOfMission)]

        iExerciseGroups = len(mfExerciseStartTime)
        iSleepGroups = len(mfSleepStartTime)

        for iCrewMember in range(1, self.iNumberOfCrewMembers + 1):
            iEvent = 0

            iCurrentExerciseGroup = (iCrewMember - 1) % iExerciseGroups
            iCurrentSleepGroup = (iCrewMember - 1) % iSleepGroups

            for iDay in range(1, iLengthOfMission + 1):
                ctEvents[iEvent][iCrewMember - 1] = {
                    'State': 2,
                    'Start': ((iDay - 1) * 24 * 3600 + mfExerciseStartTime[iCurrentExerciseGroup]),
                    'End': ((iDay - 1) * 24 * 3600 + mfExerciseStartTime[iCurrentExerciseGroup] + mfExerciseDuration[iCurrentExerciseGroup]),
                    'Started': False,
                    'Ended': False,
                    'VO2_percent': mfExerciseLevel[iCurrentExerciseGroup],
                }
                iEvent += 1

                ctEvents[iEvent][iCrewMember - 1] = {
                    'State': 0,
                    'Start': ((iDay - 1) * 24 * 3600 + mfSleepStartTime[iCurrentSleepGroup]),
                    'End': ((iDay - 1) * 24 * 3600 + mfSleepStartTime[iCurrentSleepGroup] + mfSleepDuration[iCurrentSleepGroup]),
                    'Started': False,
                    'Ended': False,
                }
                iEvent += 1

        for iCrewMember in range(1, self.iNumberOfCrewMembers + 1):
            txCrewPlaner = {'ctEvents': [event[iCrewMember - 1] for event in ctEvents], 'tMealTimes': tMealTimes}
            components.matter.DetailedHuman.Human(self, f"Human_{iCrewMember}", txCrewPlaner, 600)

        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        fAmbientTemperature = 294.15
        fDensityH2O = self.oMT.calculateDensity('liquid', {'H2O': 1}, fAmbientTemperature, 101325)

        # Cabin stores
        matter.store(self, 'Cabin', 50)
        oCabinPhase = self.toStores.Cabin.createPhase('gas', 'boundary', 'CabinAir', 48, {'N2': 5.554e4, 'O2': 1.476e4, 'CO2': 40}, fAmbientTemperature, 0.506)
        oCondensatePhase = matter.phases.liquid(self.toStores.Cabin, 'Condensate', {'H2O': fDensityH2O * 0.5}, fAmbientTemperature, 101325)

        matter.store(self, 'Cabin2', 50)
        oCabinPhase2 = self.toStores.Cabin2.createPhase('gas', 'boundary', 'CabinAir', 48, {'N2': 5.554e4, 'O2': 1.476e4, 'CO2': 40}, fAmbientTemperature, 0.506)
        oCondensatePhase2 = matter.phases.liquid(self.toStores.Cabin2, 'Condensate', {'H2O': fDensityH2O * 0.5}, fAmbientTemperature, 101325)

        # Oxygen store
        matter.store(self, 'O2', 100)
        oO2 = self.toStores.O2.createPhase('gas', 'O2', 100, {'O2': 200e5}, fAmbientTemperature, 0)

        # Potable water
        matter.store(self, 'PotableWaterStorage', 10)
        fSodiumMass = 4e-6 * (0.9 * 10 * 1000)
        fSodiumMol = fSodiumMass / self.oMT.afMolarMass[self.oMT.tiN2I.Naplus]
        fChlorideMass = fSodiumMol * self.oMT.afMolarMass[self.oMT.tiN2I.Clminus]
        oPotableWaterPhase = matter.phases.liquid(self.toStores.PotableWaterStorage, 'PotableWater', {'H2O': fDensityH2O * 0.9 * 10, 'Naplus': fSodiumMass, 'Clminus': fChlorideMass}, fAmbientTemperature, 101325)

        # Feces and Urine
        matter.store(self, 'UrineStorage', 10)
        matter.phases.mixture(self.toStores.UrineStorage, 'Urine', 'liquid', {'Urine': 1.6}, 295, 101325)

        matter.store(self, 'FecesStorage', 10)
        matter.phases.mixture(self.toStores.FecesStorage, 'Feces', 'solid', {'Feces': 0.132}, 295, 101325)

        # Food store
        tfFood = {'Food': 100, 'Carrots': 10}
        oFoodStore = components.matter.FoodStore(self, 'FoodStore', 100, tfFood)

        # Branching
        matter.branch(self, oO2, {}, oCabinPhase, 'O2_to_Cabin')
        matter.branch(self, oO2, {}, oCabinPhase2, 'O2_to_Cabin2')

        # Condensate and CO2 P2Ps
        oCondensateP2P = components.matter.P2Ps.ManualP2P(self.toStores.Cabin, 'Condensate', oCabinPhase, oCondensatePhase)
        components.matter.P2Ps.ManualP2P(self.toStores.Cabin2, 'Condensate', oCabinPhase2, oCondensatePhase2)

        oCO2P2P = components.matter.P2Ps.ManualP2P(self.toStores.Cabin, 'CO2', oCabinPhase, oCondensatePhase)
        components.matter.P2Ps.ManualP2P(self.toStores.Cabin2, 'CO2', oCabinPhase2, oCondensatePhase2)

    def exec(self, _):
        super().exec()
        if self.oTimer.fTime > 3 * 24 * 3600 and not self.bHumanMoved:
            for iCrewMember in range(1, self.iNumberOfCrewMembers + 1):
                self.toChildren[f"Human_{iCrewMember}"].moveHuman(self.toStores.Cabin2.toPhases.CabinAir)

            self.bHumanMoved = True
