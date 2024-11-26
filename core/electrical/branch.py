class branch:
    """
    Describes flow path between two terminals.
    """
    def __init__(self, oCircuit, sLeft, csComponents, sRight, sCustomName=None):
        """
        Initialize the branch object.

        Parameters:
        - oCircuit: Reference to the parent electrical circuit.
        - sLeft: Left port as a string or object handle.
        - csComponents: List of component names to include in the branch.
        - sRight: Right port as a string or object handle.
        - sCustomName: Optional custom name for the branch.
        """
        self.oCircuit = oCircuit
        self.coTerminals = [None, None]
        self.aoFlows = []
        self.aoComponents = []
        self.iFlows = 0
        self.iComponents = 0
        self.fResistance = 0
        self.fCurrent = 0
        self.afCurrents = [1] * 10
        self.bOutdated = False
        self.listeners = {}

        # Add branch to circuit
        self.oCircuit.addBranch(self)

        # Create processes (components) and calculate resistance
        self.createProcs(csComponents)
        self.calculateResistance()

    def createProcs(self, csComponents):
        """
        Adds the provided components to the branch.
        """
        for sComponent in csComponents:
            if sComponent not in self.oCircuit.toComponents:
                raise ValueError(f"electrical.branch, Component {sComponent} not found on circuit this branch belongs to!")

            oComponent = self.oCircuit.toComponents[sComponent]

            if self.aoFlows:
                oComponent.addFlow(self.aoFlows[-1])

            oFlow = flow(self)
            self.aoFlows.append(oFlow)
            oComponent.addFlow(oFlow, 'Right')

            self.aoComponents.append(oComponent)

    def setFlows(self, aoFlows):
        """
        Sets the aoFlows property and counts them.
        """
        self.aoFlows = aoFlows
        self.iFlows = len(self.aoFlows)

    def setOutdated(self):
        """
        Marks the branch as outdated for recalculation.
        """
        if not self.bOutdated:
            self.bOutdated = True
            self.trigger('outdated')

    def setCurrent(self, fCurrent):
        """
        Sets current for all flow objects.
        """
        if self.coTerminals[0] is None:
            raise ValueError("setCurrent, Left side is interface, can't set current on this branch object.")

        self.afCurrents = self.afCurrents[1:] + [fCurrent]

        if sum(self.afCurrents) < self.oCircuit.oTimer.iPrecision:
            fCurrent = 0

        self.fCurrent = fCurrent
        self.bOutdated = False

        for oComponent in self.aoComponents:
            oComponent.update()

        self.setFlowData()

    def setTerminal(self, oTerminal, iPosition):
        """
        Setter method to access protected property coTerminals.
        """
        self.coTerminals[iPosition] = oTerminal

    def calculateResistance(self):
        """
        Calculates the overall branch resistance.
        """
        self.fResistance = sum(
            oComponent.fResistance for oComponent in self.aoComponents
            if isinstance(oComponent, resistor)
        )

    def setFlowData(self):
        """
        Sets the current and voltage on all flow objects.
        """
        if self.fCurrent < 0:
            iSign = -1
        else:
            iSign = 1

        for i, oFlow in enumerate(self.aoFlows):
            if i == 0:
                fVoltage = self.coTerminals[0].fVoltage
            elif i > 0 and i < self.iFlows:
                fVoltage -= self.aoComponents[i - 1].fVoltageDrop * iSign
            elif i == self.iFlows - 1:
                fVoltage = self.coTerminals[1].fVoltage

            oFlow.update(self.fCurrent, fVoltage)

    def seal(self):
        """
        Seals this branch so nothing can be changed later on.
        """
        if hasattr(self, 'bSealed') and self.bSealed:
            raise ValueError("Already sealed")

        for oFlow in self.aoFlows:
            oFlow.seal()

        for oComponent in self.aoComponents:
            oComponent.seal()

        self.bSealed = True

    def add_listener(self, event_name, callback):
        """
        Add a listener for a specific event.
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def trigger(self, event_name, *args, **kwargs):
        """
        Trigger an event and notify all listeners.
        """
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(*args, **kwargs)

class flow:
    def __init__(self, oBranch):
        self.oBranch = oBranch
        self.fCurrent = 0
        self.fVoltage = 0

    def update(self, fCurrent, fVoltage):
        self.fCurrent = fCurrent
        self.fVoltage = fVoltage

    def seal(self):
        pass


class resistor:
    def __init__(self, fResistance):
        self.fResistance = fResistance

    def addFlow(self, oFlow, direction=None):
        pass

    def update(self):
        pass

    def seal(self):
        pass


class circuit:
    def __init__(self):
        self.toComponents = {}
        self.branches = []
        self.oTimer = timer()

    def addBranch(self, oBranch):
        self.branches.append(oBranch)


class timer:
    def __init__(self):
        self.iPrecision = 1e-6
