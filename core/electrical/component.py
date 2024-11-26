from abc import ABC, abstractmethod
import flow

class Component(ABC):
    """
    Describes an electrical component.
    This abstract class is the foundation for all electrical components
    (e.g., resistors, capacitors) in the system. Assumes derived
    components will have only two ports. If more ports are needed,
    the `addFlow()` method must be overridden.
    """

    def __init__(self, oCircuit, sName):
        """
        Initializes the component.

        Parameters:
        - oCircuit: Reference to the parent circuit.
        - sName: Name of the component.
        """
        self.sName = sName  # Name of the component
        self.oCircuit = oCircuit  # Reference to the parent circuit
        self.toPorts = {}  # A dictionary containing references to all ports
        self.abPorts = [False, False]  # Indicator for left and right port usage
        self.aoFlows = []  # Array of all flows associated with this component
        self.oTimer = oCircuit.oTimer  # Reference to the timer object
        self.oBranch = None  # Reference to a branch object this component is contained in
        self.bSealed = False  # Indicator if this component is sealed

        # Adding this component to the parent circuit
        self.oCircuit.addComponent(self)

    def addFlow(self, oFlow, sPort=None):
        """
        Adds a flow to the component. Automatically assigns to left or right port.

        Parameters:
        - oFlow: The flow object to be added.
        - sPort: Optional port name ('Left' or 'Right').
        """
        if not isinstance(oFlow, flow):
            raise ValueError("The provided flow object must derive from electrical.flow!")

        if oFlow in self.aoFlows:
            raise ValueError("The provided flow object is already registered!")

        # Find the first unused port
        if sPort is None:
            iIdx = next((i for i, used in enumerate(self.abPorts) if not used), None)
        else:
            iIdx = 0

        if iIdx is None:
            raise ValueError(
                f"The component '{self.sName}' is already in use by another branch. "
                f"Check the definition of branch: {oFlow.oBranch.sName}"
            )

        # Assign the flow to the appropriate port
        if iIdx == 0 and sPort:
            if sPort not in ['Left', 'Right']:
                raise ValueError(
                    f"The port name '{sPort}' is illegal. Must be 'Left' or 'Right'."
                )
            self.toPorts[sPort] = oFlow
            iIdx = 1 if sPort == 'Left' else 2
        elif iIdx == 0:
            raise ValueError("No available ports for the flow.")
        elif iIdx == 1:
            self.toPorts['Left'] = oFlow
        elif iIdx == 2:
            self.toPorts['Right'] = oFlow

        # Mark the port as used and associate the flow
        self.abPorts[iIdx - 1] = True
        if len(self.aoFlows) < iIdx:
            self.aoFlows.extend([None] * (iIdx - len(self.aoFlows)))
        self.aoFlows[iIdx - 1] = oFlow

        # Register the component with the flow
        oFlow.addComponent(self, lambda: self._removeFlow(oFlow))

    def _removeFlow(self, oFlow):
        """
        Removes the provided flow object from this component.
        This is a private method, accessible only via the anonymous handle.

        Parameters:
        - oFlow: The flow object to be removed.
        """
        if oFlow not in self.aoFlows:
            raise ValueError(
                f"The provided flow object is not connected to {self.sName}"
            )

        # Remove the flow object reference
        self.aoFlows.remove(oFlow)

    @abstractmethod
    def update(self):
        """
        Abstract method to be implemented by child classes.
        """
        pass
