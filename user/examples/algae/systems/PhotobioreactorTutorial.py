class PhotobioreactorTutorial:
    """
    PHOTOBIOREACTORTUTORIAL
    Cabin system that incorporates human, CCAA, and PBR (PBR has algae as a subsystem).
    The cabin system and human are based on the V-HAB tutorial of the human model.
    """

    def __init__(self, oParent, sName):
        self.oParent = oParent
        self.sName = sName
        self.txPhotobioreactorProperties = {}
        self.oPBR = None
        self.tCurrentFoodRequest = None
        self.cScheduledFoodRequest = []
        self.fFoodPrepTime = 3 * 60
        self.fInitialFoodPrepMass = None
        self.iCrewMembers = 4

        # Initialize parent class (replace `vsys` with actual parent class if needed)
        super().__init__()

        # Photobioreactor properties
        self.txPhotobioreactorProperties = {
            'sLightColor': 'RedExperimental',
            'fSurfacePPFD': 400,
            'fGrowthVolume': self.iCrewMembers * 0.0625,
            'fDepthBelowSurface': 0.0025,
            'fMembraneSurface': 10,
            'fMembraneThickness': 0.0001,
            'sMembraneMaterial': 'SSP-M823 Silicone',
            'fCirculationVolumetricFlowPerFilter': 4.167 * 10**-7,
            'fNumberOfParallelFilters': 30,
            'bUseUrine': True,
        }

        # Create Photobioreactor object
        components.matter.PBR.systems.Photobioreactor(self, 'Photobioreactor', self.txPhotobioreactorProperties)

        # Initialize CCAA subsystem
        self.initialize_ccaa()

        # Add Human to the cabin
        self.add_humans_to_cabin()

    def initialize_ccaa(self):
        """
        Initializes the CCAA subsystem.
        """
        fCoolantTemperature = 280
        tAtmosphere = {
            'fTemperature': 295,
            'rRelHumidity': 0.8,
            'fPressure': 101325,
        }
        sCDRA = None
        components.matter.CCAA.CCAA(self, 'CCAA', 60, fCoolantTemperature, tAtmosphere, sCDRA)

    def add_humans_to_cabin(self):
        """
        Add human models to the cabin, based on the V-HAB human tutorial.
        """
        iLengthOfMission = 200  # [d]
        ctEvents = [[None for _ in range(self.iCrewMembers)] for _ in range(iLengthOfMission)]

        tMealTimes = {
            'Breakfast': 0.1 * 3600,
            'Lunch': 6 * 3600,
            'Dinner': 15 * 3600,
        }

        for iCrewMember in range(1, self.iCrewMembers + 1):
            iEvent = 0

            for iDay in range(1, iLengthOfMission + 1):
                if iCrewMember in [1, 4]:
                    ctEvents[iEvent][iCrewMember - 1] = {
                        'State': 2,
                        'Start': ((iDay - 1) * 24 + 1) * 3600,
                        'End': ((iDay - 1) * 24 + 2) * 3600,
                        'Started': False,
                        'Ended': False,
                        'VO2_percent': 0.75,
                    }
                elif iCrewMember in [2, 5]:
                    ctEvents[iEvent][iCrewMember - 1] = {
                        'State': 2,
                        'Start': ((iDay - 1) * 24 + 5) * 3600,
                        'End': ((iDay - 1) * 24 + 6) * 3600,
                        'Started': False,
                        'Ended': False,
                        'VO2_percent': 0.75,
                    }
                elif iCrewMember in [3, 6]:
                    ctEvents[iEvent][iCrewMember - 1] = {
                        'State': 2,
                        'Start': ((iDay - 1) * 24 + 9) * 3600,
                        'End': ((iDay - 1) * 24 + 10) * 3600,
                        'Started': False,
                        'Ended': False,
                        'VO2_percent': 0.75,
                    }

                iEvent += 1

                ctEvents[iEvent][iCrewMember - 1] = {
                    'State': 0,
                    'Start': ((iDay - 1) * 24 + 14) * 3600,
                    'End': ((iDay - 1) * 24 + 22) * 3600,
                    'Started': False,
                    'Ended': False,
                }
                iEvent += 1

            txCrewPlaner = {
                'ctEvents': [event for event in ctEvents if event[iCrewMember - 1] is not None],
                'tMealTimes': tMealTimes,
            }
            components.matter.DetailedHuman.Human(self, f'Human_{iCrewMember}', txCrewPlaner, 60)

    def createMatterStructure(self):
        """
        Creates the matter structure for the Photobioreactor system.
        """
        # Implementation of store creation and connections between subsystems goes here.
        pass

    def createThermalStructure(self):
        """
        Creates the thermal structure for the Photobioreactor system.
        """
        pass

    def createSolverStructure(self):
        """
        Creates the solver structure for the Photobioreactor system.
        """
        pass

    def exec(self):
        """
        Executes the Photobioreactor system.
        """
        self.oTimer.synchronizeCallBacks()
