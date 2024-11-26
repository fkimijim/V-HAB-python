import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "procs")))
from p2p.stationary import StationaryP2P

StationaryP2P = StationaryP2P()

class Store:
    """
    Store class in a system containing one or more phases.
    Manages phases, processes, and their properties within a store.
    """

    def __init__(self, oContainer, sName, fVolume, tGeometryParams=None):
        """
        Initialize the Store object.

        Parameters:
        oContainer (Container): Parent container for the store.
        sName (str): Name of the store.
        fVolume (float): Total volume of the store.
        tGeometryParams (dict): Optional geometry parameters for the store.
        """
        self.aoPhases = []  # List of phases in the store
        self.toPhases = {}  # Dictionary mapping phase names to phase objects
        self.iPhases = 0  # Number of phases, updated when sealing
        self.toProcsP2P = {}  # Dictionary of P2P processors
        self.csProcsP2P = []  # List of P2P processor names
        self.aiProcsP2Pstationary = []  # List of indices of stationary P2Ps
        self.sName = sName
        self.bSealed = False  # Seal state of the store
        self.oContainer = oContainer
        self.oContainer.add_store(self)  # Add store to container
        self.oMT = oContainer.oRoot.oMT
        self.oTimer = oContainer.oRoot.oTimer
        self.csExMeNames = []  # List of ExMe processor names
        self.tGeometryParameters = tGeometryParams or {'Shape': 'Box', 'Area': 1}

        if fVolume <= 0:
            raise ValueError(f"The store '{sName}' cannot have a volume of zero or less.")
        self.fVolume = fVolume

    def get_exme(self, sExMe):
        """
        Get the ExMe processor by name.

        Parameters:
        sExMe (str): Name of the ExMe processor.

        Returns:
        ExMe: Corresponding ExMe object.
        """
        for phase in self.aoPhases:
            if sExMe in phase.toProcsEXME:
                return phase.toProcsEXME[sExMe]

        raise ValueError(f"ExMe '{sExMe}' could not be found.")

    def add_exme_name(self, sName):
        """
        Add an ExMe name to the store, ensuring uniqueness.

        Parameters:
        sName (str): Name of the ExMe processor.
        """
        self.csExMeNames.append(sName)

    def get_thermal_exme(self, sExMe):
        """
        Get a thermal ExMe processor by name.

        Parameters:
        sExMe (str): Name of the thermal ExMe processor.

        Returns:
        ExMe: Corresponding thermal ExMe object.
        """
        for phase in self.aoPhases:
            if sExMe in phase.oCapacity.toProcsEXME:
                return phase.oCapacity.toProcsEXME[sExMe]

        raise ValueError(f"Thermal ExMe '{sExMe}' could not be found.")

    def add_phase(self, oPhase):
        """
        Add a phase to the store.

        Parameters:
        oPhase (Phase): Phase object to add.
        """
        if self.bSealed:
            raise ValueError("The store is sealed, so no phases can be added.")
        if oPhase.sName in self.toPhases:
            raise ValueError("A phase with this name already exists.")
        if oPhase.oStore and oPhase.oStore != self:
            raise ValueError("The phase already belongs to a different store.")

        self.aoPhases.append(oPhase)
        self.toPhases[oPhase.sName] = oPhase

    def create_phase(self, sHelper, *args):
        """
        Create and add a phase using a helper.

        Parameters:
        sHelper (str): Name of the helper to create the phase.
        *args: Arguments for the helper.

        Returns:
        Phase: Created phase object.
        """
        if self.bSealed:
            raise ValueError("The store is sealed, so no phases can be created.")

        bFlowNode = args and args[0] == 'flow'
        bBoundaryNode = args and args[0] == 'boundary'
        cInputs = args[1:] if (bFlowNode or bBoundaryNode) else args

        cParams, sDefaultPhase = self._create_phase_params(sHelper, *cInputs)

        if bFlowNode:
            sDefaultPhase = sDefaultPhase.replace('phases.', 'phases.flow.')
        elif bBoundaryNode:
            sDefaultPhase = sDefaultPhase.replace('phases.', 'phases.boundary.')

        oPhase = eval(sDefaultPhase)(*cParams)
        self.add_phase(oPhase)
        return oPhase

    def seal(self):
        """
        Seal the store, preventing further modifications.
        """
        if self.bSealed:
            return

        self.iPhases = len(self.aoPhases)
        self.csProcsP2P = list(self.toProcsP2P.keys())

        for i, proc_name in enumerate(self.csProcsP2P):
            if isinstance(self.toProcsP2P[proc_name], StationaryP2P):
                self.aiProcsP2Pstationary.append(i)

        fPhaseVolume = sum(phase.fVolume for phase in self.aoPhases if not phase.bBoundary)
        if round(self.fVolume - fPhaseVolume, self.oTimer.iPrecision) < 0:
            raise ValueError(f"The total volume of phases exceeds the store's volume by {fPhaseVolume - self.fVolume} m^3.")

        for phase in self.aoPhases:
            phase.seal()

        self.bSealed = True

    def add_p2p(self, oProcP2P):
        """
        Add a P2P processor to the store.

        Parameters:
        oProcP2P (P2P): P2P processor object.
        """
        if self.bSealed:
            raise ValueError(f"Cannot add P2P '{oProcP2P.sName}' to sealed store '{self.sName}'.")
        if oProcP2P.sName in self.toProcsP2P:
            raise ValueError(f"P2P '{oProcP2P.sName}' already exists in the store.")
        if oProcP2P.oStore != self:
            raise ValueError(f"P2P '{oProcP2P.sName}' does not belong to this store.")

        self.toProcsP2P[oProcP2P.sName] = oProcP2P

    def add_standard_volume_manipulators(self):
        """
        Add standard volume manipulators to the phases.
        """
        for phase in self.aoPhases:
            if phase.sType == 'gas':
                oCompressibleManip = CompressibleMediumManipulator(phase.sName + '_CompressibleManip', phase)
            else:
                IncompressibleMediumManipulator(phase.sName + '_IncompressibleManip', phase, oCompressibleManip)

    def set_volume(self, fVolume):
        """
        Set the store's volume and update phases.

        Parameters:
        fVolume (float): New volume of the store.
        """
        self.fVolume = fVolume
        for phase in self.aoPhases:
            if hasattr(phase.toManips.volume, 'bCompressible'):
                phase.toManips.volume.register_update()
                phase.register_update()
            else:
                raise ValueError(f"Phases in store '{self.sName}' lack required volume manipulators.")

    def _create_phase_params(self, sHelper, *args):
        """
        Helper method for creating phase parameters.

        Parameters:
        sHelper (str): Name of the helper.
        *args: Additional arguments for the helper.

        Returns:
        tuple: Parameters for the phase and its class path.
        """
        if args and isinstance(args[0], str):
            sPhaseName = args[0]
            cPhaseParams = args[1:]
        else:
            sPhaseName = f"{self.sName}_Phase_{len(self.aoPhases) + 1}"
            cPhaseParams = args

        cParams, sDefaultPhase = HelperPhaseCreate.create(sHelper, self, *cPhaseParams)
        cParams.insert(0, self)
        cParams.insert(1, sPhaseName)

        return cParams, sDefaultPhase
