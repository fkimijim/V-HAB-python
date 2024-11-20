import node
import flow

class terminal:
    """
    An electrical port that can be connected to stores.
    This class connects stores and nodes to flows.
    """

    def __init__(self, oParent, sName=None):
        """
        Constructor for the terminal class.

        Parameters:
        - oParent: Reference to the terminal's parent object.
        - sName: Name identifying this terminal (optional).
        """
        self.oParent = oParent  # Reference to the parent object
        self.iSign = 0  # Direction of flow through the terminal
        self.oFlow = None  # Reference to the connected flow
        self.sName = sName  # Name of the terminal
        self.bHasFlow = False  # Indicates if the terminal has an assigned flow
        self.fVoltage = 0  # Voltage at the terminal

        # Automatically add the terminal to its parent if the parent is a node
        if isinstance(oParent, node):
            if not self.sName:
                # Generate a default name if none is provided
                self.sName = f"Terminal_{len(oParent.aoTerminals) + 1}"

            # Add the terminal to the parent node
            self.oParent.addTerminal(self)

    def addFlow(self, oFlow):
        """
        Assigns a flow object to this terminal.

        Parameters:
        - oFlow: The flow object to be assigned.

        Raises:
        - ValueError: If the terminal's parent is sealed, already has a flow,
            or the provided object is not an electrical flow.
        """
        # Check if the parent is sealed
        if self.oParent.bSealed:
            raise ValueError(
                "The parent of this terminal is sealed, so no flows can be added anymore."
            )

        # Check if there is already a flow assigned
        if self.oFlow is not None:
            raise ValueError(
                f"There is already a flow connected to this terminal! ({self.oParent.sName}.{self.sName}) You have to create another one."
            )

        # Check if the provided object is of the correct type
        if not isinstance(oFlow, flow):
            raise ValueError("The provided flow object is not an electrical.flow!")

        # Assign the flow to this terminal
        self.oFlow = oFlow
        self.bHasFlow = True

    def setVoltage(self, fVoltage):
        """
        Sets the voltage property.

        Parameters:
        - fVoltage: Voltage to be set.
        """
        self.fVoltage = fVoltage
