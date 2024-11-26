from FBA_Table import FBA_Table
from RCA_Table import RCATable
from MetOx_Table import MetOxTable

FBA_Table = FBA_Table()
RCA_Table = RCATable()
MetOx_Table = MetOxTable()

class FilterProcSorp:
    """
    Class to simulate the sorption and desorption process in an airstream through a filter.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sType, fLimitTothCalculation=None):
        """
        Constructor for the FilterProcSorp class.
        
        :param oStore: Stor eobject reference
        :param sName: Name of the processor
        :param sPhaseIn: Input phase
        :param sPhaseOut: Output phase
        :param sType: Filter type
        :param fLimitTothCalculation: Limit for Toth equation calculation
        """
        self.oStore = oStore
        self.sName = sName
        self.sPhaseIn = sPhaseIn
        self.sPhaseOut = sPhaseOut
        self.sType = sType
        self.fLimitTothCalculation = fLimitTothCalculation

        self.DesorptionProc = self.oStore.toProcsP2P.get('DesorptionProcessor')

        # Filter geometry and material properties
        self.fVolSolid = getattr(oStore, "tGeometryParameters", {}).get("fVolumeSolid", oStore.toPhases.FilteredPhase.fVolume)
        self.fVolFlow = getattr(oStore, "tGeometryParameters", {}).get("fVolumeFlow", oStore.toPhases.FlowPhase.fVolume)
        self.rVoidFraction = getattr(oStore, "tGeometryParameters", {}).get("rVoidFraction", self.fVolFlow / self.fVolSolid)

        self.fUnivGasConst_R = self.oStore.oMT.Const.fUniversalGas

        self._initialize_filter_properties()

        self.aiPositions = [self.oStore.oMT.tiN2I[key] for key in ['CO2', 'H2O', 'O2', 'N2']]
        self.csNames = [self.oStore.oMT.csSubstances[idx] for idx in self.aiPositions]
        self.iNumSubstances = len(self.csNames)

        self.afMolarMass = [self.oStore.oMT.afMolarMass[idx] for idx in self.aiPositions]

        # Numerical setup
        self.iNumGridPoints = 25
        self.fTimeFactor_1 = 1
        self.fTimeFactor_2 = 1
        self.fDeltaX = None
        self.afDiscreteLength = None
        self._initialize_grid()

        self.arPartials_ads = [0] * self.oStore.oMT.iSubstances
        self.arPartials_des = [0] * self.oStore.oMT.iSubstances

        # Internal state variables
        self.fCurrentSorptionTime = 0
        self.fTimeDifference = 0
        self.fLastExec = 0
        self.mfC_current = None
        self.mfQ_current = None
        self.k_l = None
        self._initialize_concentrations()

    def _initialize_filter_properties(self):
        """
        Initializes filter-specific properties based on the chosen type.
        """
        if self.sType == 'FBA':
            self.fRhoSorbent = 700  # Zeolite density in kg/m^3
            self.fFilterLength = self.oStore.oGeometry.fHeight
            self.ofilter_table = FBA_Table()
        elif self.sType == 'RCA':
            self.fRhoSorbent = 636.7  # SA9-T density in kg/m^3
            self.fFilterLength = self.oStore.fx
            self.ofilter_table = RCA_Table()
        elif self.sType == 'MetOx':
            self.fRhoSorbent = 636.7  # Placeholder value
            self.fFilterLength = self.oStore.fx
            self.ofilter_table = MetOx_Table()
        # Add other filter types as required
        else:
            raise ValueError(f"Unknown filter type: {self.sType}")

    def _initialize_grid(self):
        """
        Initializes the numerical grid for simulation.
        """
        afSpacing = [self.fFilterLength * i / (self.iNumGridPoints - 1) for i in range(self.iNumGridPoints - 1)]
        self.fDeltaX = afSpacing[-1] - afSpacing[-2]
        self.afDiscreteLength = afSpacing + [afSpacing[-1] + self.fDeltaX]

    def _initialize_concentrations(self):
        """
        Initializes concentration and loading variables.
        """
        self.mfC_current = [[0] * self.iNumGridPoints for _ in range(self.iNumSubstances)]
        self.mfQ_current = [[0] * self.iNumGridPoints for _ in range(self.iNumSubstances)]

        mfC_current_flow = [
            (self.oStore.toPhases.FlowPhase.afMass[idx] / self.afMolarMass[i]) / self.oStore.toPhases.FlowPhase.fVolume
            for i, idx in enumerate(self.aiPositions)
        ]
        for i in range(self.iNumGridPoints):
            for j in range(self.iNumSubstances):
                self.mfC_current[j][i] = mfC_current_flow[j]

        mfQ_current_adsorber = [
            (self.oStore.toPhases.FilteredPhase.afMass[idx] / self.afMolarMass[i]) / self.fVolSolid
            for i, idx in enumerate(self.aiPositions)
        ]
        for i in range(self.iNumGridPoints - 1):
            for j in range(self.iNumSubstances):
                self.mfQ_current[j][i] = mfQ_current_adsorber[j]

    def desorption(self, rDesorptionRatio):
        """
        Simplified desorption model to scale concentrations and loadings.
        :param rDesorptionRatio: Ratio of desorption to apply
        """
        for i in range(self.iNumSubstances):
            self.mfC_current[i] = [c * (1 - rDesorptionRatio) for c in self.mfC_current[i]]
            self.mfQ_current[i] = [q * (1 - rDesorptionRatio) for q in self.mfQ_current[i]]

    def update(self):
        """
        Perform the update process for sorption and desorption.
        """
        if self.oStore.oTimer.fTime == self.fLastExec:
            return

        # Update timestep
        self.fElapsedTime = self.oStore.oTimer.fTime - self.fLastExec + self.fTimeDifference

        # TODO: Add main logic for sorption and desorption here.
        pass
