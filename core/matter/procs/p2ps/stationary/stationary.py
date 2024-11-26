import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "p2p")))
from p2p.p2p import P2P

MatterProcsP2P = P2P()

class StationaryP2P(MatterProcsP2P):
    """
    StationaryP2P: A P2P processor where the flow rate does not depend 
    on the mass flows passing through the connected phases or where the 
    phase mass is much larger and the mass flows have only minor impact 
    within one tick. 

    The flow rate is calculated once and remains constant for the rest 
    of the tick.
    """

    # Constant property to indicate that this is a stationary P2P
    bStationary = True

    def __init__(self, oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut):
        """
        Initializes the StationaryP2P class.

        Args:
            oStore (object): The store object where the P2P is located.
            sName (str): Name of the processor.
            sPhaseAndPortIn (str): Input phase and EXME in "phase.exme" notation.
            sPhaseAndPortOut (str): Output phase and EXME in "phase.exme" notation.
        """
        super().__init__(oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut)
