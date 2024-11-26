import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sys")))
import Sys
from thermal.branch import Branch
from thermal.procs.conductor import Conductor

Sys = Sys()

class Container(Sys):
    """
    A collection of thermal capacities.
    Container is the base class of the thermal domain and contains capacities and branches.
    """

    def __init__(self, oParent, sName):
        """
        Initialize the Container object.
        
        Args:
            oParent: The parent system of the container.
            sName: The name of the container.
        """
        super().__init__(oParent, sName)
        self.aoThermalBranches = []  # List of thermal branches
        self.toProcsConductor = {}  # Dictionary of conductors
        self.csConductors = []  # Cached conductor names
        self.coCapacities = []  # List of capacities
        self.toThermalBranches = {}  # Dictionary of thermal branches
        self.iThermalBranches = 0  # Total number of thermal branches
        self.iCapacities = 0  # Total number of capacities
        self.bThermalSealed = False  # Seal status

    def createThermalStructure(self):
        """
        Define the thermal system by calling this method on all child objects.
        """
        # Call the method on child objects
        for sChild in self.toChildren:
            self.toChildren[sChild].createThermalStructure()
        
        # Create thermal capacities and branches
        self.createMatterCounterParts()
        self.trigger('createdThermalStructure')

    def addProcConductor(self, oConductor):
        """
        Add a conductor to the system.

        Args:
            oConductor: The conductor to add.
        """
        if self.bThermalSealed:
            raise Exception("The container is sealed, so no conductors can be added.")

        if not isinstance(oConductor, Conductor):
            raise Exception("Provided object is not a thermal.procs.conductor.")

        if oConductor.sName in self.toProcsConductor:
            raise Exception(f"Conductor {oConductor.sName} already exists.")

        if self != oConductor.oContainer:
            raise Exception("Conductor does not have this system set as a container!")

        self.toProcsConductor[oConductor.sName] = oConductor

    def addThermalBranch(self, oThermalBranch):
        """
        Add a thermal branch to the system.

        Args:
            oThermalBranch: The thermal branch to add.
        """
        if self.bThermalSealed:
            raise Exception("The container is sealed, so no branches can be added.")

        if not isinstance(oThermalBranch, Branch):
            raise Exception("Provided branch is not a thermal.branch.")

        if oThermalBranch.sName in self.toThermalBranches:
            raise Exception(f"Branch with name {oThermalBranch.sName} already exists.")

        self.aoThermalBranches.append(oThermalBranch)
        branch_name = oThermalBranch.sCustomName or oThermalBranch.sName
        self.toThermalBranches[branch_name] = oThermalBranch

    def sealThermalStructure(self):
        """
        Seal the thermal structure and delete unneeded branch stubs.
        """
        if self.bThermalSealed:
            raise Exception("Thermal structure is already sealed.")

        for sChild in self.toChildren:
            child = self.toChildren[sChild]
            child.sealThermalStructure()
            self.iThermalBranches += len(child.aoThermalBranches)

        self.csConductors = list(self.toProcsConductor.keys())

        # Remove branch stubs
        if self.aoThermalBranches:
            for branch in self.aoThermalBranches:
                if sum(branch.abIf) <= 1:
                    branch.seal()

        self.iThermalBranches = len(self.aoThermalBranches)
        self.bThermalSealed = True
        self.trigger('ThermalSeal_post')

    def setThermalSolvers(self):
        """
        Add solvers to branches without a handler.
        """
        for branch in self.aoThermalBranches:
            if not branch.oHandler:
                if branch.coConductors and isinstance(branch.coConductors[0], Conductor):
                    branch.setSolver()
                else:
                    branch.setInfiniteSolver()

    def createMatterCounterParts(self):
        """
        Create capacities and thermal branches for the matter domain.
        """
        for sStore, store in self.toStores.items():
            for phase in store.aoPhases:
                if phase.isBoundary:
                    self.addBoundaryCapacity(phase)
                elif phase.isFlow:
                    self.addFlowCapacity(phase)
                else:
                    self.addStandardCapacity(phase)

                phase.oCapacity.updateSpecificHeatCapacity()

            for processor in store.toProcsP2P.values():
                self.createThermalBranchFromProcessor(processor)

    def addCapacity(self, oCapacity):
        """
        Add a capacity to the container.

        Args:
            oCapacity: The capacity to add.
        """
        self.coCapacities.append(oCapacity)
        self.iCapacities += 1

    def createThermalBranchFromProcessor(self, processor):
        """
        Create a thermal branch for a given processor.

        Args:
            processor: The processor to use for the branch.
        """
        # Create thermal exmes for the processor
        exme_in = processor.coExmes[0]
        exme_out = processor.coExmes[1]

        self.addProcConductor(Conductor(self, processor.sName, processor))

        branch = Branch(
            self,
            exme_in.oPhase.oCapacity,
            [processor.sName],
            exme_out.oPhase.oCapacity,
            processor.sName,
            processor
        )
        processor.setThermalBranch(branch)
