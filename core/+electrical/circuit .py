import store
import node
import branch
import component
import stores.constantVoltageSource as constantVoltageSource

class circuit:
    """
    Defines an electrical circuit.
    The model of an electrical circuit consists of stores, components,
    branches, and nodes. These are all child objects of instances of this class.
    """

    def __init__(self, oParent, sName):
        """
        Initializes the circuit object.

        Parameters:
        - oParent: Reference to the parent electrical system.
        - sName: Name of this circuit.
        """
        self.oSource = None  # Reference to a voltage or current source
        self.oParent = oParent  # Reference to the parent electrical system
        self.sName = sName  # Name of the circuit

        self.aoStores = []  # Array of all electrical.store objects
        self.toStores = {}  # Struct of all electrical.store objects
        self.iStores = 0  # Number of stores

        self.aoNodes = []  # Array of all node objects
        self.toNodes = {}  # Struct of all node objects
        self.iNodes = 0  # Number of nodes

        self.aoComponents = []  # Array of all components
        self.toComponents = {}  # Struct of all components

        self.aoBranches = []  # Array of all branches
        self.toBranches = {}  # Struct of all branches
        self.iBranches = 0  # Number of branches

        self.bSealed = False  # Indicator if this circuit is sealed
        self.oTimer = self.oParent.oRoot.oTimer  # Reference to the timer object

        # Add this circuit to the parent object
        self.oParent.addCircuit(self)

    def addStore(self, oStore):
        """
        Adds the provided store to the circuit.
        """
        if self.bSealed:
            raise ValueError("addStore, The container is sealed, so no stores can be added.")

        if not isinstance(oStore, store):
            raise ValueError("addStore, Provided object is not an electrical.store!")

        if oStore.sName in self.toStores:
            raise ValueError(f"addStore, Store with name {oStore.sName} already exists!")

        if isinstance(oStore, constantVoltageSource):
            if self.oSource is None:
                self.oSource = oStore
            else:
                raise ValueError(f"addStore, This circuit ({self.sName}) already has a source.")

        self.toStores[oStore.sName] = oStore
        self.aoStores.append(oStore)
        self.iStores = len(self.aoStores)

    def addNode(self, oNode):
        """
        Adds the provided node to the circuit.
        """
        if self.bSealed:
            raise ValueError("The container is sealed, so no nodes can be added.")

        if not isinstance(oNode, node):
            raise ValueError("addNode, Provided object is not an electrical.node!")

        if oNode.sName in self.toNodes:
            raise ValueError(f"addNode, Node with name {oNode.sName} already exists!")

        self.toNodes[oNode.sName] = oNode
        self.aoNodes.append(oNode)
        self.iNodes = len(self.aoNodes)

    def addBranch(self, oBranch):
        """
        Adds the provided branch to the circuit.
        """
        if self.bSealed:
            raise ValueError("Can't create branches anymore, sealed.")

        if not isinstance(oBranch, branch):
            raise ValueError("Provided branch is not an electrical.branch!")

        if oBranch.sName in self.toBranches:
            raise ValueError(f"Branch with name {oBranch.sName} already exists!")

        self.aoBranches.append(oBranch)
        if oBranch.sCustomName:
            if oBranch.sCustomName in self.toBranches:
                raise ValueError("A branch with this custom name already exists.")
            self.toBranches[oBranch.sCustomName] = oBranch
        else:
            self.toBranches[oBranch.sName] = oBranch

        self.iBranches = len(self.aoBranches)

    def addComponent(self, oComponent):
        """
        Adds the provided component to the circuit.
        """
        if self.bSealed:
            raise ValueError("The circuit is sealed, so no components can be added.")

        if not isinstance(oComponent, component):
            raise ValueError("Provided object is not an electrical.component!")

        if oComponent.sName in self.toComponents:
            raise ValueError(f"Component with name {oComponent.sName} already exists!")

        self.toComponents[oComponent.sName] = oComponent
        self.aoComponents.append(oComponent)

    def seal(self):
        """
        Seals this circuit so nothing can be changed later on.
        """
        for oNode in self.aoNodes:
            oNode.seal()

        for oStore in self.aoStores:
            oStore.seal()

        for oBranch in self.aoBranches:
            oBranch.seal()

        self.bSealed = True

    def update(self, afValues):
        """
        Sets voltages in nodes and currents in branches.

        Parameters:
        - afValues: List containing the voltages for all nodes followed by
                    the currents for all branches.
        """
        for i, oNode in enumerate(self.aoNodes):
            oNode.setVoltage(afValues[i])

        for i, oBranch in enumerate(self.aoBranches):
            oBranch.setCurrent(afValues[i + self.iNodes])
