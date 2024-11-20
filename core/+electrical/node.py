class node:
    """
    A class describing a node in an electrical circuit diagram.
    A node can have multiple terminals leading to and from it. Its
    main property is a voltage since it does not represent an actual
    hardware component but rather an intersection of several traces in
    the circuit diagram.
    """

    def __init__(self, oCircuit, sName):
        """
        Constructor for the node class.

        Parameters:
        - oCircuit: Reference to the parent circuit.
        - sName: Identifier for the node object.
        """
        self.oCircuit = oCircuit  # Reference to the circuit object
        self.sName = sName  # Node identifier
        self.aoTerminals = []  # Array of terminals
        self.toTerminals = {}  # Dictionary of terminals
        self.iTerminals = 0  # Number of terminals
        self.fVoltage = 0  # Voltage at the node
        self.bSealed = False  # Sealed state of the node

        # Adding this node to the circuit
        self.oCircuit.addNode(self)

    def addTerminal(self, oTerminal):
        """
        Adds a terminal to this node.

        Parameters:
        - oTerminal: Terminal object to add.
        """
        self.aoTerminals.append(oTerminal)
        self.toTerminals[oTerminal.sName] = oTerminal

    def seal(self):
        """
        Seals the node to prevent further changes.
        """
        self.iTerminals = len(self.aoTerminals)
        self.bSealed = True

    def getTerminal(self, sTerminalName):
        """
        Returns a reference to a specific terminal of the node.

        Parameters:
        - sTerminalName: Name of the terminal to retrieve.

        Returns:
        - oTerminal: The terminal object with the given name.

        Raises:
        - KeyError: If the terminal name does not exist.
        """
        if sTerminalName not in self.toTerminals:
            raise KeyError(f"There is no terminal '{sTerminalName}' on node {self.sName}.")
        return self.toTerminals[sTerminalName]

    def createTerminals(self, iNumberOfTerminals):
        """
        Helper function to create multiple terminals at once.

        Parameters:
        - iNumberOfTerminals: Number of terminals to create.
        """
        for _ in range(iNumberOfTerminals):
            terminal(self)  # Create a new terminal and associate it with this node

    def setVoltage(self, fVoltage):
        """
        Sets the voltage of the node and updates its terminals.

        Parameters:
        - fVoltage: Voltage to set.
        """
        self.fVoltage = fVoltage
        for oTerminal in self.aoTerminals:
            oTerminal.setVoltage(self.fVoltage)


# Supporting Terminal Class
class terminal:
    """
    A class representing a terminal in an electrical node.
    """

    def __init__(self, oNode, sName=None):
        """
        Constructor for the terminal class.

        Parameters:
        - oNode: Parent node to which the terminal belongs.
        - sName: Optional name for the terminal.
        """
        self.oNode = oNode
        self.sName = sName if sName else f"Terminal_{len(oNode.aoTerminals) + 1}"
        self.fVoltage = 0  # Voltage at the terminal

        # Add this terminal to the parent node
        self.oNode.addTerminal(self)

    def setVoltage(self, fVoltage):
        """
        Sets the voltage at the terminal.

        Parameters:
        - fVoltage: Voltage to set.
        """
        self.fVoltage = fVoltage
