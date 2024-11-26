import Component

component = Component()

class flow:
    """
    A class defining an electrical flow.
    An electrical flow is characterized by its voltage and current.
    """

    def __init__(self, oBranch):
        """
        Constructor for the flow class.

        Parameters:
        - oBranch: Reference to the branch the flow belongs to.
        """
        self.fCurrent = 0  # Electrical current in [A]
        self.fVoltage = 0  # Voltage in [V]
        self.oTimer = oBranch.oTimer  # Reference to the timer
        self.oBranch = oBranch  # Reference to the branch
        self.oIn = None  # Reference to the object connected on the 'right'
        self.oOut = None  # Reference to the object connected on the 'left'
        self.thRemoveCBs = {"in": None, "out": None}  # Callbacks to remove the flow
        self.bSealed = False  # Indicator if this flow is sealed
        self.bInterface = False  # Interface flow indicator

    def update(self, fCurrent, fVoltage):
        """
        Updates the voltage and current properties.

        Parameters:
        - fCurrent: Current value to update.
        - fVoltage: Voltage value to update.
        """
        self.fCurrent = fCurrent
        self.fVoltage = fVoltage

    def seal(self, bIf=False, oBranch=None):
        """
        Seals the flow to prevent changes.

        Parameters:
        - bIf: Boolean indicating if this is an interface flow.
        - oBranch: Reference to the branch object.

        Returns:
        - Function handle for removing the flow from the attached component.
        """
        if self.bSealed:
            raise ValueError("seal: Already sealed!")

        hRemoveIfComponent = None
        self.bSealed = True

        if self.oIn and not self.oOut and bIf:
            self.bInterface = True
            hRemoveIfComponent = self.removeInterfaceComponent

        if oBranch is not None:
            self.oBranch = oBranch

        return hRemoveIfComponent

    def remove(self):
        """
        Removes references to the connected components.
        """
        if self.oIn and self.thRemoveCBs["in"]:
            self.thRemoveCBs["in"]()
        if self.oOut and self.thRemoveCBs["out"]:
            self.thRemoveCBs["out"]()

        self.oIn = None
        self.oOut = None

    def addComponent(self, oComponent, removeCallBack):
        """
        Adds the provided component.

        Parameters:
        - oComponent: The component to add.
        - removeCallBack: Callback to remove the component.
        """
        if not isinstance(oComponent, component):
            raise ValueError("addComponent: Provided component must derive from electrical.component!")

        if not any(flow is self for flow in oComponent.aoFlows):
            raise ValueError("addComponent: Use the component's addFlow method to add this flow.")

        if self.bSealed and (not self.bInterface or not self.oIn):
            raise ValueError("addComponent: Can't create branches anymore, sealed.")

        if not self.oIn:
            self.oIn = oComponent
            self.thRemoveCBs["in"] = removeCallBack
        elif not self.oOut:
            self.oOut = oComponent
            self.thRemoveCBs["out"] = removeCallBack
        else:
            raise ValueError("addComponent: Both oIn and oOut are already set.")

    def removeInterfaceComponent(self):
        """
        Decouples flow from the component if it's an interface flow.
        """
        if not self.bInterface:
            raise ValueError("removeInterfaceComponent: Can only be done for interface flows.")

        if not self.oOut:
            raise ValueError("removeInterfaceComponent: Not connected.")

        # Execute the remove callback
        if self.thRemoveCBs["out"]:
            self.thRemoveCBs["out"]()

        # Remove the callback and the reference
        self.thRemoveCBs["out"] = None
        self.oOut = None
