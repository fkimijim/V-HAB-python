class Example(vsys):
    """
    EXAMPLE
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName)

        eval(self.oRoot.oCfgParams.configCode(self))

        # Create the electrical circuit within the system
        electrical.circuit(self, "ExampleCircuit")

    def createElectricalStructure(self):
        super().createElectricalStructure()

        # Create circuit reference to simplify code
        oCircuit = self.toCircuits.ExampleCircuit

        # Create source
        oVoltageSource = electrical.stores.constantVoltageSource(oCircuit, "VoltageSource", "DC", 6)
        oVoltageSource.setFixedTimeStep(1)

        # Create resistors
        electrical.components.resistor(oCircuit, "Resistor1", 7.5)
        electrical.components.resistor(oCircuit, "Resistor2", 30)
        electrical.components.resistor(oCircuit, "Resistor3", 3)
        electrical.components.resistor(oCircuit, "Resistor4", 3.75)
        electrical.components.resistor(oCircuit, "Resistor5", 15)
        electrical.components.resistor(oCircuit, "Resistor6", 3)

        # Create five nodes
        oNode1 = electrical.node(oCircuit, "Node_1")
        oNode2 = electrical.node(oCircuit, "Node_2")
        oNode3 = electrical.node(oCircuit, "Node_3")
        oNode4 = electrical.node(oCircuit, "Node_4")
        oNode5 = electrical.node(oCircuit, "Node_5")

        # Create terminals for nodes
        oNode1.createTerminals(4)
        oNode2.createTerminals(3)
        oNode3.createTerminals(3)
        oNode4.createTerminals(3)
        oNode5.createTerminals(3)

        # Create electrical branches
        electrical.branch(oCircuit, "Node_1.Terminal_4",      ["Resistor1"], "Node_5.Terminal_1")
        electrical.branch(oCircuit, "Node_1.Terminal_2",      ["Resistor2"], "Node_3.Terminal_1")
        electrical.branch(oCircuit, "Node_1.Terminal_3",      ["Resistor3"], "Node_2.Terminal_1")
        electrical.branch(oCircuit, "Node_2.Terminal_2",      ["Resistor4"], "Node_4.Terminal_1")
        electrical.branch(oCircuit, "Node_2.Terminal_3",      ["Resistor5"], "Node_3.Terminal_2")
        electrical.branch(oCircuit, "VoltageSource.positive", ["Resistor6"], "Node_1.Terminal_1")
        electrical.branch(oCircuit, "Node_3.Terminal_3",      [],            "Node_4.Terminal_2")
        electrical.branch(oCircuit, "Node_4.Terminal_3",      [],            "Node_5.Terminal_2")
        electrical.branch(oCircuit, "Node_5.Terminal_3",      [],            "VoltageSource.negative")

    def createSolverStructure(self):
        super().createSolverStructure()

        # Add the DC solver for the circuit
        solver.electrical.DC.circuit(self.toCircuits.ExampleCircuit)

    def exec(self, *args):
        """
        Execute function for this system
        """
        super().exec(*args)
