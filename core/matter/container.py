import Sys
from table import Table
from store import Store
from procs.f2f import F2F
import MatterBranch

Sys = Sys()
MatterTable = Table()
MatterStore = Store()
MatterBranch = MatterBranch()
F2FProcessor = F2F()

class Container(Sys):
    """
    Container: A system that contains matter objects.
    Represents a system consisting of multiple stores, branches, etc.
    """

    def __init__(self, oParent, sName):
        """
        Initializes a new matter container class.

        Args:
            oParent (object): Parent system reference.
            sName (str): Name for this system.
        """
        super().__init__(oParent, sName)

        # Properties initialization
        self.toStores = {}
        self.aoBranches = []
        self.toProcsF2F = {}
        self.csStores = []
        self.csProcsF2F = []
        self.toBranches = {}
        self.iBranches = 0
        self.iPhases = 0
        self.bMatterSealed = False
        self.fMaxIdealGasLawPressure = 5e5  # Pa

        # Matter table reference
        if not isinstance(self.oRoot.oMT, MatterTable):
            raise TypeError("Provided object is not an instance of MatterTable.")
        self.oMT = self.oRoot.oMT

        # Solver parameters
        self.tSolverParams = self.oParent.tSolverParams

    def sealMatterStructure(self):
        """
        Seals all stores and branches in this container and calls this method on subsystems.
        """
        if self.bMatterSealed:
            raise RuntimeError("Matter structure already sealed.")

        # Process child systems
        for sChild, child in self.toChildren.items():
            child.sealMatterStructure()
            self.iPhases += child.iPhases
            self.iBranches += len(child.aoBranches)

        # Seal stores
        self.csStores = list(self.toStores.keys())
        self.csProcsF2F = list(self.toProcsF2F.keys())
        for store_name in self.csStores:
            store = self.toStores[store_name]
            store.seal()
            self.iPhases += store.iPhases

        # Seal branches
        for branch in self.aoBranches[:]:
            if branch.abIf[0] and not branch.abIf[1]:
                self.aoBranches.remove(branch)
                del self.toBranches[branch.sName]

        for branch in self.aoBranches:
            if sum(branch.abIf) <= 1:
                branch.seal()

        # Check unused F2F processors
        for proc_name in self.csProcsF2F:
            if not self.toProcsF2F[proc_name].oBranch:
                print(f"Warning: Unused F2F processor '{proc_name}' in system '{self.sName}'.")

        self.bMatterSealed = True

    def createMatterStructure(self):
        """
        Executes the `createMatterStructure` methods of all child systems.
        """
        for sChild, child in self.toChildren.items():
            child.createMatterStructure()

    def addStore(self, oStore):
        """
        Adds the provided store object to the container.

        Args:
            oStore (Store): Store object reference to add.
        """
        if self.bSealed:
            raise RuntimeError("The container is sealed; stores cannot be added.")

        if not isinstance(oStore, MatterStore):
            raise TypeError("Provided object is not a MatterStore.")

        if oStore.sName in self.toStores:
            raise ValueError(f"Store with name {oStore.sName} already exists.")

        if oStore.oMT != self.oMT:
            raise ValueError("Matter tables do not match.")

        self.toStores[oStore.sName] = oStore

    def addProcF2F(self, oProcF2F):
        """
        Adds the provided F2F processor to the container.

        Args:
            oProcF2F (F2FProcessor): F2F processor object reference.
        """
        if self.bSealed:
            raise RuntimeError("The container is sealed; F2F processors cannot be added.")

        if not isinstance(oProcF2F, F2FProcessor):
            raise TypeError("Provided object is not an F2FProcessor.")

        if oProcF2F.sName in self.toProcsF2F:
            raise ValueError(f"Processor {oProcF2F.sName} already exists.")

        self.toProcsF2F[oProcF2F.sName] = oProcF2F

    def addBranch(self, oBranch):
        """
        Adds the provided branch object to the container.

        Args:
            oBranch (Branch): Branch object reference.
        """
        if self.bSealed:
            raise RuntimeError("The container is sealed; branches cannot be added.")

        if not isinstance(oBranch, MatterBranch):
            raise TypeError("Provided branch is not a MatterBranch.")

        if oBranch.sName in self.toBranches:
            raise ValueError(f"Branch with name {oBranch.sName} already exists.")

        self.aoBranches.append(oBranch)
        self.toBranches[oBranch.sName] = oBranch

    def checkMatterSolvers(self):
        """
        Ensures all branches have a solver.
        """
        for child in self.toChildren.values():
            child.checkMatterSolvers()

        for branch in self.aoBranches:
            if not branch.oHandler:
                raise ValueError(f"Branch {branch.sName} in system {self.sName} has no solver.")

    def setMaxIdealGasLawPressure(self, fMaxIdealGasLawPressure):
        """
        Sets the maximum pressure up to which the ideal gas law is used.

        Args:
            fMaxIdealGasLawPressure (float): Maximum pressure in Pa.
        """
        self.fMaxIdealGasLawPressure = fMaxIdealGasLawPressure

    def connectIF(self, sLocalInterface, sParentInterface):
        """
        Connects two interface branches.

        Args:
            sLocalInterface (str): Name of the local interface.
            sParentInterface (str): Name of the parent interface.
        """
        local_branch = next(
            (branch for branch in self.aoBranches if branch.csNames[1] == sLocalInterface), None
        )

        if not local_branch:
            raise ValueError(f"Local interface {sLocalInterface} not found.")

        if not local_branch.abIf[1]:
            raise ValueError("Branch does not have an interface on the right side.")

        local_branch.connectTo(sParentInterface)

        if not local_branch.abIf[0] and local_branch.coExmes[1]:
            self.trigger("branch.connected", local_branch)

    def updateBranchNames(self, oBranch, sOldName):
        """
        Updates branch names in the container.

        Args:
            oBranch (Branch): Branch object.
            sOldName (str): Old name of the branch.
        """
        if oBranch in self.aoBranches:
            if not oBranch.sCustomName:
                if len(sOldName) > 63:  # MATLAB's `namelengthmax`
                    sOldName = sOldName[:63]
                del self.toBranches[sOldName]
                self.toBranches[oBranch.sName] = oBranch
        else:
            raise ValueError("The provided branch does not exist in this container.")
