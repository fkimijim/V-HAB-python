from abc import ABC

class container(ABC):
    """
    A system that contains electrical objects.
    Container is the base class of the electrical domain. It
    contains the circuits and provides methods for adding them.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the container class.

        Parameters:
        - oParent: Parent system.
        - sName: Name of the container.
        """
        super().__init__()
        self.oParent = oParent
        self.sName = sName
        self.aoCircuits = []  # Array containing all circuits
        self.toCircuits = {}  # Struct containing all circuits
        self.csCircuits = []  # Names of all circuits in this system
        self.bElectricalSealed = False  # Indicator if this container is sealed

    def createElectricalStructure(self):
        """
        Calls this function on all child objects to define the electrical structure.
        """
        csChildren = list(self.oParent.toChildren.keys())

        for sChild in csChildren:
            self.oParent.toChildren[sChild].createElectricalStructure()

    def addCircuit(self, oCircuit):
        """
        Adds the provided circuit to the container.

        Parameters:
        - oCircuit: The circuit object to be added.
        """
        self.toCircuits[oCircuit.sName] = oCircuit
        self.aoCircuits.append(oCircuit)

    def sealElectricalStructure(self):
        """
        Seals all circuits in this container and calls this method on any subsystems.
        """
        if self.bElectricalSealed:
            raise ValueError("sealElectricalStructure: Already sealed")

        # Seal all child containers
        csChildren = list(self.oParent.toChildren.keys())

        for sChild in csChildren:
            self.oParent.toChildren[sChild].sealElectricalStructure()

        # Get the names of all circuits
        self.csCircuits = list(self.toCircuits.keys())

        # Seal each circuit
        for circuit_name in self.csCircuits:
            self.toCircuits[circuit_name].seal()

        # Mark this container as sealed
        self.bElectricalSealed = True

    def disconnectElectricalBranchesForSaving(self):
        """
        Placeholder to disconnect electrical branches for saving.
        """
        # This method prevents the save process from failing.
        # Needs to be adapted for the electrical domain.
        pass

    def reconnectElectricalBranches(self):
        """
        Placeholder to reconnect electrical branches after loading.
        """
        # This method prevents the load process from failing.
        # Needs to be adapted for the electrical domain.
        pass
