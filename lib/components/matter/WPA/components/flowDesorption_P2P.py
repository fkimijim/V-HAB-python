class FlowDesorptionP2P:
    """
    P2P processor representing the desorption flow.
    Called and set externally in the adsorption P2P processor.
    IMPORTANT: The adsorption P2P must be defined before the desorption
    P2P for correct update order!
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut):
        """
        Constructor for the FlowDesorptionP2P class.
        
        :param oStore: Store to which the processor belongs
        :param sName: Name of the processor
        :param sPhaseIn: Input phase
        :param sPhaseOut: Output phase
        """
        self.oStore = oStore
        self.sName = sName
        self.sPhaseIn = sPhaseIn
        self.sPhaseOut = sPhaseOut

    def calculateFlowRate(self, *args, **kwargs):
        """
        Placeholder for calculating the flow rate.
        This method is intentionally left empty and should be overridden as needed.
        """
        pass

    def update(self):
        """
        Placeholder for the update method.
        This method is intentionally left empty and should be overridden as needed.
        """
        pass
