class StationaryDesorption_P2P(matter.procs.p2ps.stationary):
    """
    P2P processor representing the desorption flow.
    Called and set externally in the adsorption P2P processor.
    IMPORTANT: The adsorption P2P must be defined before the desorption
    P2P for correct update order!
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut):
        """
        Constructor for the StationaryDesorption_P2P class.

        :param oStore: Reference to the store this P2P belongs to.
        :param sName: Name of the P2P processor.
        :param sPhaseIn: Name of the input phase.
        :param sPhaseOut: Name of the output phase.
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

    def update(self):
        """
        Placeholder update function.
        """
        pass
