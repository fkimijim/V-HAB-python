from FBA_Table import FBA_Table
from RCA_Table import RCATable
from MetOx_Table import MetOxTable

FBATable = FBA_Table()
RCATable = RCATable()
MetOxTable = MetOxTable()

class FilterProcSorpOld:
    """
    This class numerically simulates the sorption and desorption process in an airstream through a filter.
    It calculates and sets the sorption flow rate of CO2 and other sorbates into the sorbent.
    It also calls the desorption processor if necessary.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sType):
        """
        Initialize the FilterProcSorpOld class.
        
        :param oStore: Reference to the store object
        :param sName: Name of the processor
        :param sPhaseIn: Name of the input phase
        :param sPhaseOut: Name of the output phase
        :param sType: Type of the filter ('FBA', 'RCA', or 'MetOx')
        """
        self.oStore = oStore
        self.sName = sName
        self.sPhaseIn = sPhaseIn
        self.sPhaseOut = sPhaseOut
        self.sType = sType

        # Link to desorption processor
        self.DesorptionProc = self.oStore.toProcsP2P.get('DesorptionProcessor')

        # Initialize constants and filter properties
        self.rVoidFraction = self.oStore.rVoidFraction
        self._initialize_filter_properties()
        
        # Initialize numerical variables
        self.iNumGridPoints = 25
        self.fTimeFactor_1 = 1
        self.fTimeFactor_2 = 1
        self.fDeltaX = 0
        self.afDiscreteLength = []

        # Initialize simulation properties
        self.mfC_current = None
        self.mfQ_current = None
        self.arPartials_ads = []
        self.arPartials_des = []

        self._initialize_simulation_properties()

    def _initialize_filter_properties(self):
        """
        Initializes filter-specific properties based on the type.
        """
        if self.sType == 'FBA':
            self.fRhoSorbent = 700  # Zeolite density in kg/m^3
            self.fFilterLength = self.oStore.oGeometry.fHeight
            self.ofilter_table = FBATable()
        elif self.sType == 'RCA':
            self.fRhoSorbent = 636.7  # SA9-T density in kg/m^3
            self.fFilterLength = self.oStore.fx
            self.ofilter_table = RCATable(self)
        elif self.sType == 'MetOx':
            self.fRhoSorbent = 636.7  # Placeholder value
            self.fFilterLength = self.oStore.fx
            self.ofilter_table = MetOxTable()
        else:
            raise ValueError("Unsupported filter type specified.")

    def _initialize_simulation_properties(self):
        """
        Initializes simulation-related properties.
        """
        self.iNumSubstances = 0
        self.csNames = []
        self.aiPositions = []

        # Positions of relevant sorptives in the matter table
        self.aiPositions = [
            self.oStore.oMT.tiN2I['CO2'],
            self.oStore.oMT.tiN2I['H2O'],
            self.oStore.oMT.tiN2I['O2'],
            self.oStore.oMT.tiN2I['N2']
        ]
        self.csNames = [self.oStore.oMT.csSubstances[i] for i in self.aiPositions]
        self.iNumSubstances = len(self.csNames)

        # Molar masses
        self.afMolarMass = [self.oStore.oMT.afMolarMass[i] for i in self.aiPositions]
        self.mfMolarMass = [
            [self.afMolarMass[i] for _ in range(self.iNumGridPoints)]
            for i in range(self.iNumSubstances)
        ]

        # Current concentrations and loadings
        self.mfC_current = [[0] * self.iNumGridPoints for _ in range(self.iNumSubstances)]
        self.mfQ_current = [[0] * self.iNumGridPoints for _ in range(self.iNumSubstances)]

    def set_initial_concentration(self):
        """
        Sets the initial concentrations for the filter based on phase properties.
        """
        self.fSorptionPressure = self.oStore.toPhases[self.sPhaseIn].fPressure
        self.fSorptionTemperature = self.oStore.toPhases[self.sPhaseIn].fTemperature

        arMassFractions = [
            self.oStore.toPhases[self.sPhaseIn].arPartialMass[i]
            for i in self.aiPositions
        ]
        arMolFractions = [
            arMassFractions[i] * self.oStore.toPhases[self.sPhaseIn].fMolarMass / self.afMolarMass[i]
            for i in range(self.iNumSubstances)
        ]

        self.afConcentration = [
            arMolFractions[i] * self.fSorptionPressure / (8.314 * self.fSorptionTemperature)
            for i in range(self.iNumSubstances)
        ]

        for i in range(self.iNumGridPoints):
            for j in range(self.iNumSubstances):
                self.mfC_current[j][i] = self.afConcentration[j]

    def desorption(self, rDesorptionRatio):
        """
        Simplified desorption model. Scales current concentrations and loadings.

        :param rDesorptionRatio: Fraction of desorption to apply
        """
        for i in range(self.iNumSubstances):
            self.mfC_current[i] = [c * (1 - rDesorptionRatio) for c in self.mfC_current[i]]
            self.mfQ_current[i] = [q * (1 - rDesorptionRatio) for q in self.mfQ_current[i]]

    def update(self):
        """
        Performs the main sorption process update, handling transport, reaction, and boundary conditions.
        """
        # Placeholder: Implementation of the update method, including
        # transport and reaction processes, goes here.
        pass
